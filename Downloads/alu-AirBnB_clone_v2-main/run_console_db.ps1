# PowerShell script to run console with DBStorage
# Usage: .\run_console_db.ps1

Write-Host "Starting AirBnB Console with DBStorage (MySQL)..." -ForegroundColor Green

$env:HBNB_MYSQL_USER = "hbnb_dev"
$env:HBNB_MYSQL_PWD = "hbnb_dev_pwd"
$env:HBNB_MYSQL_HOST = "localhost"
$env:HBNB_MYSQL_DB = "hbnb_dev_db"
$env:HBNB_TYPE_STORAGE = "db"

python console.py
