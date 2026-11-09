# Commands by system

This page lists every terminal command you need to add a skill to vibe.md or to install skills. Each step has the commands for macOS, Linux and Windows. For the full contribution rules, see [CONTRIBUTING.md](../CONTRIBUTING.md).

A few terms:

- **Terminal**: the window where you type commands. On Windows, the examples use PowerShell or Git Bash.
- **Git Bash**: a bash terminal that comes with Git for Windows.
- **WSL**: Windows Subsystem for Linux. It runs a real Linux terminal inside Windows. In WSL, follow the Linux commands.

Windows is not tested in CI. The Windows notes come from reading the code, not from running it there.

## 1. Install Git and Python

You need Git and Python 3.9 or later.

### macOS

`xcode-select --install` installs Git and Python 3. You can also use Homebrew.

```bash
xcode-select --install
# or, with Homebrew:
brew install git python

git --version
python3 --version
```

### Linux

Use the command for your distribution.

```bash
# Debian or Ubuntu
sudo apt update && sudo apt install -y git python3 python3-venv python3-pip

# Fedora
sudo dnf install -y git python3 python3-pip

git --version
python3 --version
```

### Windows

Git for Windows includes Git Bash, but not Python, so install both. Open a new terminal after you install. Use the `py` launcher on Windows. `python3` may open the Microsoft Store instead. You can also download Python from [python.org](https://www.python.org/downloads/windows/).

```powershell
winget install --id Git.Git -e
winget install --id Python.Python.3.12 -e

git --version
py --version
```

## 2. Fork, clone, and create a branch

First, fork [vibe-md/vibe.md](https://github.com/vibe-md/vibe.md) on GitHub. Then clone your fork and make a branch.

A skill in a package lives at `skills/<package>/<package>-<skill>/SKILL.md`. A standalone skill lives at `skills/<skill-name>/SKILL.md`. These examples use `my-skill` as a standalone skill.

### macOS

```bash
git clone https://github.com/<your-username>/vibe.md.git
cd vibe.md
git remote add upstream https://github.com/vibe-md/vibe.md.git
git fetch upstream main
git checkout -b add-my-skill
mkdir -p skills/my-skill
```

### Linux

```bash
git clone https://github.com/<your-username>/vibe.md.git
cd vibe.md
git remote add upstream https://github.com/vibe-md/vibe.md.git
git fetch upstream main
git checkout -b add-my-skill
mkdir -p skills/my-skill
```

### Windows

PowerShell paths use `\`. Git and the `--files` option of the scripts use `/`.

```powershell
git clone https://github.com/<your-username>/vibe.md.git
cd vibe.md
git remote add upstream https://github.com/vibe-md/vibe.md.git
git fetch upstream main
git checkout -b add-my-skill
mkdir skills\my-skill
```

## 3. Create a virtual environment

A virtual environment keeps the project's Python packages separate from the rest of your computer. Leave it with `deactivate`.

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Windows

With the environment active, `py` uses the environment's Python. If PowerShell says running scripts is disabled on this system, run one of the `Set-ExecutionPolicy` lines, then activate again. In Git Bash, use `source .venv/Scripts/activate` instead.

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1

# Only if PowerShell blocks the script. Once, for your user:
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
# Or for this window only:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

## 4. Install dev requirements and run the checks

Run these from the repository folder, with the virtual environment active. Use `upstream/main` in a fork. Use `origin/main` in a clone of vibe-md/vibe.md.

### macOS

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests
python3 scripts/check-contribution.py --base upstream/main
```

### Linux

```bash
python3 -m pip install -r requirements-dev.txt
python3 scripts/validate-skills.py
python3 -m unittest discover -s tests
python3 scripts/check-contribution.py --base upstream/main
```

### Windows

`validate-skills.py` and `check-contribution.py` are plain Python. They are expected to work in PowerShell. `check-contribution.py` runs `git`, so Git must be on your PATH. To check one file without a Git diff, use `--files` with forward slashes.

Run the test suite in WSL, using the Linux commands. Clone the repository inside WSL's own file system (for example `~/vibe.md`) and make a new virtual environment there. A Windows `.venv` does not work in WSL. The tests run `bash scripts/install.sh`, make symbolic links, and set executable bits. Git Bash is not enough for the full suite. Windows allows symbolic links only with Developer Mode or admin rights. Windows Python cannot set an executable bit on a `.md` file.

`build-packages.py` calls bash. Run it in Git Bash or WSL.

```powershell
py -m pip install -r requirements-dev.txt
py scripts/validate-skills.py
py scripts/check-contribution.py --base upstream/main
py scripts/check-contribution.py --files skills/my-skill/SKILL.md
```

## 5. Install skills with install.sh

`install.sh` is a bash script. `<agent>` is one of `claude-code`, `codex`, `cursor`, `gemini` or `copilot`. It needs Bash 3.2 or later. If you run it without cloning, it also needs `curl` and `tar`. Add `--dry-run` first to preview. It changes nothing.

The first block clones the repository and runs the script. The second downloads the script so you can read it before you run it. The third runs it in one line. The last block tests your own skill in a scratch folder.

### macOS

```bash
# Clone and run
git clone https://github.com/vibe-md/vibe.md.git ~/vibe.md
bash ~/vibe.md/scripts/install.sh --list
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code --dry-run
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code

# Or download, review, then run
curl -fsSL -o vibe-install.sh https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh
less vibe-install.sh
bash vibe-install.sh --list
bash vibe-install.sh --group gitly --agent codex --dry-run
bash vibe-install.sh --group gitly --agent codex

# Or in one line
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex --dry-run
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex

# Test your own skill (from the repository folder)
mkdir -p /tmp/skill-playground
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground --dry-run
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground
```

### Linux

```bash
# Clone and run
git clone https://github.com/vibe-md/vibe.md.git ~/vibe.md
bash ~/vibe.md/scripts/install.sh --list
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code --dry-run
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code

# Or download, review, then run
curl -fsSL -o vibe-install.sh https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh
less vibe-install.sh
bash vibe-install.sh --list
bash vibe-install.sh --group gitly --agent codex --dry-run
bash vibe-install.sh --group gitly --agent codex

# Or in one line
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex --dry-run
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex

# Test your own skill (from the repository folder)
mkdir -p /tmp/skill-playground
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground --dry-run
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground
```

### Windows

Use Git Bash or WSL. Do not use PowerShell or cmd. Git for Windows includes bash, `curl` and `tar`. In Git Bash, a Windows path looks like `/c/Users/<you>/my-project`. In WSL, it looks like `/mnt/c/Users/<you>/my-project`. This has not been tested in CI. The commands below are the same as on Linux, except for the project path in the last step.

```bash
# Clone and run
git clone https://github.com/vibe-md/vibe.md.git ~/vibe.md
bash ~/vibe.md/scripts/install.sh --list
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code --dry-run
bash ~/vibe.md/scripts/install.sh --group gitly --agent claude-code

# Or download, review, then run
curl -fsSL -o vibe-install.sh https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh
less vibe-install.sh
bash vibe-install.sh --list
bash vibe-install.sh --group gitly --agent codex --dry-run
bash vibe-install.sh --group gitly --agent codex

# Or in one line
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex --dry-run
curl -fsSL https://raw.githubusercontent.com/vibe-md/vibe.md/main/scripts/install.sh | bash -s -- --skill <skill-name> --agent codex

# Test your own skill (from the repository folder)
mkdir -p /tmp/skill-playground
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground --dry-run
bash scripts/install.sh --skill <skill-name> --agent claude-code --project /tmp/skill-playground
```

## What works natively on Windows

"Yes" means expected to work, based on reading the code. "No" means the code needs something that PowerShell or Git Bash does not provide.

| Step | PowerShell | Git Bash | WSL |
| --- | --- | --- | --- |
| Install Git and Python | Yes (`winget`) | Git Bash comes with Git. Install Python separately, from PowerShell (`winget`) or [python.org](https://www.python.org/downloads/windows/) | Yes (Linux commands) |
| Clone and branch | Yes | Yes | Yes |
| Virtual environment | Yes | Yes | Yes |
| `pip install` | Yes | Yes | Yes |
| `validate-skills.py` | Yes (pure Python, handles Windows drives, `scripts/validate-skills.py:66-68`) | Yes | Yes |
| `check-contribution.py` | Yes, with Git on PATH (`scripts/check-contribution.py:92`) | Yes | Yes |
| Unit tests | No (run `bash`, `tests/test_installer.py:74-77`) | No, partly (symlinks, `tests/test_validator.py:130`; chmod, `tests/test_validator_safety.py:88`) | Yes |
| `build-packages.py` | No (calls bash, `scripts/build-packages.py:72-73`) | Probably (bash is on PATH there; not checked) | Yes |
| `install.sh` | No (bash script) | Yes | Yes |

## Not tested in CI

The workflow [`validate-skills.yml`](../.github/workflows/validate-skills.yml) runs only on `ubuntu-latest` and `macos-latest`. Nobody runs the Windows commands in this file automatically. If a Windows command fails for you, please open an issue.
