$secpasswd = ConvertTo-SecureString "KUPH+p3yKl6nNZfXAFVVN8IFxED1HDqHI/mVCJb8W9A=" -AsPlainText -Force
$mycreds = New-Object System.Management.Automation.PSCredential ('eb6b5fca-3303-4214-bb1d-b1193c23a826', $secpasswd)
Login-AzureRmAccount -ServicePrincipal -Tenant '72f988bf-86f1-41af-91ab-2d7cd011db47' -Credential $mycreds
##
$pubIPs = Get-AzureRmPublicIpAddress -ResourceGroupName 'e2einfandFunc'
$mgmtpubIPs = $pubIPs | ?{$_.name -like 'mgmt*'}
ConvertTo-Json -InputObject $mgmtpubIPs | Out-File -
#something
#to-do define imperative storage output/input for powershell functions