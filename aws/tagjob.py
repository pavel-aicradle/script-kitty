import boto3

client = boto3.client('sagemaker', region_name='us-west-2')

client.add_tags(ResourceArn='arn:aws:sagemaker:us-west-2:636539472052:labeling-job/twitter-crash',
	Tags=[
		{
			'Key': 'team:name',
			'Value': 'algorithms'
		},
		{
			'Key': 'created-with',
			'Value': 'manual'
		}
	]
)