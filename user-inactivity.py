# This AWS Lambda script automates the management of IAM user access keys based on inactivity. It performs the following actions:

# Fetch IAM Users & Access Keys: Retrieves a list of all IAM users and their associated access keys.
# Evaluate Key Inactivity: Checks the last used date for each access key. If a key has been inactive for a specified number of days (DISABLE_IN_DAYS), it sends a warning. If the inactivity exceeds the threshold (DISABLE_IN_DAYS), the key is disabled. If inactivity surpasses DELETE_IN_DAYS, the access key is deleted, and the corresponding IAM user is removed.
# Notification: Sends notifications regarding the status of the user’s access keys (Warning, Disable, or Delete) with detailed inactivity information.
# Environment Variables: Configurable thresholds for disabling and deleting keys are set through environment variables (DISABLE_IN_DAYS, DELETE_IN_DAYS, etc.)
# Workflow:
# IAM users are queried for their associated access keys.
# Last used date for each key is checked.
# Depending on inactivity, keys are either warned, disabled, or deleted.
# The script logs and notifies actions taken, based on the inactivity thresholds.


import os
import boto3
from datetime import datetime

DISABLE_IN_DAYS = int(os.environ['DISABLE_IN_DAYS'])
DELETE_IN_DAYS = int(os.environ['DELETE_IN_DAYS'])

def lambda_handler(event, context):

    iam_client = boto3.client('iam')
    iam_resource = boto3.resource('iam')
    all_iam_users = [user.name for user in iam_resource.users.all()]
    associated_email = {}

    for user in all_iam_users:
        response = iam_client.list_user_tags(UserName=user)["Tags"]
        for i in response:
            if i["Key"] == "email":
                associated_email[user] = i["Value"]
    access_key_data = []

    for user in all_iam_users:
        response = iam_client.list_access_keys(UserName=user)
        for i in response["AccessKeyMetadata"]:
            access_key_data.append(i)

    for i in access_key_data:
        response = iam_client.get_access_key_last_used(AccessKeyId=i["AccessKeyId"])
        if "LastUsedDate" in response["AccessKeyLastUsed"].keys():    
            i["LastUsed"] = response["AccessKeyLastUsed"]["LastUsedDate"]
        else:
            i["LastUsed"] = i["CreateDate"]

    for access_key in access_key_data:
        
        last_used_days = (datetime.today().date() - access_key["LastUsed"].date()).days
        if last_used_days == (disable_in_days-1):
            print((datetime.today().date() - access_key["LastUsed"].date()))
            #Sending warnings
            notify_email("WARNING", access_key["UserName"], access_key["LastUsed"].date())
            print(associated_email[access_key["UserName"]])
            
        elif last_used_days >= disable_in_days and last_used_days < delete_in_days:
            notify_email("DISABLE", access_key["UserName"], access_key["LastUsed"].date())
            # Disable access key
            iam_client.update_access_key(UserName=access_key['UserName'],
                                         AccessKeyId=access_key["AccessKeyId"],
                                         Status='Inactive')
                
        elif last_used_days > delete_in_days:
            notify_email("DELETE", access_key["UserName"], access_key["LastUsed"].date())
            iam_client.delete_access_key(UserName=access_key['UserName'],
                                         AccessKeyId=access_key["AccessKeyId"])
            # DELETE USER
            iam_client.delete_user(UserName=access_key['UserName'])
    return {
        'statusCode': 200,
        'body': 'IAM USERS SUSPENSION AND DELETION!'
    }

def notify_email(action, username, last_used_on):
    if action == "DELETE":
      print(" %s the  < %s > due to inactivity in the past %d days. Last activity was on %s \n\n" % ( action, username, delete_in_days, last_used_on ))
    elif action == "DISABLE":
      print(" %s the  < %s > due to inactivity in the past %d days. Last activity was on %s \n\n" % ( action, username, disable_in_days, last_used_on ))
    elif action == "WARNING":
      print(" %s :  USER: < %s > is going to be disabled in 24 hours due to inactivity in the past %d days, Kindly use it to prevent this action. Last activity was on %s \n\n" % ( action, username, disable_in_days, last_used_on ))
    else:
      print("ENJOY")
    return "Hello IAM"
