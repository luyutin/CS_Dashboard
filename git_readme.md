如果是第一次把專案推到新的 GitHub repo：
```
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote set-url origin https://github.com/luyutin/publicis_media_dashboard.git
git push -u origin main
```

之後每次只要：
```
git add .
git commit -m "更新內容"
git push
```