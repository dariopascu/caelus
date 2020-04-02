import logging
from typing import Union
import boto3


class AWSSecurity(object):
    _aws_logger = logging.getLogger('aws')

    def __init__(self, session: boto3.session):
        self.sts_client = session.client('sts')

        self._caller_identity = self.sts_client.get_caller_identity()

    @property
    def account_number(self):
        return self._caller_identity.get('Account')

    @property
    def user_name(self):
        return self._caller_identity.get('Arn').split('/')[-1]

    @staticmethod
    def get_mfa_token():
        mfa_token = input("Enter the MFA code: ")

        return mfa_token

    def assume_role(self, role_arn: str, session_name: str, session_duration: int,
                    mfa_serial_number: Union[None, str] = None):
        role_info = dict(RoleArn=role_arn,
                         RoleSessionName=session_name,
                         DurationSeconds=session_duration)

        if mfa_serial_number is not None:
            mfa_token = self.get_mfa_token()
            role_info.update(dict(SerialNumber=mfa_serial_number,
                                  TokenCode=mfa_token))

        role_credentials = self.sts_client.assume_role(**role_info)

        return role_credentials
