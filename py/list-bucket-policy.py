import boto3
from botocore.exceptions import ClientError
import argparse
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from common.list_sso_profiles import list_sso_profiles

def get_bucket_location(s3_client, bucket_name):
    """Get the region of a specific bucket."""
    try:
        location = s3_client.get_bucket_location(Bucket=bucket_name)['LocationConstraint']
        return location if location else 'us-east-1'
    except ClientError as e:
        print(f"Error getting location for bucket {bucket_name}: {e}")
        return None

def check_bucket_policy(session, bucket_name, policy_filter):
    """Check the policy of a specific bucket."""
    s3 = session.client('s3')
    bucket_region = get_bucket_location(s3, bucket_name)
    
    if bucket_region:
        s3_region = session.client('s3', region_name=bucket_region)
        
        try:
            policy = s3_region.get_bucket_policy(Bucket=bucket_name)
            policy_content = policy['Policy']

            if policy_filter:
                if policy_filter in policy_content:
                    print(f"\nBucket {bucket_name} matches the filter in {bucket_region}:")
                    print(json.dumps(json.loads(policy_content), indent=4))
                else:
                    print(f"Bucket {bucket_name} does NOT match the filter in {bucket_region}.")
            else:
                print(f"\nBucket {bucket_name} policy in {bucket_region}:")
                print(json.dumps(json.loads(policy_content), indent=4))

        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchBucketPolicy':
                print(f"Bucket {bucket_name} does NOT have any policy.")
            else:
                print(f"Error checking bucket {bucket_name}: {e}")

def check_bucket_policies(profile_name: str, policy_filter: str = None):
    """Check bucket policies for a specific AWS SSO profile."""
    session = boto3.session.Session(profile_name=profile_name)
    s3 = session.client('s3')
    
    try:
        buckets = s3.list_buckets()
        bucket_names = [bucket['Name'] for bucket in buckets['Buckets']]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(check_bucket_policy, session, bucket_name, policy_filter) for bucket_name in bucket_names]
            for future in as_completed(futures):
                future.result()
                
    except ClientError as e:
        print(f"Error listing buckets: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check S3 bucket policies across AWS accounts.")
    parser.add_argument("--profile", help="AWS SSO profile name (optional, will prompt if not provided).")
    parser.add_argument("--filter", help="String to filter in bucket policies (e.g., 'aws:SecureTransport').")

    args = parser.parse_args()

    profile_name = args.profile
    if not profile_name:
        profiles = list_sso_profiles()
        if profiles:
            print("Available AWS SSO profiles:")
            for i, profile in enumerate(profiles, 1):
                print(f"{i}. {profile}")
            choice = int(input("\nSelect a profile by number: "))
            profile_name = profiles[choice - 1]
        else:
            print("No AWS SSO profiles found. Exiting.")
            exit(1)

    policy_filter = args.filter
    if not policy_filter:
        policy_filter = input("Enter a string to filter bucket policies (leave blank for no filter): ").strip()

    check_bucket_policies(profile_name, policy_filter)