# Installation

Use pip:

```
pip install py_mssso
```
or

```
pip install git+https://github.com/shineum/py_mssso.git
```


# Prerequisites
Create Azure App with MS Azure Protal "App registrations".
These information from Azure App are required.
- Directory (tenant) ID (Overview)
- Application (client) ID (Overview)
- Client secret (Manage - Certificates & secrets)
- scopes (Manage - API permissions)
- redirect url (Manage - Authentication - Web Redirect URIs)


# Getting Started
```
from py_mssso import MSSSOHelper

...

MSSSOHelper.add(
    **{
        "tenant_type": MS_SSO_TENANT_TYPE,
        "tenant_id": MS_SSO_TENANT_ID,
        "client_id": MS_SSO_CLIENT_ID,
        "client_secret": MS_SSO_CLIENT_SECRET,
        "scopes": MS_SSO_SCOPES,
        "redirect_url": MS_SSO_REDIRECT_URL,
    }
)
```

#### tenant_type
```
"SINGLE", "MULTI" or "PUBLIC" - default: "SINGLE"
```

#### scopes
```
["User.Read"]: Read user data only for login user
["User.Read.All"]: when you need to read other user's information (ex: manager of login user)
```

#### redirect_url
```
url must be set in Web Redirect URIs in Azure App
```


# login url
django example
```
# view.py
from py_mssso import MSSSOHelper

...

# sso login
def sso_login(request):
    if not request.session.session_key:
        request.session.create()
    request.session["msal_flow"] = MSSSOHelper.get().get_auth_code_flow()
    request.session.save()
    return HttpResponseRedirect(request.session["msal_flow"].get("auth_uri"))
```


# callback url
django example
```
# view.py
import requests
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.http import HttpResponseRedirect
from py_mssso import MSSSOHelper

_LOGIN_FAIL_URL = "/"
_LOGIN_SUCCESS_URL = "/"
_MSGRAPH_BASE_URI = "https://graph.microsoft.com/v1.0"
_MSGRAPH_QUERY_SELECT_ITEMS_FOR_USER = ",".join(
    [
        "displayName",
        "givenName",
        "surname",
        "mail",
        "mobilePhone",
        "officeLocation",
        "userPrincipalName",
        "jobTitle",
        "department",
        "companyName",
        "onPremisesSamAccountName",
    ]
)

...

# django login helper
def _login(request, username):
    try:
        user = get_user_model().objects.get(username=username)
        user.backend = "django.contrib.auth.backends.ModelBackend"
        login(request, user)
    except:
        raise Exception(f"Login Failed - user not exist: [{username}]")

# sso callback
def sso_login_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")
    session_state = request.GET.get("session_state")
    msal_flow = request.session.get("msal_flow")

    try:
        # request validation
        if not code:
            raise Exception("Invalid request")

        # get token info
        token_info = MSSSOHelper.get().get_token_info(
            auth_code_flow=msal_flow,
            auth_res={
                "code": code,
                "state": state,
                "session_state": session_state,
            },
        )

        # token info validation
        if not token_info:
            raise Exception("Invalid request")

        # find token
        token = token_info.get("access_token")

        # token validation
        if not token:
            raise Exception("Invalid request")

        # set request header
        headers = {"Authorization": f"Bearer {token}"}

        # get user data with MS Graph API
        res_user = requests.get(
            f"{_MSGRAPH_BASE_URI}/me?$select={_MSGRAPH_QUERY_SELECT_ITEMS_FOR_USER}",
            headers=headers,
        )

        # get manager data with MS Graph API (Optional, "User.Read.All" permission is required)
        res_manager = requests.get(
            f"{_MSGRAPH_BASE_URI}/me/manager?$select={_MSGRAPH_QUERY_SELECT_ITEMS_FOR_USER}",
            headers=headers,
        )

        ##############################################
        # Run some processes with user / manager data
        # ex) create (django) user if not exist
        #     or update profile if necessary
        ##############################################

        # django login
        # set username with res_user - it can be "userPrincipalName" or "onPremisesSamAccountName" depending on your settings
        _login(request, username)
    except:
        return HttpResponseRedirect(_LOGIN_FAIL_URL)

    return HttpResponseRedirect(_LOGIN_SUCCESS_URL)
```