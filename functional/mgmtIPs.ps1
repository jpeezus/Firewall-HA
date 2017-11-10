$secpasswd = ConvertTo-SecureString "" -AsPlainText -Force
$mycreds = New-Object System.Management.Automation.PSCredential ('', $secpasswd)
Login-AzureRmAccount -ServicePrincipal -Tenant 72f988bf-86f1-41af-91ab-2d7cd011db47 -Credential $mycreds
##
$pubIPs = Get-AzureRmPublicIpAddress -ResourceGroupName 'existingTempalte_api'
$mgmtpubIPs = $pubIPs | ?{$_.name -like 'mgmt*'}
$mgmtpubIPs.IPAddress