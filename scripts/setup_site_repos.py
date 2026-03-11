"""
setup_site_repos.py
-------------------
Run ONCE from E:\\0x

What it does:
  1. Deletes fleet_audit.json
  2. Writes CLAUDE.md into every site folder (active + banned)
  3. Writes .gitignore into every site folder
  4. git init in every site folder
  5. Initial commit in every site folder

Each site becomes a fully isolated local git repo.
No site knows any other site exists.
"""

import os
import subprocess
from pathlib import Path

SITES_DIR = Path(r"E:\0x\sites")

BANNED = {
    "adamstratmeyer.com",
    "cremedepoignet.com",
    "irbgpt.com",
    "nursesarahs.com",
    "observablecompute.org",
    "stratmeyeranalytica.org",
    "wristcream.com",
}

CLAUDE_MD_ACTIVE = """\
# {domain}

## HARD STOP

This is a standalone, isolated project.
It has NO relationship to any other website.

- NO fleet operations
- NO batch deploys
- NO multi-site scripts
- NO association with any other domain
- ONE site. ONE build.py. ONE deploy.py. That is all.

---

## Rules

See `SITE.md` for the complete 32 Laws, E-E-A-T requirements,
banned text list, required files checklist, and deployment workflow.

## Workflow (in order, no shortcuts)

1. OBSERVE — Open `public_html/index.html`. Note what exists.
2. PLAN — Design changes for THIS SITE ONLY. Get AIS approval.
3. BUILD — Run `build.py`. Touches only `public_html/` in this folder.
4. VERIFY — Check 32 Laws. Scan for banned text.
5. DEPLOY — Run `deploy.py`. Uploads only to this site's server path.
"""

CLAUDE_MD_BANNED = """\
# {domain}

## 🔒 BANNED — DO NOT TOUCH

This domain is permanently off-limits.

- DO NOT build
- DO NOT modify
- DO NOT deploy
- DO NOT read files with intent to change them
- EVER

No exceptions. No overrides.
"""

GITIGNORE = """\
__pycache__/
*.pyc
*.pyo
.DS_Store
Thumbs.db
"""


def git(cmd, cwd):
    result = subprocess.run(
        cmd, cwd=cwd, shell=True,
        capture_output=True, text=True
    )
    if result.returncode != 0:
        print(f"    [warn] {cmd!r} -> {result.stderr.strip()}")
    return result.returncode == 0


def setup():
    # 1. Delete fleet_audit.json
    audit = Path(r"E:\0x\fleet_audit.json")
    if audit.exists():
        audit.unlink()
        print("[deleted] fleet_audit.json")
    else:
        print("[skip] fleet_audit.json not found")

    # 2. Process each site folder
    site_dirs = sorted([d for d in SITES_DIR.iterdir() if d.is_dir()])

    for site_dir in site_dirs:
        domain = site_dir.name
        is_banned = domain in BANNED

        print(f"\n[{'BANNED' if is_banned else 'active'}] {domain}")

        # Write CLAUDE.md
        template = CLAUDE_MD_BANNED if is_banned else CLAUDE_MD_ACTIVE
        claude_md = site_dir / "CLAUDE.md"
        claude_md.write_text(template.format(domain=domain), encoding="utf-8")
        print(f"    [wrote] CLAUDE.md")

        # Write .gitignore
        gitignore = site_dir / ".gitignore"
        gitignore.write_text(GITIGNORE, encoding="utf-8")
        print(f"    [wrote] .gitignore")

        # git init (skip if already a repo)
        git_dir = site_dir / ".git"
        if git_dir.exists():
            print(f"    [skip] already a git repo")
        else:
            git("git init", site_dir)
            print(f"    [init] git repo created")

        # Initial commit
        git("git add .", site_dir)
        git(f'git commit -m "init: {domain} — isolated standalone project"', site_dir)
        print(f"    [commit] initial commit done")

    print("\n✓ All site repos structured. fleet_audit.json deleted.")
    print("✓ Each site is now an independent git repo with its own CLAUDE.md.")
    print("✓ No site references any other site.")


if __name__ == "__main__":
    setup()
