#!/usr/bin/env python3
"""Generate organigrama.html from organigrama.yaml.

Usage: python3 build.py
"""
import html
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).parent
YAML_PATH = ROOT / 'organigrama.yaml'
HTML_PATH = ROOT / 'organigrama.html'

ROLE_LABELS = [('tl', 'Team Lead'), ('pm', 'PM'), ('ux', 'UX'), ('po', 'PO'), ('qa', 'QA')]


def esc(s):
    return html.escape(str(s)) if s else ''


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def initials(name):
    parts = [p for p in re.split(r'\s+', name) if p]
    if not parts:
        return '?'
    if len(parts) == 1:
        return parts[0][:2].upper()
    return (parts[0][0] + parts[-1][0]).upper()


def render_microteam(mt):
    name = mt['name']
    roles_html = []
    for key, label in ROLE_LABELS:
        val = mt.get(key)
        if not val:
            continue
        roles_html.append(
            f'<div class="role"><span class="role-label">{esc(label)}</span>'
            f'<span class="role-value"><span class="avatar">{esc(initials(val))}</span>{esc(val)}</span></div>'
        )
    members = mt.get('members') or []
    members_html = ''
    if members:
        chips = ''.join(
            f'<span class="member-chip"><span class="avatar small">{esc(initials(m))}</span>{esc(m)}</span>'
            for m in members
        )
        members_html = (
            f'<div class="members"><div class="members-label">Members ({len(members)})</div>'
            f'<div class="members-list">{chips}</div></div>'
        )
    tl = mt.get('tl') or ''
    return (
        f'<article class="microteam" data-name="{esc(name.lower())}" '
        f'data-tl="{esc(tl.lower())}" '
        f'data-members="{esc(" ".join(members).lower())}">'
        f'<header class="mt-header"><h4>{esc(name)}</h4></header>'
        f'<div class="roles">{"".join(roles_html)}</div>'
        f'{members_html}'
        f'</article>'
    )


def render_area(area):
    name = area['name']
    mts = area.get('microteams') or []
    mt_html = ''.join(render_microteam(mt) for mt in mts)
    plural = 's' if len(mts) != 1 else ''
    return (
        f'<section class="area" data-area="{esc(name.lower())}">'
        f'<header class="area-header"><h3>{esc(name)}</h3>'
        f'<span class="count">{len(mts)} microteam{plural}</span></header>'
        f'<div class="microteams">{mt_html}</div>'
        f'</section>'
    )


def render_domain(domain):
    name = domain['name']
    areas = domain.get('areas') or []
    a_html = ''.join(render_area(a) for a in areas)
    n_mt = sum(len(a.get('microteams') or []) for a in areas)
    return (
        f'<section class="domain" id="domain-{slug(name)}" data-domain="{esc(name.lower())}">'
        f'<header class="domain-header" data-toggle>'
        f'<h2><span class="chevron">&#9662;</span> {esc(name)}</h2>'
        f'<span class="domain-stats">{len(areas)} areas &middot; {n_mt} microteams</span>'
        f'</header>'
        f'<div class="domain-body">{a_html}</div>'
        f'</section>'
    )


CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  background: #f6f7f9;
  color: #1f2937;
  line-height: 1.45;
}
.page { max-width: 1400px; margin: 0 auto; padding: 24px; }
header.top {
  display: flex; flex-wrap: wrap; gap: 16px; align-items: flex-end;
  justify-content: space-between; margin-bottom: 24px;
  padding-bottom: 16px; border-bottom: 1px solid #e5e7eb;
}
header.top h1 { margin: 0 0 4px 0; font-size: 28px; letter-spacing: -0.02em; }
header.top .subtitle { color: #6b7280; font-size: 14px; }
.stats { display: flex; gap: 18px; flex-wrap: wrap; }
.stat { background: #fff; border: 1px solid #e5e7eb; border-radius: 8px; padding: 8px 14px; }
.stat .num { font-weight: 700; font-size: 18px; color: #111827; }
.stat .lbl { font-size: 12px; color: #6b7280; text-transform: uppercase; letter-spacing: .04em; }
.controls { display: flex; gap: 12px; align-items: center; margin-bottom: 24px; flex-wrap: wrap; }
.search {
  flex: 1; min-width: 260px;
  display: flex; align-items: center;
  background: #fff; border: 1px solid #d1d5db; border-radius: 8px;
  padding: 8px 12px;
}
.search input { flex: 1; border: 0; outline: 0; font-size: 14px; background: transparent; }
.search svg { margin-right: 8px; color: #9ca3af; flex-shrink: 0; }
.btn {
  background: #fff; border: 1px solid #d1d5db; padding: 8px 14px;
  border-radius: 8px; cursor: pointer; font-size: 14px; color: #374151;
}
.btn:hover { background: #f3f4f6; }
.domain {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 12px;
  margin-bottom: 24px; overflow: hidden;
}
.domain-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: 16px 20px; cursor: pointer; user-select: none;
  background: linear-gradient(180deg, #fafbfc, #f3f4f6);
  border-bottom: 1px solid #e5e7eb;
}
.domain-header h2 { margin: 0; font-size: 20px; display: flex; align-items: center; gap: 8px; }
.domain-header .chevron { transition: transform .15s; display: inline-block; color: #6b7280; }
.domain.collapsed .domain-header .chevron { transform: rotate(-90deg); }
.domain.collapsed .domain-body { display: none; }
.domain-stats { color: #6b7280; font-size: 13px; }
.domain-body { padding: 12px 20px 20px; }
.area { margin-top: 16px; }
.area-header {
  display: flex; align-items: baseline; gap: 12px;
  padding: 6px 0; border-bottom: 2px solid #f3f4f6;
  margin-bottom: 12px;
}
.area-header h3 { margin: 0; font-size: 16px; color: #111827; text-transform: uppercase; letter-spacing: .04em; }
.area-header .count { font-size: 12px; color: #6b7280; }
.microteams {
  display: grid; gap: 14px;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
}
.microteam {
  background: #fff; border: 1px solid #e5e7eb; border-radius: 10px;
  padding: 14px 16px; transition: box-shadow .15s, border-color .15s;
}
.microteam:hover { box-shadow: 0 4px 12px rgba(0,0,0,.04); border-color: #d1d5db; }
.mt-header h4 {
  margin: 0 0 10px 0; font-size: 14px;
  color: #0f172a; text-transform: uppercase; letter-spacing: .03em;
  border-left: 3px solid #4f46e5; padding-left: 8px;
}
.roles { display: flex; flex-direction: column; gap: 4px; margin-bottom: 10px; }
.role { display: flex; align-items: center; gap: 8px; font-size: 13px; }
.role-label {
  flex-shrink: 0; min-width: 64px;
  font-size: 11px; font-weight: 600; color: #6b7280;
  text-transform: uppercase; letter-spacing: .04em;
}
.role-value { display: flex; align-items: center; gap: 6px; color: #1f2937; }
.avatar {
  display: inline-flex; align-items: center; justify-content: center;
  width: 22px; height: 22px; border-radius: 50%;
  background: #ede9fe; color: #4f46e5;
  font-size: 10px; font-weight: 700; flex-shrink: 0;
}
.avatar.small { width: 18px; height: 18px; font-size: 9px; background: #e0e7ff; color: #3730a3; }
.members { border-top: 1px dashed #e5e7eb; padding-top: 10px; }
.members-label { font-size: 11px; font-weight: 600; color: #6b7280; text-transform: uppercase; letter-spacing: .04em; margin-bottom: 6px; }
.members-list { display: flex; flex-wrap: wrap; gap: 6px; }
.member-chip {
  display: inline-flex; align-items: center; gap: 5px;
  background: #f9fafb; border: 1px solid #e5e7eb; border-radius: 999px;
  padding: 3px 10px 3px 4px; font-size: 12px; color: #374151;
}
.microteam.hidden, .area.hidden, .domain.hidden { display: none; }
.empty { text-align: center; color: #9ca3af; padding: 60px 20px; font-size: 14px; }
.source-note { margin-top: 32px; font-size: 12px; color: #9ca3af; text-align: center; }
.source-note code { background: #f3f4f6; padding: 2px 6px; border-radius: 4px; }
@media (max-width: 640px) {
  .page { padding: 14px; }
  header.top h1 { font-size: 22px; }
  .microteams { grid-template-columns: 1fr; }
}
@media print {
  body { background: #fff; }
  .controls, .btn { display: none; }
  .domain { break-inside: avoid; border: 1px solid #ccc; }
  .microteam { break-inside: avoid; }
  .domain.collapsed .domain-body { display: block !important; }
  .domain.collapsed .chevron { transform: none !important; }
}
"""

JS = """
const $ = (s, r=document) => r.querySelector(s);
const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

$$('.domain-header').forEach(h => {
  h.addEventListener('click', () => h.parentElement.classList.toggle('collapsed'));
});

$('#expand-all').addEventListener('click', () => {
  $$('.domain').forEach(d => d.classList.remove('collapsed'));
});
$('#collapse-all').addEventListener('click', () => {
  $$('.domain').forEach(d => d.classList.add('collapsed'));
});

const input = $('#search');
const empty = $('#empty');

function applyFilter() {
  const q = input.value.trim().toLowerCase();
  let anyVisible = false;
  $$('.domain').forEach(domain => {
    let domainVisible = false;
    $$('.area', domain).forEach(area => {
      let areaVisible = false;
      $$('.microteam', area).forEach(mt => {
        const hay = (mt.dataset.name + ' ' + mt.dataset.tl + ' ' + mt.dataset.members + ' ' + (mt.textContent||'')).toLowerCase();
        const show = !q || hay.includes(q);
        mt.classList.toggle('hidden', !show);
        if (show) areaVisible = true;
      });
      area.classList.toggle('hidden', !areaVisible);
      if (areaVisible) domainVisible = true;
    });
    domain.classList.toggle('hidden', !domainVisible);
    if (domainVisible) {
      anyVisible = true;
      if (q) domain.classList.remove('collapsed');
    }
  });
  empty.style.display = anyVisible ? 'none' : 'block';
}

input.addEventListener('input', applyFilter);
$('#clear').addEventListener('click', () => { input.value = ''; applyFilter(); input.focus(); });
"""


def main():
    if not YAML_PATH.exists():
        print(f'ERROR: {YAML_PATH.name} not found', file=sys.stderr)
        sys.exit(1)

    with YAML_PATH.open(encoding='utf-8') as f:
        data = yaml.safe_load(f)

    domains = data.get('domains') or []
    if not domains:
        print('ERROR: no domains found in YAML', file=sys.stderr)
        sys.exit(1)

    total_areas = sum(len(d.get('areas') or []) for d in domains)
    total_mts = sum(len(a.get('microteams') or []) for d in domains for a in (d.get('areas') or []))
    all_tls = set()
    all_members = set()
    for d in domains:
        for a in d.get('areas') or []:
            for mt in a.get('microteams') or []:
                if mt.get('tl'):
                    all_tls.add(mt['tl'])
                for m in mt.get('members') or []:
                    all_members.add(m)

    body = ''.join(render_domain(d) for d in domains)

    html_out = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Engineering Org Chart</title>
<style>{CSS}</style>
</head>
<body>
<div class="page">
  <header class="top">
    <div>
      <h1>Engineering Org Chart</h1>
      <div class="subtitle">Domain &rarr; Area &rarr; Microteam structure</div>
    </div>
    <div class="stats">
      <div class="stat"><div class="num">{len(domains)}</div><div class="lbl">Domains</div></div>
      <div class="stat"><div class="num">{total_areas}</div><div class="lbl">Areas</div></div>
      <div class="stat"><div class="num">{total_mts}</div><div class="lbl">Microteams</div></div>
      <div class="stat"><div class="num">{len(all_tls)}</div><div class="lbl">Team Leads</div></div>
      <div class="stat"><div class="num">{len(all_members)}</div><div class="lbl">Members</div></div>
    </div>
  </header>

  <div class="controls">
    <label class="search">
      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
      <input id="search" type="text" placeholder="Search by name, microteam, TL, member&hellip;" autocomplete="off">
    </label>
    <button class="btn" id="clear">Clear</button>
    <button class="btn" id="expand-all">Expand all</button>
    <button class="btn" id="collapse-all">Collapse all</button>
  </div>

  {body}

  <div class="empty" id="empty" style="display:none">No matches.</div>
  <div class="source-note">Source: <code>organigrama.yaml</code> &middot; rebuild with <code>python3 build.py</code></div>
</div>
<script>{JS}</script>
</body>
</html>
"""

    HTML_PATH.write_text(html_out, encoding='utf-8')
    print(f'Wrote {HTML_PATH.name} ({len(html_out):,} bytes)')
    print(f'  {len(domains)} domains, {total_areas} areas, {total_mts} microteams, '
          f'{len(all_tls)} TLs, {len(all_members)} members')


if __name__ == '__main__':
    main()
