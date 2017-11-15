Write-Output "PowerShell Timer trigger function executed at:$(get-date)";
$secpasswd = ConvertTo-SecureString "KUPH+p3yKl6nNZfXAFVVN8IFxED1HDqHI/mVCJb8W9A=" -AsPlainText -Force
$mycreds = New-Object System.Management.Automation.PSCredential ('eb6b5fca-3303-4214-bb1d-b1193c23a826', $secpasswd)
Login-AzureRmAccount -ServicePrincipal -Tenant 72f988bf-86f1-41af-91ab-2d7cd011db47 -Credential $mycreds
##todo poll blob storage for latest metric metric into array variable
#get-content
$array = 40,30
$average = $array | measure -Average
if ($average.Average -le 40){
$VMs = Get-AzureRmVM -ResourceGroupName 'e2einfandFunc' -Status | ?{$_.name -like 'VM-Series*'}
$onVMs = $VMs | ?{$_.PowerState -like '*running*'}
$onVMs[0] | Stop-AzureRmVM -Force
}
if ($average.Average -ge 60){
$VMs = Get-AzureRmVM -ResourceGroupName 'e2einfandFunc' -Status | ?{$_.name -like 'VM-Series*'}
$offVMs = $VMs | ?{$_.PowerState -like '*deallocated*'}
$offVMs[0] | Start-AzureRmVM
}