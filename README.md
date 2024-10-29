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