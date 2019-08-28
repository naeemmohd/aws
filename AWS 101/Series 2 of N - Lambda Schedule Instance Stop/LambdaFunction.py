import boto3


def lambda_handler(event, context):

    # Step 1 : enlist all regions
    ec2Client = boto3.client('ec2')     # retrieve the EC2 client first
    ec2Regions = [region['RegionName'] for region in ec2Client.describe_regions()['Regions']]    # List Comprehension to get all regions

    # Lop though the regions to find any instances running and stop them
    for ec2Region in ec2Regions:
        print("Searching in the region:", ec2Region)
        ec2Resource = boto3.resource('ec2', region_name=ec2Region)     # retrieve EC2 resource
        
        # filter only running instances
        ec2Instances = ec2Resource.instances.filter(Filters=[{'Name': 'instance-state-name', 'Values': ['running']}]) # filtering the running ec2 resources

        # Loop though to stop the running instances in that region
        for ec2Instance in ec2Instances:
            print("Stopping the EC2 instance: ", ec2Instance.id )
            ec2Instance.stop()
