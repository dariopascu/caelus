from botocore.client import BaseClient


def get_waiter(aws_client: BaseClient, waiter_name: str, delay: int, max_attempts: int):
    waiter = aws_client.get_waiter(waiter_name)

    waiter.config.delay = delay
    waiter.config.max_attempts = max_attempts

    return waiter
