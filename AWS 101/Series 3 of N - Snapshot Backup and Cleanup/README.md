### Problem:
  * How to schedule creation of snapshots and cleaning up stale backups og EC2 instance volumes in all regions using Lambda Function
 
### Solution:
  * This task involves 2 steps
    * **Create a policy and a role**
      - First create a custom policy using the custom JSON as below:
        ```
        {
          "Version": "2012-10-17",
          "Statement": [{
              "Effect": "Allow",
              "Action": [
                "logs:CreateLogGroup",
                "logs:CreateLogStream",
                "logs:PutLogEvents"
              ],
              "Resource": "arn:aws:logs:*:*:*"
            },
            {
              "Effect": "Allow",
              "Action": [
                "ec2:CreateSnapshot",
                "ec2:DeleteSnapshot",
                "ec2:Describe*",
                "ec2:ModifySnapshotAttribute",
                "ec2:ResetSnapshotAttribute",
                "ec2:CreateTags"
              ],
              "Resource": "*"
            }
          ]
        }
        ```
      - The above policy assigns the Lambda function specified permissions to create, delete or tag snapshots and create log groups and streams and write log events in CloudWatch
      - ![The IAM Policy](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%202%20of%20N%20-%20Lambda%20Schedule%20Instance%20Stop/images/IAMPolicy.PNG)

    * **Create a Lambda Function for ***backup*** of the snapshots using that role**
      * Use the above role to create the Lambda function and set the time out from 3 secs to a minute or more as it will take some time to loop through all instances in all regions.
      * Now create a Lambda Function using the code below:
      ```
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

      ```
      - ![The Lambda Function](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%203%20of%20N%20-%20Snapshot%20Backup%20and%20Cleanup/images/LambdafunctionForBackup.PNG)

      - ![The Lambda Function Execution Result](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%203%20of%20N%20-%20Snapshot%20Backup%20and%20Cleanup/images/LambdafunctionForBackupExecutionResult.PNG)


    * **Create a Lambda Function for ***cleanup*** of the snapshots using that role**
      * Use the above role to create the Lambda function and set the time out from 3 secs to a minute or more as it will take some time to loop through all instances in all regions.
      * Now create a Lambda Function using the code below:
      ```
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
      ```
      - ![The Lambda Function](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%203%20of%20N%20-%20Snapshot%20Backup%20and%20Cleanup/images/LambdafunctionForCleanup.PNG)

      - ![The Lambda Function Execution Result](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%203%20of%20N%20-%20Snapshot%20Backup%20and%20Cleanup/images/LambdafunctionForCleanupExecutionResult.PNG)


    * **Schedule a CRON job to schedule the Lambda Funtion**
      - Use a CRON job syntax to schedule a CRON job 
      - Cron expression: 0 22 ? * MON-FRI *
      - Note : 23 hrs is in UTC which will be 5 pm EST
      - ![The CRON Job](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%203%20of%20N%20-%20Snapshot%20Backup%20and%20Cleanup/images/CRONJob.PNG)