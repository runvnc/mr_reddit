from lib.providers.services import service
from lib.providers.commands import command
from coreplugins.chat.services import init_chat_session, send_message_to_agent
from lib.providers.hooks import hook
from lib.chatcontext import ChatContext
from lib.utils.debug import debug_box
import asyncpraw
import os
from dotenv import load_dotenv
import asyncio
import json
from typing import Optional, Dict
from datetime import datetime, timezone
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

reddit_client: Optional[asyncpraw.Reddit] = None

processed_posts: Dict[str, dict] = {}

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

        processed_posts[post.id] = {
            'log_id': log_id,
            'post': post,
            'timestamp': datetime.now(timezone.utc)
        }

        agent_name = os.getenv('DEFAULT_AGENT_NAME', 'default_agent')
        await init_chat_session(
            user=os.getenv('REDDIT_USERNAME'),
            agent_name=agent_name,
            log_id=log_id
        )

        subreddit = os.getenv('REDDIT_SUBREDDIT')
        if not subreddit:
            logger.error("REDDIT_SUBREDDIT environment variable not set")
            return False

        
        message = {
            "type": "text",
            "text": f"New post from r/{subreddit}:\n\nTitle: {post.title}\n\n{post.selftext}",
            "metadata": {
                "post_id": post.id,
                "log_id": log_id,
                "subreddit": subreddit
            }
        }

        await send_message_to_agent(
            session_id=log_id,
            message=message,
            user={"username": os.getenv('REDDIT_USERNAME') }
        )
        
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
            
        if post_id not in processed_posts:
            return {"error": f"Post ID {post_id} not found in processed posts"}
            
        post_data = processed_posts[post_id]
        post = post_data['post']
        
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
    """Monitor the configured subreddit (from REDDIT_SUBREDDIT env var) for new posts."""
    global reddit_client, processed_posts
    debug_box("Checking subreddit")
    try:
        if reddit_client is None:
            success = await init_reddit_client(context)
            if not success:
                logger.error("Failed to initialize Reddit client")
                return False
        
        subreddit_name = os.getenv('REDDIT_SUBREDDIT')
        debug_box(f"Subbreddit name: {subreddit_name}")

        if not subreddit_name:
            logger.error("REDDIT_SUBREDDIT environment variable not set")
            return False

        subreddit = await reddit_client.subreddit(subreddit_name)
        
        # Clean up old processed posts (older than 24 hours)
        current_time = datetime.now(timezone.utc)
        processed_posts = {
            post_id: data 
            for post_id, data in processed_posts.items()
            if (current_time - data['timestamp']).total_seconds() < 86400
        }
        
        async for post in subreddit.new(limit=10):
            if post.id not in processed_posts:
                logger.info(f"New post found: {post.id}")
                await process_reddit_post(post, context)
        
        return True
    except Exception as e:
        logger.error(f"Error monitoring subreddit: {str(e)}")
        return False

# Start monitoring when plugin loads
@hook()
async def startup(app, context=None):
    """Start the monitoring service."""
    debug_box("Started monitoring subreddit")
    while True:
        await monitor_subreddit(context)
        await asyncio.sleep(60)  # Wait 60 seconds between checks

