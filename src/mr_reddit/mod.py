from lib.providers.services import service
from lib.providers.commands import command
from coreplugins.chat.services import init_chat_session, send_message_to_agent
from lib.providers.hooks import hook
from lib.chatcontext import ChatContext
from lib.utils.debug import debug_box
from .processed_posts import ProcessedPosts
import asyncpraw
import os
from dotenv import load_dotenv
import asyncio
import json
from typing import Optional
from datetime import datetime, timezone
import logging
import traceback

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

reddit_client: Optional[asyncpraw.Reddit] = None
processed_posts = ProcessedPosts()

@service()
async def init_reddit_client(context=None):
    """Initialize the Reddit client using credentials from environment variables."""
    global reddit_client

    try:
        if reddit_client is not None:
            await reddit_client.close()

        reddit_client = asyncpraw.Reddit(
            client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            username=os.getenv('REDDIT_USERNAME'),
            password=os.getenv('REDDIT_PASSWORD'),
            user_agent=os.getenv('REDDIT_USER_AGENT', 'MindRoot Reddit Bot v0.1.0')
        )

        logger.info("Reddit client initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {str(e)}")
        return False

@service()
async def process_reddit_post(post, context=None):
    """Process a Reddit post and create a chat session."""
    try:
        log_id = f"reddit_{post.id}_{int(datetime.now(timezone.utc).timestamp())}"
        agent_name = os.getenv('DEFAULT_AGENT_NAME', 'default_agent')

        await init_chat_session(os.getenv('REDDIT_USERNAME'), agent_name, log_id)

        subreddit = os.getenv('REDDIT_SUBREDDIT')
        if not subreddit:
            logger.error("REDDIT_SUBREDDIT environment variable not set")
            return False

        message = f"New post from r/{subreddit}:\npost_id: {post.id}\n\nTitle: {post.title}\n\n{post.selftext}"
        user_ = {"username": os.getenv('REDDIT_USERNAME')}

        await send_message_to_agent(log_id, message, user=user_)

        logger.info(f"Successfully processed post {post.id}")
        return True
    except Exception as e:
        logger.error(f"Error processing post {post.id}: {str(e)}")
        return False

@command()
async def reddit_reply(post_id: str, reply_text: str, context=None):
    """Reply to a Reddit post or comment.

    Args:
        post_id: The ID of the Reddit post to reply to
        reply_text: The text content of the reply

    Example:
        { "reddit_reply": { "post_id": "abc123", "reply_text": "This is my response." } }
    """
    try:
        if reddit_client is None:
            await init_reddit_client(context)

        # Get the post from Reddit API
        post = await reddit_client.submission(id=post_id)
        if not post:
            return {"error": f"Post ID {post_id} not found"}

        # Submit the reply
        comment = await post.reply(reply_text)

        logger.info(f"Successfully replied to post {post_id}")
        return {
            "success": True,
            "comment_id": comment.id,
            "permalink": comment.permalink
        }

    except Exception as e:
        logger.error(f"Error replying to post {post_id}: {str(e)}")
        return {"error": str(e)}

@service()
async def monitor_subreddit(context=None):
    """Stream new posts from subreddit continuously."""
    try:
        if reddit_client is None:
            success = await init_reddit_client(context)
            if not success:
                logger.error("Failed to initialize Reddit client")
                return

        subreddit_name = os.getenv('REDDIT_SUBREDDIT')
        if not subreddit_name:
            logger.error("REDDIT_SUBREDDIT not set")
            return

        logger.info(f"Updated: Starting stream for r/{subreddit_name}")
        subreddit = await reddit_client.subreddit(subreddit_name, fetch=True)
        logger.info("display name: "+ subreddit.display_name)
        logger.info("title:"+ subreddit.title)
        # get a random limit between 60 and 80
        rand_limit = 60 + int(os.urandom(1)[0]) % 20
        # Infinite stream of new posts
        async for post in subreddit.top(time_filter="week"):
            try:
                print("Found new post!")
                print(post)
                if not await processed_posts.is_processed(subreddit_name, post.id):
                    logger.info(f"Processing new post: {post.id}")
                    # Process post with timeout
                    async with asyncio.timeout(90):
                        success = await process_reddit_post(post, context)
                        if success:
                            await processed_posts.mark_processed(subreddit_name, post.id)
                else:
                    logger.debug(f"Skipping already processed post: {post.id}")
            except asyncio.TimeoutError:
                logger.error(f"Timeout processing post {post.id}")
            except Exception as e:
                trace = traceback.format_exc()
                logger.error(f"Error processing post {post.id}: {str(e)}\n{trace}")
                # Continue streaming even if individual post fails
                continue

    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f"Stream error: {str(e)}\n{trace}")
        # Let monitoring_loop restart us
        return

@hook()
async def startup(app, context=None):
    """Start the monitoring service."""
    try:
        # Start monitoring in background task
        task = asyncio.create_task(monitor_subreddit(context))
        task.add_done_callback(
            lambda t: logger.error(f"Monitor task ended: {t.exception() if t.exception() else 'No error'}")
        )
        logger.info("Started Reddit monitoring task")
    except Exception as e:
        trace = traceback.format_exc()
        logger.error(f"Startup error: {str(e)}\n{trace}")
