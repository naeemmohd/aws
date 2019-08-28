# import boto3 and datetime module
from datetime import datetime
import boto3


def lambda_handler(event, context):

    # Enlist all regions
    ec2Client = boto3.client('ec2')     # retrieve the EC2 client first
    ec2Regions = [region['RegionName'] for region in ec2Client.describe_regions()['Regions']]    # List Comprehension to get all regions

    # Lop though the regions to find any instances running and stop them
    for ec2Region in ec2Regions:
        print("Searching in the region:", ec2Region)
        ec2Resource = boto3.resource('ec2', region_name=ec2Region)     # retrieve EC2 resource
        
        # filter only running instances
        ec2Instances = ec2Resource.instances.filter(Filters=[{'Name': 'tag:serversforbackupandcleanup', 'Values': ['true']}]) # filtering the running ec2 resources

        # ISO 8601 timestamp, i.e. 2019-01-31T14:01:58
        timestamp = datetime.utcnow().replace(microsecond=0).isoformat()

        # Iterate through the instances in that region and create a snapshot
        for instance in ec2Instances.all():
            for volume in instance.volumes.all():

                details = 'Snapshot Backup for Instance: {0}, Volume: {1}, created at:{2}'.format(instance.id, volume.id, timestamp)
                print(details)
                newSnapshot = volume.create_snapshot(Description=details)
                print("Snapshot created: ", newSnapshot.id)
