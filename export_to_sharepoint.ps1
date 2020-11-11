#~ SharePoint Links
$listName = 'Capstone EULA Test'
$rootSite = "https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom"
#$listSite = "/Lists/Capstone%20EULA%20Test%20List/AllItems.aspx"

# Stores CSV contents to a variable.
$csv_file = '.\xlsx_dump.csv'

#Add items to SP list (FUNCTIONING)

Function Check-SPListItem([string]$csvInfo){
    #~ Add New List Item
    Connect-PnPOnline -Url $rootSite -UseWebLogin | Out-Null
    $list = Get-PnPList -Identity $listName
    $splist = @{}
    Get-PnPListItem $list -Fields "Id","Title" | ForEach-Object{
    $splist.Add($_['Title'],$_.Id)
    }    
    Import-CSV $csvInfo | ForEach-Object{        
        if ( $splist.ContainsKey($_.'software name')){            
            Set-PnPListItem -List $list -Identity $splist[$_.'software name'] -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $_.'licensing restrictions'}
            }
        else{            
            Add-PnPListItem -List $list -Values @{"Title"= $_.'software name'; "PublisherName"= $_.'publisher name'; "InformationWebpage"= $_.'information webpage'; "LicensingRestrictions"= $_.'licensing restrictions'}
            }
        }
}
Check-SPListItem($csv_file)


#Get from Fulton List Work in Progress
Function Get-SPListItem(){
    $listName = 'Software'
    $rootSite = "https://arizonastateu.sharepoint.com/sites/Fulton/ETS/sysmgmt/software"
    Connect-PnPOnline -Url $rootSite -UseWebLogin | Out-Null
    $list= Get-PnPList -Identity $listName
    
    Get-PnPListItem $list -Fields "Title","Publisher","Information_x0020_Webpage","License_x0020_Restrictions"
}

