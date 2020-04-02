from typing import Union

from azure.core.exceptions import ClientAuthenticationError
from azure.common.credentials import ServicePrincipalCredentials


class AzureAuth(object):

    def __init__(self, tenant_id: Union[None, str] = None, client_id: Union[None, str] = None,
                 client_secret: Union[None, str] = None, resource: Union[None, str] = None,
                 access_key: Union[None, str] = None, connection_string: Union[None, str] = None):
        arguments = locals()
        arguments_values = list(arguments.values())

        self._tenant_id = tenant_id
        self._client_id = client_id
        self._client_secret = client_secret
        self._resource = resource

        self._service_principal_token = None
        self._key_token = None
        self._connection_string_token = None

        if not any(arguments_values):
            # Authenticating with DefaultAzureCredential
            raise ClientAuthenticationError('Some credentials are required')
        elif access_key:
            # Authenticating a service principal with a client secret
            self._key_token = access_key
        elif connection_string:
            # Authenticating a service principal with a certificate
            self._connection_string_token = connection_string
        elif None not in (tenant_id, client_id, client_secret, resource):
            # Authenticating a service principal with a client secret
            self._credential = ServicePrincipalCredentials(
                client_id=self._client_id,
                secret=self._client_secret,
                tenant=self._tenant_id,
                resource=self._resource
            )
            self._service_principal_token = self._credential.token["access_token"]
        else:
            # Authenticating with DefaultAzureCredential
            raise ClientAuthenticationError('Some credentials are required')

    @property
    def key_token(self) -> str:
        return self._key_token

    @property
    def connection_string_token(self) -> str:
        return self._connection_string_token

    @property
    def service_principal_token(self) -> str:
        return self._service_principal_token

    @property
    def tenant_id(self) -> str:
        return self._tenant_id

    @property
    def client_id(self) -> str:
        return self._client_id

    @property
    def client_secret(self) -> str:
        return self._client_secret

    @property
    def resource(self) -> str:
        return self._resource

    @property
    def credential(self):
        return self._credential
