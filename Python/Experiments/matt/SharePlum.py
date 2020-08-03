# pip install O365
from O365 import Account

credentials = ('client_id', 'client_secret')

account = Account(credentials)
m = account.new_message()
m.to.add('to_example@example.com')
m.subject = 'Testing!'
m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
m.send()


# # python -m pip install --upgrade pip
# # pip install shareplum
# from shareplum import Site
# from shareplum import Office365
# from shareplum.site import Version
# from requests_ntlm import HttpNtlmAuth

# # Office 365

# auth = Office365('https://arizonastateu.sharepoint.com/', username='mbuchan7@sundevils.asu.edu', password='Fh232tAK%2').GetCookies()
# site = Site('https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom/', authcookie=auth)
# sp_list = site.List('list name')
# data = sp_list.GetListItems('All Items', rowlimit=200)


# # REST API

# auth = Office365('https://arizonastateu.sharepoint.com', username='mbuchan7@sundevils.asu.edu', password='Fh232tAK%2').GetCookies()
# site = Site('https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom/', version=Version.v365 , authcookie=auth)

# new_list = site.List('My New List')
# sp_data = new_list.GetListItems()