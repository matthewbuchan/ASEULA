﻿#~ SharePoint Links
Import-Module WebAdministration
$listName = 'Capstone EULA Test'
$rootSite = "https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom"
#$listSite = "/Lists/Capstone%20EULA%20Test%20List/AllItems.aspx"

# Stores CSV contents to a variable.
$csv_file = '.\xlsx_dump.csv'

#Add items to SP list (FUNCTIONING)

Function Check-SPListItem([string]$csvInfo){
    #~ Add New List Item
    Connect-PnPOnline -Url $rootSite -UseWebLogin
    $list = Get-PnPList -Identity $listName
    $splist = @{}
    Get-PnPListItem $list -Fields "Id","Title" | ForEach-Object{
    $splist.Add($_['Title'],$_.Id)
    }
    Import-CSV $csvInfo | ForEach-Object{        
        $choiceitems = $_.'licensing restrictions'.replace(";#",", ")
        if ( $splist.ContainsKey($_.'software name')){
            $spitem = Set-PnPListItem -List $list -Identity $splist[$_.'software name'] -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $choiceitems}
            $spitem.update($true)
            }
        else{            
            Add-PnPListItem -List $list -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $choiceitems}
            }
        }
    Disconnect-PnPOnline
}
Check-SPListItem($csv_file)