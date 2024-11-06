import requests
import requests.auth
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
from dotenv import load_dotenv
import os

load_dotenv()

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')

EVENT_HUB_CONNECTION_STR = os.getenv('EVENT_HUB_CONNECTION_STR')
EVENT_HUB_NAME = os.getenv('EVENT_HUB_NAME')


async def getRedditTopPosts():
    # Authenticate with Reddit API
    auth = requests.auth.HTTPBasicAuth(CLIENT_ID, CLIENT_SECRET)

    data = {
        'grant_type': 'password',
        'username': USERNAME,
        'password': PASSWORD
    }

    headers = {'User-Agent': 'TPIUO_LAB'}

    # Get the access token from Reddit API
    res = requests.post('https://www.reddit.com/api/v1/access_token',
                        auth=auth, data=data, headers=headers)

    TOKEN = res.json()['access_token']

    headers['Authorization'] = f'bearer {TOKEN}'

    redditApiUrl = 'https://oauth.reddit.com/r/dataengineering/top'

    # Fetch the top 10 posts
    res = requests.get(redditApiUrl,
                       headers=headers, params={'limit': 10})

    if res.status_code != 200:
        print('Unable to fetch posts')
        return []
    else:
        posts = res.json()["data"]["children"]

    return posts


async def run():
    # Fetch the posts
    posts = await getRedditTopPosts()

    # Create a producer client to send messages to the event hub
    producer = EventHubProducerClient.from_connection_string(
        EVENT_HUB_CONNECTION_STR, eventhub_name=EVENT_HUB_NAME)
    async with producer:
        # Create a batch
        eventDataBatch = await producer.create_batch()
        for post in posts:
            # Add the post to the batch
            eventDataBatch.add(EventData(str(post)))
        # Send the batch of events to the event hub
        await producer.send_batch(eventDataBatch)


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    while True:
        pass
