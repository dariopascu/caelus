import logging

from google.oauth2 import service_account


class GCPAuth(object):
    _gcp_logger = logging.getLogger('gcp')

    def __init__(self, project_id: str = None, credentials_file: str = None, account_info: str = None):
        self._project_id = project_id

        if credentials_file is not None:
            self._credential = service_account.Credentials.from_service_account_file(credentials_file)

        elif account_info is not None:
            self._credential = service_account.Credentials.from_service_account_info(info=account_info)

    @property
    def project_id(self):
        return self._project_id

    @property
    def credential(self):
        return self._credential
