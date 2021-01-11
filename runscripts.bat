@ECHO ON
SET ERRORS = 0
python covid_19\\nl\\script.py .\\
IF %ERRORLEVEL% NEQ 0 (
	SET /A ERRORS = ERRORS + 1
)

python covid_19\\de\\script.py .\\
IF %ERRORLEVEL% NEQ 0 (
	SET /A ERRORS = ERRORS + 1
)

python covid_19\\uk\\script.py .\\
IF %ERRORLEVEL% NEQ 0 (
	SET /A ERRORS = ERRORS + 1
)

powershell gitcommit.ps1
IF %ERRORLEVEL% NEQ 0 (
	SET /A ERRORS = ERRORS + 1
	EXIT /B %ERRORLEVEL%
)