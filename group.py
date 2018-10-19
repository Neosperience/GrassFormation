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

group_version_attributes = [
    'CoreDefinitionVersionArn',
    'DeviceDefinitionVersionArn',
    'FunctionDefinitionVersionArn',
    'LoggerDefinitionVersionArn',
    'ResourceDefinitionVersionArn',
    'SubscriptionDefinitionVersionArn'
]

def create(event, context):
    """
    Place your code to handle Create events here.

    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    params = {}
    params['Name'] = event['ResourceProperties']['Name']
    initial_version = filter_dictionary(event['ResourceProperties'], group_version_attributes)
    if initial_version:
        logger.info('Group InitialVersion detected')
        params['InitialVersion'] = initial_version
    response = greengrass_client.create_group(**params)
    response.pop('ResponseMetadata', None)
    physical_resource_id = response['Id']
    return physical_resource_id, response


def update(event, context):
    """
    Place your code to handle Update events here

    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    physical_resource_id = event['PhysicalResourceId']
    response = {}
    group_requires_new_version = change_requires_update(logger,
                                                        group_version_attributes,
                                                        event['OldResourceProperties'],
                                                        event['ResourceProperties'])
    if group_requires_new_version:
        logger.info('Group requires new version')
        params = filter_dictionary(event['ResourceProperties'], group_version_attributes)
        params['GroupId'] = physical_resource_id
        version_response = greengrass_client.create_group_version(**params)
        version_response.pop('ResponseMetadata', None)
        response['create_group_version'] = version_response

    group_requires_rename = change_requires_update(logger,
                                                   ['Name'],
                                                   event['OldResourceProperties'],
                                                   event['ResourceProperties'])
    if group_requires_rename:
        logger.info('Group is renamed')
        params = {'GroupId': physical_resource_id, 'Name': event['ResourceProperties']['Name']}
        update_response = greengrass_client.update_group(**params)
        update_response.pop('ResponseMetadata', None)
        response['update_group'] = update_response

    return physical_resource_id, response


def delete(event, context):
    """
    Place your code to handle Delete events here

    To return a failure to CloudFormation simply raise an exception, the exception message will be sent to CloudFormation Events.
    """
    physical_resource_id = event['PhysicalResourceId']
    if physical_resource_id == 'NONE':
        # This is a rollback from a failed create.  Nothing to do.
        return

    greengrass_client.delete_group(GroupId=physical_resource_id)
    return


def handler(event, context):
    """
    Main handler function, passes off it's work to crhelper's cfn_handler
    """
    # update the logger with event info
    global logger
    logger = crhelper.log_config(event)
    return crhelper.cfn_handler(event, context, create, update, delete, logger,
                                init_failed)
