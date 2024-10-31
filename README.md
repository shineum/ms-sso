# Installation

Use pip:

```
pip install py-mssso
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
from django.http import HttpResponseRedirect

...

# sso login
def sso_login(request):
    if not request.session.session_key:
        request.session.create()
    msal_flow = MSSSOHelper.get().get_auth_code_flow()
    request.session["msal_flow"] = msal_flow
    request.session.save()
    return HttpResponseRedirect(msal_flow.get("auth_uri"))
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
    msal_flow = request.session.get("msal_flow")

    try:
        # get token
        token = MSSSOHelper.get().get_token(
            auth_code_flow=msal_flow,
            auth_res=request.GET,
        )

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

        # parse user object
        ms_user_obj = res_user.json()

        # set username - it could be "userPrincipalName", "onPremisesSamAccountName" or any other values depending on your settings
        username = ms_user_obj.get("userPrincipalName")
        if not username:
            raise Exception("Invalid User")

        # create or update django user
        get_user_model().objects.update_or_create(
            username=username,
            defaults={
                "first_name": ms_user_obj.get("givenName"),
                "last_name": ms_user_obj.get("surname"),
                "email": ms_user_obj.get("mail"),
                "is_active": True,
            },
        )

        # django login
        _login(request, username)
    except:
        return HttpResponseRedirect(_LOGIN_FAIL_URL)

    return HttpResponseRedirect(_LOGIN_SUCCESS_URL)
```

# sample project
```
https://github.com/shineum/py_mssso_sample
```
