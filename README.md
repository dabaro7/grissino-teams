# grissino-teams

Repo to keep track of grissino teams and members of each team.

Engineering org chart — generated as a self-contained HTML page from a YAML source of truth.

**Live site:** https://dabaro7.github.io/grissino-teams/

## Files

- **`organigrama.yaml`** — source of truth. Domain → Area → Microteam hierarchy. Edit this.
- **`build.py`** — generator. Reads the YAML, emits `index.html`.
- **`.github/workflows/deploy.yml`** — CI: rebuilds and deploys to GitHub Pages on every push to `main`.

The generated `index.html` is **not committed** — it's built by CI from the YAML on every push. The original `organigrama.xlsx` is also not versioned (kept locally as backup).

## Editing the org chart

1. Edit `organigrama.yaml`.
2. Commit and push to `main`.
3. GitHub Actions runs `build.py`, regenerates `index.html`, and deploys to Pages.
4. Live site updates in about a minute.

## Local preview

```bash
pip3 install pyyaml
python3 build.py
open index.html
```

## YAML schema

```yaml
domains:
  - name: <Domain>
    areas:
      - name: <Area>
        microteams:
          - name: <Microteam>
            tl: <Team Lead>           # optional
            pm: <Product Manager>     # optional
            ux: <UX Designer>         # optional
            po: <Product Owner>       # optional
            qa: <QA / Other>          # optional
            members:                  # optional
              - <Person 1>
              - <Person 2>
```

Omit optional keys entirely when there is no value (don't leave them with empty values).

## Features in the generated HTML

- Search by microteam name, team lead, or member.
- Collapsible domain sections.
- Expand all / collapse all.
- Print-friendly (all sections expand when printing).
