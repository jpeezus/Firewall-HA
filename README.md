This is a sample script that automatically enables/disables firewalls based on the average number of sessions across all running firewalls. 

The script requires a number of inputs including, clientid, client secret, directory id which needs to be setup in AD. For instructions on how to set this up please see: 
"Create an Azure Active Directory application" in (https://docs.microsoft.com/en-us/azure/azure-resource-manager/resource-group-create-service-principal-portal)

In addition the script needs the Resource Group name that the VM's have been deployed in. Last the script requires the API Key for querying the sessions from the firewalls. 
