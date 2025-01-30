import asyncio
import asyncpraw
import os
from dotenv import load_dotenv

async def test_connection():
    try:
        # Load environment variables
        load_dotenv()
        
        reddit = asyncpraw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent=os.getenv('REDDIT_USER_AGENT')
        )
        
        print("Created Reddit instance")
        
        # Add timeout to subreddit load
        try:
            subreddit = await reddit.subreddit(os.getenv('REDDIT_SUBREDDIT', 'AskReddit'))
            print(f"Got subreddit object for r/{subreddit.display_name}")
            
            # Add explicit timeout
            async with asyncio.timeout(10):
                await subreddit.load()
                print("Successfully loaded subreddit")
                print(f"Title: {subreddit.title}")
                print(f"Subscribers: {subreddit.subscribers}")
                
        except asyncio.TimeoutError:
            print("Timeout while loading subreddit")
        except Exception as e:
            print(f"Error loading subreddit: {e}")
            
        await reddit.close()
        
    except Exception as e:
        print(f"Error creating Reddit instance: {e}")
        
async def main():
    await test_connection()

if __name__ == "__main__":
    asyncio.run(main())
