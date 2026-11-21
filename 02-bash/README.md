# 02 - Bash script exercise

Énoncé : https://courses.dallard.tech/linux/bash_exo/ (slide 13)

## Part 1 : Améliorer son shell

```bash
echo "$0"          # le shell en cours d'exécution (ex : -zsh)
echo "$SHELL"      # le shell de login de l'utilisateur (ex : /bin/zsh sur macOS)
```

Installer Oh My Zsh (zsh) ou Oh My Bash (bash) :

```bash
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
```

Puis dans `~/.zshrc` (ou `~/.bashrc`) : choisir un thème (`ZSH_THEME="agnoster"`), activer le plugin git avec `plugins=(git)`, et recharger avec `source ~/.zshrc`.

**À quoi sert `source` ?** Il exécute un fichier *dans le shell courant*, et pas dans un sous-shell. Les variables, alias et fonctions qu'il définit restent donc disponibles dans le terminal. C'est ce qui permet de recharger sa config sans rouvrir de terminal.

Alias du plugin git : `gst` = `git status`, `glog` = `git log --oneline --graph`, `gp` = `git push`, `gl` = `git pull`.

## Part 2 : Python

```bash
python3 --version
```

## Part 3 : `env_install.sh`

```bash
chmod +x env_install.sh
./env_install.sh --dry-run     # montre ce qui serait fait, sans rien installer
./env_install.sh               # installation réelle
./env_install.sh --uninstall   # désinstalle Jupyter
```

| Feature | Fonction |
|---|---|
| 1. Pretty printing (`printf`, lignes vides) | `pretty_print` |
| 2. Détection de l'OS via `$OSTYPE` | `detect_os` |
| 3. Vérification / installation de python3 | `check_python` |
| 4. Vérification de pip | `check_pip` |
| 5. Installation de Jupyter Notebook | `install_jupyter` |
| 6. `brew doctor` sur macOS | `brew_health_check` |

Bonus réalisés :
- **couleurs** ANSI : vert = info, jaune = warning, rouge = erreur ;
- **logging** horodaté dans `env_install.log` (chaque commande, son succès ou son échec) ;
- **strict mode** `set -euo pipefail` ;
- flags `--dry-run`, `--verbose`, `--quiet` ;
- option `--uninstall`.

## Part 4 : Checklist

- [x] Le prompt reflète le framework installé
- [x] `gst` fonctionne
- [x] `python3 --version` → 3.x
- [x] `python3 -m pip --version`
- [x] `jupyter notebook` se lance
- [x] `brew doctor` (macOS)
