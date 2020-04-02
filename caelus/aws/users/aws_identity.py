import logging

import boto3


class AWSIdentity(object):
    _aws_logger = logging.getLogger('aws')

    def __init__(self, session: boto3.Session, user_name: str):
        self._user_name = user_name

        self.iam_client = session.client('iam')

    @property
    def user_name(self):
        return self._user_name

    def list_user_groups(self):
        groups_list = self.iam_client.list_groups_for_user(UserName=self.user_name).get('Groups')
        return groups_list

    def get_group_names(self):
        group_names = []
        group_list = self.list_user_groups()
        for group in group_list:
            group_names.append(group.get('GroupName'))

        return group_names

    def get_group_policy_statement(self, group_name: str, policy_name: str):
        policy = self.iam_client.get_group_policy(GroupName=group_name, PolicyName=policy_name)
        statement_list = policy.get('PolicyDocument').get('Statement')

        return statement_list

    def get_mfa_devices(self):
        mfa_devices = self.iam_client.list_mfa_devices(UserName=self.user_name)
        return mfa_devices.get('MFADevices')

    def get_mfa_serial_numbers(self):
        serial_numbers = []
        mfa_devices = self.get_mfa_devices()
        for mfa_device in mfa_devices:
            serial_numbers.append(mfa_device.get('SerialNumber'))

        return serial_numbers
