# Base Rules

* **Response Language:** `zh-TW`
* All specifications, plans, and user-facing documentation MUST be written in Traditional Chinese (zh-TW). Only the constitution MUST be in English.
* When drafting the constitution, the context MUST be translated into `constitution_zhTW.md` and placed in the same directory (file names are case-sensitive).
* Git logs and code annotations MUST be written in Traditional Chinese (zh-TW).

# Development Guidelines

* When the frontend calls a backend API or function, ensure the API/function actually exists on the backend. Do not arbitrarily name or assume APIs/functions.
* Avoid over-design and over-engineering.
* During development, the frontend UI should account for layout height. Input fields, components, and their placement should be consistent across the interface.

# Virtual Environment

* Check whether a virtual environment (e.g., `.venv`) exists in the current folder. If it does, do not create a new virtual environment.

# Skills

Skills in this project are stored as folders under `.github/skills/`. Each skill has a fixed entry file named `SKILL.md`.

* **How to reference / find skills**
  * Open directly: `.github/skills/<skill-id>/SKILL.md`
  * VS Code global search: search for `path:.github/skills SKILL.md`, or search by skill-id (e.g. `python-venv-check`)
  * Browse the directory: open `.github/skills/` to see the list of available skills

* **Included skills (folder name = skill-id)**
  * `RunPowerShell`: `.github/skills/RunPowerShell/SKILL.md`
  * `algorithmic-art`: `.github/skills/algorithmic-art/SKILL.md`
  * `brand-guidelines`: `.github/skills/brand-guidelines/SKILL.md`
  * `canvas-design`: `.github/skills/canvas-design/SKILL.md`
  * `commit-message-helper`: `.github/skills/commit-message-helper/SKILL.md`
  * `copilot-sdk`: `.github/skills/copilot-sdk/SKILL.md`
  * `container-image-hygiene`: `.github/skills/container-image-hygiene/SKILL.md`
  * `doc-coauthoring`: `.github/skills/doc-coauthoring/SKILL.md`
  * `docx`: `.github/skills/docx/SKILL.md`
  * `frontend-design`: `.github/skills/frontend-design/SKILL.md`
  * `internal-comms`: `.github/skills/internal-comms/SKILL.md`
  * `mcp-builder`: `.github/skills/mcp-builder/SKILL.md`
  * `pdf`: `.github/skills/pdf/SKILL.md`
  * `pptx`: `.github/skills/pptx/SKILL.md`
  * `python-venv-check`: `.github/skills/python-venv-check/SKILL.md`
  * `skill-creator`: `.github/skills/skill-creator/SKILL.md`
  * `slack-gif-creator`: `.github/skills/slack-gif-creator/SKILL.md`
  * `theme-factory`: `.github/skills/theme-factory/SKILL.md`
  * `web-artifacts-builder`: `.github/skills/web-artifacts-builder/SKILL.md`
  * `webapp-testing`: `.github/skills/webapp-testing/SKILL.md`
  * `xlsx`: `.github/skills/xlsx/SKILL.md`