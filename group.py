import crhelper
from utils import change_requires_update, filter_dictionary

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
    'CoreDefinitionVersionArn',
    'DeviceDefinitionVersionArn',
    'FunctionDefinitionVersionArn',
    'LoggerDefinitionVersionArn',
    'ResourceDefinitionVersionArn',
    'SubscriptionDefinitionVersionArn'
]

def create(event, context):
    params = {}
    params['Name'] = event['ResourceProperties']['Name']
    initial_version = filter_dictionary(event['ResourceProperties'], version_attributes)
    if initial_version:
        logger.info('Group InitialVersion detected')
        params['InitialVersion'] = initial_version
    response = greengrass_client.create_group(**params)
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
        logger.info('Group requires new version')
        params = filter_dictionary(event['ResourceProperties'], version_attributes)
        params['GroupId'] = physical_resource_id
        version_response = greengrass_client.create_group_version(**params)
        version_response.pop('ResponseMetadata', None)
        response['Version'] = version_response

    requires_rename = change_requires_update(logger,
                                             ['Name'],
                                             event['OldResourceProperties'],
                                             event['ResourceProperties'])
    if requires_rename:
        logger.info('Group is renamed')
        params = {
            'GroupId': physical_resource_id,
            'Name': event['ResourceProperties']['Name']
        }
        greengrass_client.update_group(**params)

    return physical_resource_id, response

def delete(event, context):
    physical_resource_id = event['PhysicalResourceId']
    if physical_resource_id == 'NONE':
        # This is a rollback from a failed create.  Nothing to do.
        return

    greengrass_client.delete_group(GroupId=physical_resource_id)
    return

def handler(event, context):
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)
