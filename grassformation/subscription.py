# grassformation/subscription.py

''' Defines the lambda function for managing CloudFormation custom resource of
AWS Greengrass Subscription Definition. '''

import botocore
from grassformation.utils import crhelper
from grassformation.utils import keypath
from grassformation.utils import change_requires_update, filter_dictionary, val_to_bool

# initialise logger
logger = crhelper.log_config({"RequestId": "CONTAINER_INIT"})
logger.info('Logging configured')
# set global to track init failures
init_failed = False

try:
    import boto3
    greengrass_client = boto3.client('greengrass')
    logger.info("Container initialization completed")
except Exception as e:
    logger.error(e, exc_info=True)
    init_failed = e

version_attributes = [
    'Subscriptions'
]

def create(event, context):
    params = {}
    params['Name'] = event['ResourceProperties']['Name']
    initial_version = filter_dictionary(event['ResourceProperties'], version_attributes)
    if initial_version:
        logger.info('Subscription Definition InitialVersion detected')
        params['InitialVersion'] = initial_version
    response = greengrass_client.create_subscription_definition(**params)
    response.pop('ResponseMetadata', None)
    physical_resource_id = response['Id']
    return physical_resource_id, response

def update(event, context):
    physical_resource_id = event['PhysicalResourceId']
    response = {}
    requires_new_version = change_requires_update(logger,
                                                  version_attributes,
                                                  event['OldResourceProperties'],
                                                  event['ResourceProperties'])
    if requires_new_version:
        logger.info('Subscription Definition requires new version')
        params = filter_dictionary(event['ResourceProperties'], version_attributes)
        params['SubscriptionDefinitionId'] = physical_resource_id
        version_response = greengrass_client.create_subscription_definition_version(**params)
        version_response.pop('ResponseMetadata', None)
        response['Version'] = version_response

    requires_rename = change_requires_update(logger,
                                             ['Name'],
                                             event['OldResourceProperties'],
                                             event['ResourceProperties'])
    if requires_rename:
        logger.info('Subscription Definition is renamed')
        params = {
            'SubscriptionDefinitionId': physical_resource_id,
            'Name': event['ResourceProperties']['Name']
        }
        greengrass_client.update_subscription_definition(**params)

    return physical_resource_id, response

def delete(event, context):
    physical_resource_id = event['PhysicalResourceId']
    if physical_resource_id == 'NONE':
        # This is a rollback from a failed create.  Nothing to do.
        return
    try:
        greengrass_client.delete_subscription_definition(SubscriptionDefinitionId=physical_resource_id)
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == 'IdNotFoundException':
            logger.warning('Requested to delete non existing resource.')
        else:
            raise e
    return

def handler(event, context):
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)
