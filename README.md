# grissino-teams

Repo to keep track of grissino teams and members of each team.

Engineering org chart — generated as a self-contained HTML page from a YAML source of truth.

## Files

- **`organigrama.yaml`** — source of truth. Domain → Area → Microteam hierarchy. Edit this.
- **`build.py`** — generator. Reads the YAML, emits `organigrama.html`.
- **`organigrama.html`** — generated output. Self-contained (inline CSS + JS), no external dependencies.

The original `organigrama.xlsx` is kept locally as backup but is not versioned (see `.gitignore`).

## Usage

```bash
pip3 install pyyaml
python3 build.py
open organigrama.html
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
