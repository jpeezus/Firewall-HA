Function GetActiveSessions($ip){
    $apiKey = $env:apiKey
    $firewall_cmd = "<show><system><state><filter>sw.mprelay.s1.dp0.stats.session</filter></state></system></show>"
    $concatUrl = "https://$ip/api/?type=op&cmd=$firewall_cmd&key=$apiKey"
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = { $True }
    [System.Net.ServicePointManager]::SecurityProtocol =  'tls12'
    $url = $concatUrl
    $apiReq = [System.Net.HttpWebRequest]::CreateHttp($url)
    $apiRes = $apiReq.GetResponse() 
    $respstream = $apiRes.GetResponseStream(); 
    $sr = new-object System.IO.StreamReader $respstream; 
    $result = $sr.ReadToEnd(); 
    $option = [System.StringSplitOptions]::RemoveEmptyEntries
    $result = $result.split('{')[1].split(',')[1].split(': ', $option)[1];
    return $result; 
}

Function Scale($noOfActiveSessions){
    if ($NoOfActiveSessions -le $env:minThreashhold -and $vmCount -gt 2) {
        $VMs = Get-AzureRmVM -ResourceGroupName $env:resourceGroup -Status | ?{$_.name -like 'VM-Series*'}
        $onVMs = $VMs | ?{$_.PowerState -like '*running*'}
        $onVMs[0] | Stop-AzureRmVM -Force
        Write-Ouput "Scaling DOWN!"
    }
    elseif($noOfActiveSessions -gt $env:maxThreashhold -and $vmCount -lt 10) {
        $VMs = Get-AzureRmVM -ResourceGroupName $env:resourceGroup -Status | ?{$_.name -like 'VM-Series*'}
        $offVMs = $VMs | ?{$_.PowerState -like '*deallocated*'}
        $offVMs[0] | Start-AzureRmVM
        Write-Ouput "Scaling UP!";
    }
    else {
        Write-Output "Nothing to scale with average session: $noOfActiveSessions"
    }
}

Write-Output "Firewall HA Script started at:$(get-date)";
Try {
    $password = ConvertTo-SecureString $env:clientsecret -AsPlainText -Force
    $credential = New-Object System.Management.Automation.PSCredential ($env:clientid, $password)
    Add-AzureRmAccount -ServicePrincipal -Tenant $env:tenantid -Credential $credential
    $context = Get-AzureRmContext
    Set-AzureRmContext -Context $context
    $pubIPs = Get-AzureRmPublicIpAddress -ResourceGroupName 'wedPARG'
    $mgmtpubIPs = $pubIPs | ?{$_.name -like 'mgmtip*'}
    $vmCount = 0;
    $totalNumberOfSessions = 0;
    foreach ($ip in $mgmtpubIPs.IPAddress) {
        $vmCount++;
        $res = GetActiveSessions($ip);
        $totalNumberOfSessions += $res;
        write-output("Active sessions for IP: $ip is $res");
    }
    $averageNumberOfSessions = $totalNumberOfSessions / $vmCount;
    Scale($averageNumberOfSessions);
}
Catch {
    Write-Output "Oh no.. Something went wrong: $_.Exception.Message `n $_.Exception.InnerExecption"        
}
Finally {
    [System.Net.ServicePointManager]::ServerCertificateValidationCallback = $null
}