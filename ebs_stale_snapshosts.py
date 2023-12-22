import boto3

def lambda_handler(event, context):
    # Create EC2 and EBS clients
    ec2_client = boto3.client('ec2')
    ebs_client = boto3.client('ec2')

    # Get a list of all EBS snapshots owned by the account
    response = ebs_client.describe_snapshots(OwnerIds=['self'])
    snapshots = response['Snapshots']

    # Get a list of all EC2 instances (running and stopped)
    instances = ec2_client.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])
    
    # Extract the instance IDs from the instances response
    active_instance_ids = [instance['InstanceId'] for reservation in instances['Reservations'] for instance in reservation['Instances']]

    # Iterate through each snapshot and check if associated volume is not associated with any active instance
    for snapshot in snapshots:
        volume_id = snapshot['VolumeId']

        # Check if the volume is not associated with any active instance
        if volume_id not in [volume['Ebs']['VolumeId'] for instance in instances['Reservations'] for volume in instance['BlockDeviceMappings']]:
            # Delete the stale snapshot
            snapshot_id = snapshot['SnapshotId']
            print(f"Deleting stale snapshot: {snapshot_id}")
            ebs_client.delete_snapshot(SnapshotId=snapshot_id)
