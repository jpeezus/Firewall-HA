
$array = 40,50
$average = $array | measure -Average
if ($average.Average -le 40){
$VMs = Get-AzureRmVM -ResourceGroupName 'existingtempalte_api' -Status | ?{$_.name -like 'VM-Series*'}
$onVMs = $VMs | ?{$_.PowerState -like '*running*'}
$onVMs[0] | Stop-AzureRmVM -Force
}
if ($average.Average -ge 60){
$VMs = Get-AzureRmVM -ResourceGroupName 'existingtempalte_api' -Status | ?{$_.name -like 'VM-Series*'}
$offVMs = $VMs | ?{$_.PowerState -like '*deallocated*'}
$offVMs[0] | Start-AzureRmVM
}