# # pip install O365
# from O365 import Account

# credentials = ('client_id', 'client_secret')

# account = Account(credentials)
# m = account.new_message()
# m.to.add('to_example@example.com')
# m.subject = 'Testing!'
# m.body = "George Best quote: I've stopped drinking, but only while I'm asleep."
# m.send()


# # python -m pip install --upgrade pip
# # pip install shareplum
from shareplum import Site
from shareplum import Office365
from shareplum.site import Version
from requests_ntlm import HttpNtlmAuth

# # Office 365

# auth = Office365('https://arizonastateu.sharepoint.com/adfs/', username='mbuchan7@sundevils.asu.edu', password='').GetCookies()
# site = Site('https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom/', authcookie=auth)
# sp_list = site.List('list name')
# data = sp_list.GetListItems('All Items', rowlimit=200)

# REST API

auth = Office365('https://arizonastateu.sharepoint.com/adfs', username='mbuchan7@sundevils.asu.edu', password='').GetCookies()
site = Site('https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom/', version=Version.v365 , authcookie=auth)

new_list = site.List('My New List')
sp_data = new_list.GetListItems()


# # Other

# from office365.runtime.auth.authentication_context import AuthenticationContext
# from office365.sharepoint.client_context import ClientContext

# url= "https://login.microsoftonline.com/login.srf"
# ctx_auth = AuthenticationContext(url)
# if ctx_auth.acquire_token_for_user('mbuchan7@sundevils.asu.edu', ''):
#   ctx = ClientContext(url, ctx_auth)
#   web = ctx.web
#   ctx.load(web)
#   ctx.execute_query()
#   print ("Web title: {0}".format(web.properties['Title']))

# else:
#     print("NOPE")
#     print (ctx_auth.get_last_error())



# import json

# from office365.runtime.auth.authentication_context import AuthenticationContext
# from office365.runtime.client_request import ClientRequest
# from office365.runtime.utilities.request_options import RequestOptions

# tenant_url= "https://login.microsoftonline.com/login.srf"
# ctx_auth = AuthenticationContext(tenant_url)

# site_url="https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom/"

# if ctx_auth.acquire_token_for_user("mbuchan7@sundevils.asu.edu","Fh232tAK%2"):
#   request = ClientRequest(ctx_auth)
#   options = RequestOptions("{0}/_api/web/".format(site_url))
#   options.set_header('Accept', 'application/json')
#   options.set_header('Content-Type', 'application/json')
#   data = request.execute_request_direct(options)
#   s = json.loads(data.content)
#   web_title = s['Title']
#   print("Web title: " + web_title)
# else:
#   print(ctx_auth.get_last_error())