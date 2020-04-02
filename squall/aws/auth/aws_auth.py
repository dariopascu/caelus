import logging
from typing import Union
import boto3

from squall.aws.users import AWSIdentity
from squall.aws.users import AWSSecurity


class AWSAuth(object):
    _aws_logger = logging.getLogger('aws')

    def __init__(self, key: Union[None, str] = None, secret_key: Union[None, str] = None,
                 profile_name: Union[None, str] = None, region_name: Union[None, str] = None):
        self._key = key
        self._secret_key = secret_key
        self._profile_name = profile_name
        self._region_name = region_name

        self._session = boto3.Session(aws_access_key_id=key, aws_secret_access_key=secret_key,
                                      profile_name=profile_name, region_name=region_name)

    @property
    def profile_name(self) -> str:
        return self._profile_name

    @property
    def region_name(self) -> str:
        return self._region_name

    @property
    def session(self):
        return self._session

    @session.setter
    def session(self, new_session):
        self._session = new_session


class AWSDelegatedAuth(AWSAuth):
    SESSION_DURATION = 3600  # session duration in seconds

    def __init__(self, policy_name: str, use_mfa: bool = True, session_name: str = 'temp_session',
                 key: Union[None, str] = None, secret_key: Union[None, str] = None,
                 profile_name: Union[None, str] = None, region_name: Union[None, str] = None):
        AWSAuth.__init__(self, key, secret_key, profile_name, region_name)

        self._use_mfa = use_mfa
        self._policy_name = policy_name
        self._session_name = session_name

        self.session = self.delegated_session

    @property
    def policy_name(self):
        return self._policy_name

    @property
    def use_mfa(self):
        return self._use_mfa

    @property
    def session_name(self):
        return self._session_name

    @property
    def delegated_session(self):
        sts = AWSSecurity(self.session)
        iam = AWSIdentity(self.session, sts.user_name)
        group_name = iam.get_group_names()[0]
        policy_statement = iam.get_group_policy_statement(group_name, self.policy_name)
        delegated_arn = policy_statement[0].get('Resource')[0]

        mfa_serial_number = None
        if self.use_mfa:
            mfa_serial_number = iam.get_mfa_serial_numbers()[0]

        assumed_role = sts.assume_role(role_arn=delegated_arn, session_name=self.session_name,
                                       session_duration=self.SESSION_DURATION,
                                       mfa_serial_number=mfa_serial_number)

        role_credentials = assumed_role.get('Credentials')

        delegated_session = boto3.Session(aws_access_key_id=role_credentials.get('AccessKeyId'),
                                          aws_secret_access_key=role_credentials.get('SecretAccessKey'),
                                          aws_session_token=role_credentials.get('SessionToken'),
                                          region_name=self.region_name, profile_name=self.profile_name)

        return delegated_session
