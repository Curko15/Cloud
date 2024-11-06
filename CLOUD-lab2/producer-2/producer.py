import requests
import requests.auth
import asyncio
from azure.eventhub import EventData
from azure.eventhub.aio import EventHubProducerClient
import json

CLIENT_ID = ''

CLIENT_SECRET = ''

USERNAME = ''

PASSWORD = ''

EVENTHUB_CONNECTION_STR = ''

EVENTHUB_NAME = ''


async def getRedditTopPosts(after=None):
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
    params = {'limit': 10, 't': 'all'}
    if after:
        params['after'] = after

    res = requests.get(redditApiUrl,
                       headers=headers, params=params)

    if res.status_code != 200:
        print('Unable to fetch posts')
        return []

    posts = res.json()["data"]["children"]
    print(posts)
    after = res.json()["data"]["after"]
    print(after)
    return posts, after


async def run():
    after = None
    # Fetch the posts
    while True:
        posts, after = await getRedditTopPosts(after)

        if not posts:
            break

        # Create a producer client to send messages to the event hub
        producer = EventHubProducerClient.from_connection_string(
            EVENTHUB_CONNECTION_STR, eventhub_name=EVENTHUB_NAME)
        async with producer:
            # Create a batch
            eventDataBatch = await producer.create_batch()
            for post in posts:
                # Add the post to the batch

                eventData = EventData(json.dumps(post))
                eventDataBatch.add(eventData)
            # Send the batch of events to the event hub
            await producer.send_batch(eventDataBatch)
        await asyncio.sleep(10)

# Run the main method
if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    while True:
        pass
