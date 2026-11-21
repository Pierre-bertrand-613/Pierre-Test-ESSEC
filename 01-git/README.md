# 01 - Git mini exo

Énoncé : https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388 (slide 26)

`install.sh` est le script de la Part 7. Il a été ajouté sur la branche `feature-install`, puis mergé dans `main` (Part 11).

## Part 1 : Setup & config

```bash
git --version
git config --global user.name "Pierre Bertrand"
git config --global user.email "mon.email@example.com"
git config --list            # vérifier
```

## Part 2 : Créer un repo

```bash
mkdir my-first-repo
cd my-first-repo
git init
touch readme.txt
```

## Part 3 : Premier commit

| Question | Commande |
|---|---|
| État du repo | `git status` |
| Stager `readme.txt` | `git add readme.txt` |
| Commit | `git commit -m "Add readme file"` |
| Historique | `git log` |

## Part 4 : Modifications

```bash
echo "Une nouvelle ligne" >> readme.txt
git status      # readme.txt apparaît en rouge dans "Changes not staged for commit" :
                # Git sait que le fichier suivi a été modifié, mais le changement n'est pas encore stagé
git add readme.txt
git commit -m "Add a second line to readme"
git log --oneline   # 2 commits
```

## Part 5 : Exploration

- `git diff` affiche, ligne par ligne, les différences entre le working directory et la staging area (ce qui a été modifié mais pas encore `add`). `git diff --staged` compare la staging area au dernier commit.
- `git log --oneline` affiche l'historique compact : une ligne par commit (hash court + message).

## Part 6 : Branches

| Question | Commande |
|---|---|
| Lister les branches | `git branch` |
| Créer `feature-script` | `git branch feature-script` |
| Basculer dessus | `git switch feature-script` (ou `git checkout feature-script`) |
| Créer + basculer sur `dev` | `git switch -c dev` (ou `git checkout -b dev`) |
| Revenir sur `feature-script` | `git switch feature-script` |
| Vérifier | `git branch` (la branche courante a une `*`) ou `git status` |

## Part 7 : Script bash sur une branche

```bash
git switch feature-script
touch install.sh          # contenu : voir install.sh
chmod +x install.sh
git add install.sh
git commit -m "Add install script"
git log --oneline
```

## Part 8 : Merge

```bash
git switch main
ls                         # install.sh n'est PAS là : il n'existe que dans les commits de feature-script
git merge feature-script
ls                         # install.sh est maintenant présent
git log --oneline          # le commit "Add install script" fait partie de l'historique de main
                           # (fast-forward : main a simplement avancé jusqu'au commit de la branche)
git branch -d feature-script
```

## Part 9 : Push sur GitHub

Je crée le repo `my-first-repo` sur github.com **sans** README, sinon les deux historiques divergent et le premier push est refusé.

```bash
git remote add origin git@github.com:Pierre-bertrand-613/my-first-repo.git
git branch -M main
git push -u origin main
```

Quand je rafraîchis la page GitHub, je vois mes fichiers (`readme.txt`, `install.sh`) et l'historique des commits.

## Part 10 : Supprimer et cloner

```bash
cd ..
rm -rf my-first-repo
git clone git@github.com:Pierre-bertrand-613/my-first-repo.git
cd my-first-repo
ls && git log --oneline    # tout est revenu : GitHub garde une copie complète du repo
```

## Part 11 : Workflow complet

```bash
mkdir bash-installer && cd bash-installer
git init
echo "# bash-installer" > README.md
git add README.md && git commit -m "Add README"
git switch -c feature-install
cp ../install.sh . && chmod +x install.sh
git add install.sh && git commit -m "Add install script"
git switch main
git merge feature-install
git branch -d feature-install
gh repo create bash-installer --public --source=. --push   # ou : créer sur github.com + git remote add + git push
```

Ce workflow est appliqué à ce repo : chaque exercice a été développé sur sa propre branche (`feature-install`, `feature-bash-env`, `feature-oop`, …) puis mergé dans `main`.

## Questions de réflexion

1. **Pourquoi le versioning est utile ?** On garde un historique de chaque modification, on peut revenir en arrière, savoir qui a changé quoi et pourquoi, travailler à plusieurs sans s'écraser et avoir une sauvegarde à distance.
2. **Staging vs commit ?** Le staging (`git add`) prépare les modifications à inclure : c'est un brouillon qu'on peut encore ajuster. Le commit (`git commit`) enregistre définitivement ce snapshot dans l'historique, avec un message.
3. **Quand committer ?** Dès qu'on a une unité de travail cohérente qui fonctionne (une feature, un fix, un refactor). On fait des petits commits fréquents plutôt qu'un énorme commit en fin de journée.
4. **`git init` vs `git clone` ?** `git init` crée un nouveau repo vide dans un dossier local. `git clone` copie un repo existant (distant) avec tout son historique et configure le remote `origin`.
5. **Pourquoi de bons messages de commit ?** Pour que l'historique se lise comme un journal : retrouver un changement, comprendre pourquoi il a été fait, faciliter la review et le debug (`git log`, `git blame`, `git bisect`).
6. **À quoi servent les branches ?** À développer une feature ou un fix de façon isolée, sans casser `main`, puis à l'intégrer par un merge une fois terminé et testé.
7. **Quand créer une branche plutôt que travailler sur `main` ?** Pour toute nouvelle feature, toute expérimentation, tout fix qui n'est pas trivial, et dès qu'on travaille à plusieurs. `main` doit toujours rester stable et fonctionnelle.
