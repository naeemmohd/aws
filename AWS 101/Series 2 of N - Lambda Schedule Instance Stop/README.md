### Problem:
  * How to schedule a stop and start all running EC2 instances in all regions using Lambda Function
 
### Solution:
  * This task involves 2 steps
    * **Create a policy and a role**
      - First create a custom policy using the custom JSON as below:
        ```
        {
          "Version": "2012-10-17",
          "Statement": [
            {
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
                "ec2:DescribeInstances",
                "ec2:DescribeRegions",
                "ec2:StartInstances",
                "ec2:StopInstances"
              ],
              "Resource": "*"
            }
          ]
        }
        ```
      - The above policy assigns the Lambda function specified permissions to describe, start, stop EC2 instances, describe regions, create log groups and streams and write log events in CloudWatch
      - ![The IAM Policy](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%202%20of%20N%20-%20Lambda%20Schedule%20Instance%20Stop/images/IAMPolicy.PNG)

    * **Create a Lambda Function using that role**
      * Use the above role to create the Lambda function and set the time out from 3 secs to a minute or more as it will take some time to loop through all instances in all regions.
      * Now create a Lambda Function using the code below:
      ```
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
      ```
      - ![The Lambda Function](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%202%20of%20N%20-%20Lambda%20Schedule%20Instance%20Stop/images/Lambdafunction.PNG)
      

    * **Schedule a CRON job to schedule the Lambda Funtion**
      - Use a CRON job syntax to schedule a CRON job 
      - Cron expression: 0 22 ? * MON-FRI *
      - Note : 23 hrs is in UTC which will be 5 pm EST
      - ![The CRON Job](https://github.com/naeemmohd/aws/blob/master/AWS%20101/Series%202%20of%20N%20-%20Lambda%20Schedule%20Instance%20Stop/images/CRONJob.PNG)