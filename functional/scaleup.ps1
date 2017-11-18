﻿#login
$secpasswd = ConvertTo-SecureString "" -AsPlainText -Force
$mycreds = New-Object System.Management.Automation.PSCredential ('', $secpasswd)
Login-AzureRmAccount -ServicePrincipal -Tenant 72f988bf-86f1-41af-91ab-2d7cd011db47 -Credential $mycreds
#scale-up
$VMs = Get-AzureRmVM -ResourceGroupName 'existingtempalte_api' -Status | ?{$_.name -like 'VM-Series*'}
$offVMs = $VMs | ?{$_.PowerState -like '*deallocated*'}
$offVMs[0] | Start-AzureRmVM