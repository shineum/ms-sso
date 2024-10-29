import msal
from msal.authority import AuthorityBuilder, AZURE_PUBLIC


_MSALInstanceMap = {}


class _MSALInstance:
    _auth = None
    _scopes = None
    _redirect_url = None

    def __init__(self, **kwargs):
        """
        required keywords -
        tenant_type: ("SINGLE" or "MULTI"),
        tenant_id,
        client_id,
        client_secret,
        scopes,
        redirect_url
        """
        tenant_type = kwargs.get("tenant_type", "SINGLE")
        tenant_id = kwargs.get("tenant_id", None)
        client_id = kwargs.get("client_id", None)
        client_secret = kwargs.get("client_secret", None)

        self._scopes = kwargs.get("scopes", None)
        self._redirect_url = kwargs.get("redirect_url", None)

        try:
            if tenant_type == "PUBLIC":
                self._auth = msal.PublicClientApplication(**{"client_id": client_id})
            elif tenant_type == "MULTI":
                self._auth = msal.ClientApplication(
                    **{"client_id": client_id, "client_credential": client_secret}
                )
            else:
                self._auth = msal.ConfidentialClientApplication(
                    **{
                        "client_id": client_id,
                        "client_credential": client_secret,
                        "authority": AuthorityBuilder(AZURE_PUBLIC, tenant_id),
                    }
                )

        except Exception as e:
            self._auth = None
            raise Exception("MS SSO Configuration: Init Value Error")

    def get_auth(self):
        if not self._auth:
            raise Exception("MS SSO Configuration: Not Initialized")
        return self._auth

    def get_auth_code_flow(self):
        return self._auth.initiate_auth_code_flow(
            scopes=self._scopes,
            redirect_uri=self._redirect_url,
        )

    def get_token_info(self, auth_code_flow, auth_res):
        return self.get_auth().acquire_token_by_auth_code_flow(
            auth_code_flow=auth_code_flow, auth_response=auth_res
        )

    def get_accounts(self, username=None):
        return self.get_auth().get_accounts(username)


class MSSSOHelper:

    @staticmethod
    def add(name="default", **kwargs):
        _MSALInstanceMap[name] = _MSALInstance(**kwargs)

    @staticmethod
    def get(name="default"):
        if name in _MSALInstanceMap:
            return _MSALInstanceMap[name]
        else:
            raise Exception("Not Initialized")
