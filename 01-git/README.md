# 01 - Git mini exo

Exercise: https://gist.github.com/bdallard/8bdbdd70f234f94823c0c2cde9515388 (slide 26)

`install.sh` is the script from part 7. I made it on the `feature-install` branch and then merged it into main (part 11).

## Part 1 - Setup & config

```bash
git --version
git config --global user.name "Pierre Bertrand"
git config --global user.email "my.email@example.com"
git config --list   # to check
```

## Part 2 - First repo

```bash
mkdir my-first-repo
cd my-first-repo
git init
touch readme.txt
```

## Part 3 - First commit

1. `git status`
2. `git add readme.txt`
3. `git commit -m "Add readme file"`
4. `git log`

## Part 4 - Make changes

```bash
echo "a new line" >> readme.txt
git status
```

`git status` shows readme.txt in red under "Changes not staged for commit": git knows the file changed but I haven't added it yet.

```bash
git add readme.txt
git commit -m "Add a second line to readme"
git log --oneline   # 2 commits now
```

## Part 5 - Exploration

- `git diff`: shows the lines I changed that are not staged yet (`git diff --staged` shows what is staged)
- `git log --oneline`: the history on one line per commit (short hash + message)

## Part 6 - Branches

1. `git branch`
2. `git branch feature-script`
3. `git switch feature-script` (or `git checkout feature-script`)
4. `git switch -c dev` (or `git checkout -b dev`)
5. `git switch feature-script`
6. `git branch` (the current branch has a `*`)

## Part 7 - Bash script on a branch

```bash
git switch feature-script
touch install.sh     # see install.sh for the content
chmod +x install.sh
git add install.sh
git commit -m "Add install script"
git log --oneline
```

## Part 8 - Merge

```bash
git switch main
ls                       # install.sh is not here, it only exists on feature-script
git merge feature-script
ls                       # now install.sh is here
git log --oneline        # the "Add install script" commit is in main's history (fast-forward)
git branch -d feature-script
```

## Part 9 - Push to GitHub

Create `my-first-repo` on github.com **without** a README (otherwise the histories are different and the push gets rejected).

```bash
git remote add origin git@github.com:Pierre-bertrand-613/my-first-repo.git
git branch -M main
git push -u origin main
```

After refreshing the page I can see my files and my commits.

## Part 10 - Delete and clone

```bash
cd ..
rm -rf my-first-repo
git clone git@github.com:Pierre-bertrand-613/my-first-repo.git
cd my-first-repo
ls   # everything is back
```

## Part 11 - Full workflow

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
# create the repo on GitHub, then:
git remote add origin git@github.com:Pierre-bertrand-613/bash-installer.git
git push -u origin main
```

## Reflection questions

1. **Why is version control useful?** You keep the whole history, you can go back if you break something, you can see who changed what, and you can work with other people without overwriting their work.
2. **Staging vs committing?** Staging (`git add`) is choosing what goes in the next commit, you can still change it. Committing saves that snapshot in the history with a message.
3. **When should you commit?** Every time you finish a small thing that works (a feature, a fix...). Small commits are better than one huge commit at the end.
4. **`git init` vs `git clone`?** `git init` creates a new empty repo. `git clone` copies an existing repo (with all its history) and sets up `origin`.
5. **Why write good commit messages?** So you (and others) can understand the history later and find when/why something changed.
6. **Why use branches?** To work on something without breaking main, and merge it only when it's ready.
7. **When to create a branch instead of working on main?** For any new feature or experiment, and always when working in a team. Main should always work.
