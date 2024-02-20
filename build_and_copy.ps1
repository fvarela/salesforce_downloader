# Delete the .\build and .\dist folders if they exist
$buildPath = ".\build"
$distPath = ".\dist"

if (Test-Path $buildPath) {
    Remove-Item -Path $buildPath -Recurse -Force
}

if (Test-Path $distPath) {
    Remove-Item -Path $distPath -Recurse -Force
}

# Run pyinstaller to create the executable from run.py, suppressing command output
pyinstaller --name salesforce_data_exporter .\run.py *>$null

# Check if the ./dist/run/config_files directory exists, if not, create it
$distConfigPath = ".\dist\salesforce_data_exporter\config_files"
if (-not (Test-Path $distConfigPath)) {
    New-Item -ItemType Directory -Path $distConfigPath
}

# Copy the config.yaml file into the newly created directory
$sourceConfig = ".\config_files\config.yaml"
$destinationConfig = ".\dist\salesforce_data_exporter\config_files\config.yaml"
Copy-Item -Path $sourceConfig -Destination $destinationConfig

Write-Output "PyInstaller build complete, and config.yaml has been copied to $distConfigPath"
