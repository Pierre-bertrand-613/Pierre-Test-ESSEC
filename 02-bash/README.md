# 02 - Bash script exercise

Exercise: https://courses.dallard.tech/linux/bash_exo/

## Part 1 - Shell

```bash
echo $0       # shell currently running
echo $SHELL   # my login shell (/bin/zsh on my Mac)
```

I'm on zsh so I installed Oh My Zsh, then in `~/.zshrc` I picked a theme and added `plugins=(git)`, then ran `source ~/.zshrc`.

**What's the purpose of `source`?** It runs the file in the current shell (not in a new one), so the variables/aliases it defines stay available. That's how you reload your config without opening a new terminal.

Git aliases I tested: `gst` = git status, `gp` = git push, `gl` = git pull.

## Part 2 - Python

```bash
python3 --version
```

## Part 3 - The script

```bash
chmod +x env_install.sh
./env_install.sh --dry-run   # shows what it would do without installing anything
./env_install.sh
```

What it does:
1. `pretty_print` function (with printf and blank lines)
2. detects the OS with `$OSTYPE`
3. checks python3, installs it if missing
4. checks pip
5. installs Jupyter Notebook
6. runs `brew doctor` on macOS

I also tried some of the bonus: colors, a log file, strict mode (`set -euo pipefail`), `--dry-run` / `--verbose` / `--quiet` flags and an `--uninstall` option.
