

### ✅ Step-by-Step: Add Download Button for `RaceAssist.exe` in `README.md`

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

