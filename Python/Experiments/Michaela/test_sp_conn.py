from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext

ctx_auth = AuthenticationContext("https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom")
if ctx_auth.acquire_token_for_user("mdpawlow", ""):
    ctx = ClientContext("https://arizonastateu.sharepoint.com/sites/O365FSEETSClassroom", ctx_auth)
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print("Web Title: {0}".format(web.properties['Title']))
else:
    print(ctx_auth.get_last_error())