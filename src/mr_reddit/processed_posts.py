import os
import json
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class ProcessedPosts:
    def __init__(self, base_path="data/reddit_posts"):
        self.base_path = base_path
    
    def get_day_file(self, subreddit, dt=None):
        if not dt:
            dt = datetime.now()
        return f"{self.base_path}/{subreddit}/{dt.year}/{dt.month:02d}/{dt.day:02d}.json"
    
    async def mark_processed(self, subreddit, post_id):
        path = self.get_day_file(subreddit)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        
        data = {}
        if os.path.exists(path):
            with open(path) as f:
                data = json.load(f)
        
        if 'processed_ids' not in data:
            data['processed_ids'] = {}
            
        data['processed_ids'][post_id] = datetime.now().isoformat()
        
        with open(path, 'w') as f:
            json.dump(data, f)
            logger.info(f"Marked post {post_id} as processed in {path}")
    
    async def is_processed(self, subreddit, post_id):
        # Check today and yesterday's file
        for days in [0, 1]:
            dt = datetime.now() - timedelta(days=days)
            path = self.get_day_file(subreddit, dt)
            if os.path.exists(path):
                with open(path) as f:
                    data = json.load(f)
                    if post_id in data.get('processed_ids', {}):
                        logger.debug(f"Found post {post_id} in {path}")
                        return True
        return False
    
    async def cleanup_old_files(self, days_to_keep=7):
        """Remove files older than days_to_keep days."""
        try:
            for subreddit in os.listdir(self.base_path):
                subreddit_path = os.path.join(self.base_path, subreddit)
                if not os.path.isdir(subreddit_path):
                    continue
                    
                for year in os.listdir(subreddit_path):
                    year_path = os.path.join(subreddit_path, year)
                    if not os.path.isdir(year_path):
                        continue
                        
                    for month in os.listdir(year_path):
                        month_path = os.path.join(year_path, month)
                        if not os.path.isdir(month_path):
                            continue
                            
                        for day in os.listdir(month_path):
                            day_path = os.path.join(month_path, day)
                            if not os.path.isfile(day_path):
                                continue
                                
                            # Parse date from path
                            try:
                                file_date = datetime.strptime(f"{year}/{month}/{day}", "%Y/%m/%d")
                                if (datetime.now() - file_date).days > days_to_keep:
                                    os.remove(day_path)
                                    logger.info(f"Removed old file: {day_path}")
                            except ValueError:
                                logger.warning(f"Could not parse date from path: {day_path}")
                                continue
                                
                        # Try to remove empty directories
                        try:
                            if not os.listdir(month_path):
                                os.rmdir(month_path)
                        except OSError:
                            pass
                            
                    try:
                        if not os.listdir(year_path):
                            os.rmdir(year_path)
                    except OSError:
                        pass
                        
                try:
                    if not os.listdir(subreddit_path):
                        os.rmdir(subreddit_path)
                except OSError:
                    pass
                    
        except Exception as e:
            logger.error(f"Error during cleanup: {str(e)}")
