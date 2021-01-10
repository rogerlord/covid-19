$success = $true

cmd /c python covid_19\\nl\\script.py 
if (-not $?) {$success = $?}

cmd /c python covid_19\\de\\script.py
if (-not $?) {$success = $?}

cmd /c python covid_19\\uk\\script.py
if (-not $?) {$success = $?}

.\gitcommit.ps1

if (-not $success) {throw "at least one step failed"}