# import boto3 and datetime module
from datetime import datetime
import boto3


def lambda_handler(event, context):

    # Get account ID to retrive the list of only snapshots from your account
    accountID = boto3.client('sts').get_caller_identity().get('Account')

    # Enlist all regions
    ec2Client = boto3.client('ec2')     # retrieve the EC2 client first
    ec2Regions = [region['RegionName'] for region in ec2Client.describe_regions()['Regions']]    # List Comprehension to get all regions

    # Lop though the regions to find any instances running and stop them
    for ec2Region in ec2Regions:
        print("Searching in the region:", ec2Region)
        ec2Resource = boto3.resource('ec2', region_name=ec2Region)     # retrieve EC2 resource
        
        responseData = ec2Resource.describe_snapshots(OwnerIds=[accountID])
        accountSnapshots = responseData["Snapshots"]

        # Sorting the  snapshots by StartTime ascending
        accountSnapshots.sort(key=lambda x: x["StartTime"])

        # remove any snapshots which you dont want to clean up ( the latest 2 e.g.)
        accountSnapshots = accountSnapshots[:-2]

        # Iterate through the instances in that region and cleanup the snapshots if not in use else display proper message
        for snapshot in accountSnapshots:
            snapshotID = snapshot['SnapshotId']
            try:
                print("Cleaning up snapshot:", snapshotID)
                ec2Resource.delete_snapshot(SnapshotId=snapshotID)
            except:
                print("Snapshot {} already in use, can't clean it up.".format(id))
                continue