$desktop = [Environment]::GetFolderPath('Desktop')
$godot = Join-Path $desktop 'Godot_v4.6.2-stable_win64.exe'

if (-not (Test-Path $godot)) {
    Write-Host 'Godot executable not found:'
    Write-Host $godot
    pause
    exit 1
}

Start-Process -FilePath $godot -ArgumentList @('--path', 'C:\Users\rysla\AnfisaVPN')
