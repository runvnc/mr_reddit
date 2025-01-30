import asyncio
from mod import monitor_subreddit, init_reddit_client

async def main():
    print("Starting direct monitor test...")
    await monitor_subreddit()

if __name__ == "__main__":
    asyncio.run(main())
