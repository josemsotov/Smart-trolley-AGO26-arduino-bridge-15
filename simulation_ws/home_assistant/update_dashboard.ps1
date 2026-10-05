param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$tokenPath = 'C:\Users\cools\Desktop\long lived token HA-VS CODE.txt'
$ws = [System.Net.WebSockets.ClientWebSocket]::new()
$deadline = [System.Threading.CancellationTokenSource]::new(60000)
function Receive-Json {
    $buffer = New-Object byte[] 65536
    $stream = [System.IO.MemoryStream]::new()
    do {
        $segment = [ArraySegment[byte]]::new($buffer)
        $result = $ws.ReceiveAsync($segment, $deadline.Token).GetAwaiter().GetResult()
        if ($result.MessageType -eq [System.Net.WebSockets.WebSocketMessageType]::Close) { throw 'Home Assistant closed connection' }
        $stream.Write($buffer, 0, $result.Count)
    } until ($result.EndOfMessage)
    $json = [Text.Encoding]::UTF8.GetString($stream.ToArray())
    $stream.Dispose()
    return ($json | ConvertFrom-Json)
}
function Send-Json($payload) {
    $bytes = [Text.Encoding]::UTF8.GetBytes(($payload | ConvertTo-Json -Depth 100 -Compress))
    $ws.SendAsync([ArraySegment[byte]]::new($bytes), [System.Net.WebSockets.WebSocketMessageType]::Text, $true, $deadline.Token).GetAwaiter().GetResult() | Out-Null
}
function Command($payload) {
    Send-Json $payload
    do { $reply = Receive-Json } until ($reply.id -eq $payload.id)
    if (!$reply.success) { throw "HA command failed: $($reply.error.code) $($reply.error.message)" }
    return $reply.result
}
try {
    $ws.ConnectAsync([Uri]'ws://homeassistant.local:8123/api/websocket', $deadline.Token).GetAwaiter().GetResult() | Out-Null
    $hello = Receive-Json
    $token = [IO.File]::ReadAllText($tokenPath).Trim()
    Send-Json @{type='auth'; access_token=$token}
    $token = $null
    $auth = Receive-Json
    if ($auth.type -ne 'auth_ok') { throw 'Home Assistant rejected the token' }
    $config = Command @{id=1; type='lovelace/config'; url_path='smart-trolley'}
    $backupDir = Join-Path ([Environment]::GetFolderPath('LocalApplicationData')) 'SmartTrolley\ha-backups'
    [IO.Directory]::CreateDirectory($backupDir) | Out-Null
    $backup = Join-Path $backupDir ('smart-trolley-' + (Get-Date -Format 'yyyyMMdd-HHmmss') + '.json')
    [IO.File]::WriteAllText($backup, ($config | ConvertTo-Json -Depth 100), [Text.UTF8Encoding]::new($false))
    Write-Output "Backup: $backup"
    for ($i=0; $i -lt $config.views.Count; $i++) {
        $v=$config.views[$i]
        Write-Output "View $i title=$($v.title) type=$($v.type) cards=$(@($v.cards).Count) sections=$(@($v.sections).Count)"
    }
    if ($config.strategy.type -eq 'iframe') {
        Write-Output "Strategy type=iframe url=$($config.strategy.url)"
    }
    if (!$Apply) { return }
    if ($config.strategy.type -eq 'iframe') {
        $canonicalUrl = 'http://192.168.40.74:8080/?v=elp-live-20261005'
        if ($config.strategy.url.TrimEnd('/') -notin @(
            'http://192.168.40.74:8080',
            'http://192.168.40.74:8080/?v=slam-map-20260909',
            'http://192.168.40.74:8080/?v=unified-interface-20261002',
            'http://192.168.40.74:8080/?v=unified-interface-20261005',
            'http://192.168.40.74:8080/?v=elp-camera-20261005',
            $canonicalUrl
        )) {
            throw 'Unexpected embedded interface URL; inspect before changing'
        }
        $config.strategy.url = $canonicalUrl
        Command @{id=2; type='lovelace/config/save'; url_path='smart-trolley'; config=$config} | Out-Null
        $verified=Command @{id=3; type='lovelace/config'; url_path='smart-trolley'}
        if ($verified.strategy.url -ne $config.strategy.url) { throw 'Dashboard verification failed' }
        Write-Output "Home Assistant now embeds the canonical Fairway OS interface: $canonicalUrl"
        return
    }
    $view = $config.views[0]
    $url='http://192.168.40.74:8080/static/map.html'
    if (($config | ConvertTo-Json -Depth 100).Contains($url)) { Write-Output 'Map already present'; return }
    if ($view.type -eq 'panel') { throw 'Panel layout requires review before inserting a card' }
    $card = [pscustomobject]@{type='iframe'; title='Mapa del robot'; url=$url; aspect_ratio='75%'}
    if ($view.type -eq 'sections') {
        $section=[pscustomobject]@{type='grid'; cards=@($card)}
        $view.sections = @($view.sections) + @($section)
    } else {
        $view | Add-Member -NotePropertyName cards -NotePropertyValue (@($view.cards) + @($card)) -Force
    }
    Command @{id=2; type='lovelace/config/save'; url_path='smart-trolley'; config=$config} | Out-Null
    $verified=Command @{id=3; type='lovelace/config'; url_path='smart-trolley'}
    if (!(($verified | ConvertTo-Json -Depth 100).Contains($url))) { throw 'Saved map card not found on verification' }
    Write-Output 'Map card saved and verified in smart-trolley'
} finally {
    $ws.Dispose()
    $deadline.Dispose()
}
