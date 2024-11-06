import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from datetime import datetime
from azure.storage.filedatalake import DataLakeServiceClient
import json

BLOB_STORAGE_ACCOUNT_CONNECTION_STRING = ""
BLOB_CONTAINER_NAME = ""
EVENTHUB_CONNECTION_STR = ''
EVENTHUB_NAME = ''
DATA_LAKE_KEY = ""
DATA_LAKE_NAME = ""


async def on_event(partition_context, event):
    try:
        eventData = event.body_as_str()
        redditPost = json.loads(eventData)['data']
        print("Raw event message:", redditPost['title'])
        print("Processing raw event message...")
        creationTime = datetime.utcfromtimestamp(redditPost['created_utc'])
        directoryName = creationTime.strftime('%Y/%m/%d/%H/%M')

        fileName = 'redditPost.json'
        service = DataLakeServiceClient(account_url="{}://{}.dfs.core.windows.net".format(
            "https", DATA_LAKE_NAME), credential=DATA_LAKE_KEY)
        fileSystemName = "adtpiuocontainer"
        filesystemClient = service.get_file_system_client(fileSystemName)

        # Get or create the directory in the file system
        directory_client = filesystemClient.get_directory_client(directoryName)
        if not directory_client.exists():
            directory_client.create_directory()

        # Get or create the file in the directory
        file_client = directory_client.get_file_client(fileName)
        file_content = json.dumps(redditPost)

        # Upload data to the file
        if not file_client.exists():
            file_client.create_file()
        file_client.append_data(file_content.encode(
            'utf-8'), offset=0, length=len(file_content))
        file_client.flush_data(len(file_content))

        await partition_context.update_checkpoint(event)
    except Exception as e:
        print("Error: ", e)


async def main():
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        BLOB_STORAGE_ACCOUNT_CONNECTION_STRING, BLOB_CONTAINER_NAME)

    client = EventHubConsumerClient.from_connection_string(
        EVENTHUB_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENTHUB_NAME, checkpoint_store=checkpoint_store)

    async with client:
        await client.receive(on_event=on_event,  starting_position="-1")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
