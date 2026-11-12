param([Parameter(ValueFromRemainingArguments=$true)][string[]]$StudioArgs)
$ErrorActionPreference='Continue'
$root='D:/vibe/learn_draw_studio/evidence/studio-endpoints/usability'
$command='> python -m scripts.studio '+($StudioArgs -join ' ')
$command | Add-Content "$root/commands.log"
$result=& D:/vibe/learn_draw_studio/.venv/Scripts/python.exe -m scripts.studio @StudioArgs 2>&1
$code=$LASTEXITCODE
$result | Add-Content "$root/commands.log"
('exit='+$code) | Add-Content "$root/commands.log"
Write-Output $command
Write-Output ('exit='+$code)
if ($code -ne 0) {Write-Output $result}
