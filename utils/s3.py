import urllib3
import boto3
from botocore.config import Config
from botocore.exceptions import ClientError

from utils.logs import msg


def s3_ensure_bucket(
    endpoint: str, access_key: str, secret_key: str, bucket: str, region: str
) -> None:
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    client = boto3.client(
        "s3",
        endpoint_url=endpoint,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=region,
        verify=False,
        config=Config(s3={"addressing_style": "path"}),
    )
    try:
        client.head_bucket(Bucket=bucket)
        msg(level="info", message=f"S3 bucket '{bucket}' already exists at {endpoint}")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code in ("404", "NoSuchBucket"):
            client.create_bucket(Bucket=bucket)
            msg(level="info", message=f"S3 bucket '{bucket}' created at {endpoint}")
        else:
            msg(
                level="error",
                message=f"Failed to check S3 bucket '{bucket}' at {endpoint}: {e}",
            )
            raise SystemExit(1)
