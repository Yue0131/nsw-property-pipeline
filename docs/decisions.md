# Design decisions

One entry per decision. Keep each short.

## YYYY-MM-DD — Title
- **Context:** what problem I faced
- **Options:** what I considered
- **Decision:** what I chose
- **Why / trade-offs:** what I gain and what I give up

## 2026-10-26 — Use a conda environment instead of venv
- **Context:** PySpark 3.5 only supports Java 8, 11 and 17. My Mac has Java 25 installed system-wide, and Python 3.11 was not installed.
- **Options:**
  1. venv + install Python 3.11 and Java 17 with Homebrew, then switch `JAVA_HOME` manually.
  2. conda environment with `python=3.11` and `openjdk=17` from conda-forge.
  3. Upgrade to PySpark 4.x, which supports newer Java.
- **Decision:** Option 2. Create the env with `conda create -n nsw-pipeline -c conda-forge python=3.11 openjdk=17`, then `pip install -r requirements.txt`.
- **Why / trade-offs:** Java 17 lives inside the project env and `JAVA_HOME` is set on activate, so the system Java 25 is untouched and setup is one command. The cost is that anyone running the project needs conda, and mixing conda and pip packages needs care (I only use conda for Python and Java, and pip for everything else).
