# PowerShell script to run tests with DBStorage
# Usage: .\run_tests_db.ps1

Write-Host "Running tests with DBStorage (MySQL)..." -ForegroundColor Green

$env:HBNB_ENV = "test"
$env:HBNB_MYSQL_USER = "hbnb_test"
$env:HBNB_MYSQL_PWD = "hbnb_test_pwd"
$env:HBNB_MYSQL_HOST = "localhost"
$env:HBNB_MYSQL_DB = "hbnb_test_db"
$env:HBNB_TYPE_STORAGE = "db"

python -m unittest discover tests

Write-Host "`nTests completed!" -ForegroundColor Green
