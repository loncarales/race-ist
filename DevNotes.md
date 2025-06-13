## Dev Notes

### Software Build `RaceAssist.exe` 
```
pyinstaller --onefile --noconsole `
--icon=RaceAssist.ico `
--version-file=version.txt `
--add-data="..\venv\Lib\site-packages\mediapipe\modules;mediapipe\modules" `
run.py
``` 
###  Download Feature for `RaceAssist.exe` in `README.md`

#### 🧾 1. Upload `RaceAssist.exe` to a GitHub Release

You **cannot directly link `.exe` from the repo folder** — GitHub blocks downloads of binaries for security.

Instead:

1. Go to your GitHub repo
2. Click **"Releases"** (or create a new one from **"Create a new release"**)
3. Attach `RaceAssist.exe` as a binary asset
4. Publish the release

Once published, the download URL will look like:

```
https://github.com/<username>/<repo>/releases/download/<tag>/RaceAssist.exe
```

Example:

```
https://github.com/kintsugidev/RaceAssist/releases/download/v1.0/RaceAssist.exe
```

---

#### 🧩 2. Add to `README.md`

Use this Markdown snippet:

```md
## 🔽 Download & Try Now

### ✅ RaceAssist – Plug & Play Edition  
> 🎮 No Python. No Setup. Just Run & Race.

[![Download RaceAssist](https://img.shields.io/badge/Download-RaceAssist.exe-blue?logo=windows)](https://github.com/kintsugidev/RaceAssist/releases/download/v1.0/RaceAssist.exe)
```

> 📝 **Make sure to update the actual URL** with your real GitHub release link.

###  Delete or modify a middle commit
---

### ⚠️ **IMPORTANT WARNING**

> If you've already **pushed** your commits to a remote (like GitHub) and **other people or systems rely on it**, rewriting history (like deleting a middle commit) can cause **issues or conflicts**.

If you're **working alone or haven't pushed yet**, you're safe to proceed.

---

## 🧹 Option 1: Use Interactive Rebase (Safest for Middle Commits)

This allows you to **edit, delete, or squash** any commit *before HEAD*.

### ✅ Steps:

```bash
# Open the last N commits in interactive rebase
git rebase -i HEAD~N
# Replace N with number of commits from HEAD you want to go back (e.g., 5)
```

### 🔧 In the Editor That Opens:

You'll see something like:

```bash
pick a1b2c3d Commit message 1
pick d4e5f6g Commit message 2 ← you want to delete this?
pick h7i8j9k Commit message 3
```

* Change the word `pick` to `drop` for the commit you want to delete:

```bash
pick a1b2c3d Commit message 1
drop d4e5f6g Commit message 2  ← this will be deleted
pick h7i8j9k Commit message 3
```

* Save and close the editor. Git will rebase and remove that commit.

---

## 🚨 If You've Already Pushed

Then after the rebase, you'll need to force push:

```bash
git push --force
```

**Caution**: This rewrites history. If you're working with others, they will need to sync using `git pull --rebase` or reset their branches.

---

## 🧠 Pro Tip

Use `git log --oneline` to find the number of commits and commit hashes before rebasing.

---
