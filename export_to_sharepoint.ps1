#~ SharePoint Links
$listName = 'Capstone EULA Test'
$rootSite = "https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom"
#$listSite = "/Lists/Capstone%20EULA%20Test%20List/AllItems.aspx"

# Stores CSV contents to a variable.
$csv_file = '.\xlsx_dump.csv'

#Add items to SP list (FUNCTIONING)

Function New-SPListItem([string]$csvInfo){
    #~ Add New List Item
    Connect-PnPOnline -Url $rootSite -UseWebLogin | Out-Null
    $list = Get-PnPList -Identity $listName    
    Import-CSV $csvInfo | ForEach-Object{
        echo $_.'software name' #Shows software name being added to list
        #Sharepoint field names not the same as displayed. Go to gear at top right > list settings > click field > look at end of URL
        Add-PnPListItem -List $list -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $_.'licensing restrictions'}
       }
    Get-PnPListItem $list
}

New-SPListItem($csv_file)