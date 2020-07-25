git config --global credential.helper store
Add-Content -Path "$HOME\.git-credentials" -Value "https://$($env:access_token):x-oauth-basic@github.com`n" -NoNewline
git config --global user.email "32603156+rogerlord@users.noreply.github.com"
git config --global user.name "AppVeyor"
git add -Af .\data
if (git status --porcelain) {
    $dt = (Get-Date).ToString("yyyy-mm-dd")	
	git commit -m $dt
    git fetch --all
    git checkout -f master
    git merge HEAD@{1} -s recursive -X ours
    git push --all
}
