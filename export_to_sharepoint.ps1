#~ SharePoint Links
$listName = 'Capstone EULA Test'
$rootSite = "https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom"
#$listSite = "/Lists/Capstone%20EULA%20Test%20List/AllItems.aspx"

# Stores CSV contents to a variable.
$csv_file = '.\xlsx_dump.csv'

#Add items to SP list (FUNCTIONING)

Function Check-SPListItem([string]$csvInfo){    
    Connect-PnPOnline -Url $rootSite -UseWebLogin
    $list = Get-PnPList -Identity $listName
    $splist = @{}
    Get-PnPListItem $list -Fields "Id","Title" | ForEach-Object{
        $splist.Add($_['Title'],$_.Id)
    }
    Import-CSV $csv_file | ForEach-Object{    
        $choiceitems = $_.'licensing restrictions' -split ';#'
        
        #~ Update Existing List Item
        if ( $splist.ContainsKey($_.'software name')){
            Set-PnPListItem -List $list -Identity $splist[$_.'software name'] -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $choiceitems}
            }
        #~ Add New List Item
        else{
            Add-PnPListItem -List $list -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $choiceitems}
            }
        }
    Disconnect-PnPOnline
}
Check-SPListItem($csv_file)