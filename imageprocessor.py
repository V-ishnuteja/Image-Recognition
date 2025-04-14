import json
import boto3
import os

# Initialize AWS clients
rekognition = boto3.client('rekognition')
sns = boto3.client('sns')
s3 = boto3.client('s3')

# Environment variable for SNS Topic ARN
SNS_TOPIC_ARN = os.environ['SNS_TOPIC_ARN']

# Labels that will trigger a notification
TRIGGER_LABELS = ['Person', 'Weapon', 'Fire']

def lambda_handler(event, context):
    # Get bucket and object key from the S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Call Rekognition to detect labels
    response = rekognition.detect_labels(
        Image={'S3Object': {'Bucket': bucket, 'Name': key}},
        MaxLabels=10,
        MinConfidence=75
    )

    labels_detected = [label['Name'] for label in response['Labels']]
    print("Labels Detected:", labels_detected)

    # Check if any of the trigger labels are detected
    matched_labels = [label for label in labels_detected if label in TRIGGER_LABELS]

    if matched_labels:
        # Construct the notification message
        message = (
            f"🚨 Alert! The following label(s) were detected in the uploaded image '{key}': "
            f"{', '.join(matched_labels)}.\n\n"
            f"Bucket: {bucket}"
        )

        # Publish to SNS topic
        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="⚠️ Image Recognition Alert",
            Message=message
        )

        return {
            'statusCode': 200,
            'body': json.dumps('Notification sent!')
        }

    return {
        'statusCode': 200,
        'body': json.dumps('No matching labels detected.')
    }
