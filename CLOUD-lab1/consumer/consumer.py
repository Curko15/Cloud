import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from dotenv import load_dotenv
import os

load_dotenv()

BLOB_STORAGE_CONNECTION_STRING = os.getenv('BLOB_STORAGE_CONNECTION_STRING')
BLOB_CONTAINER_NAME = os.getenv('BLOB_CONTAINER_NAME')
EVENT_HUB_CONNECTION_STR = os.getenv('EVENT_HUB_CONNECTION_STR')
EVENT_HUB_NAME = os.getenv('EVENT_HUB_NAME')


async def on_event(partition_context, event):
    # Parse the event message as JSON
    message = event.body_as_str(encoding='UTF-8')
    # Print the JSON message
    print("Received JSON message: {}".format(
        message, partition_context.partition_id))

    # Update the checkpoint so that the program doesn't read the events
    # that it has already read when you run it next time.
    await partition_context.update_checkpoint(event)


async def main():
    # Create an Azure blob checkpoint store to store the checkpoints.
    checkpoint_store = BlobCheckpointStore.from_connection_string(
        BLOB_STORAGE_CONNECTION_STRING, BLOB_CONTAINER_NAME)

    # Create a consumer client for the event hub.
    client = EventHubConsumerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR, consumer_group="$Default", eventhub_name=EVENT_HUB_NAME, checkpoint_store=checkpoint_store)

    async with client:
        # Call the receive method. Read from the beginning of the partition (starting_position: "-1")
        await client.receive(on_event=on_event,  starting_position="-1")

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
