# MindRoot Reddit Bot Plugin

A plugin for MindRoot that monitors r/ai_agents subreddit and creates chat sessions for new posts.

## Installation

1. Clone this repository or copy files to your plugins directory
2. Install the package:
   ```bash
   pip install -e .
   ```
3. Copy `.env.example` to `.env` and fill in your Reddit API credentials:
   ```bash
   cp .env.example .env
   ```

## Configuration

### Reddit API Credentials

You'll need to create a Reddit application to get API credentials:

1. Go to https://www.reddit.com/prefs/apps
2. Click "create another app..."
3. Fill in the required information:
   - Name: MindRoot Bot
   - Type: Script
   - Description: Bot for monitoring r/ai_agents
   - About URL: (optional)
   - Redirect URI: http://localhost:8080

4. After creating the app, you'll get:
   - client_id (under the app name)
   - client_secret

Add these to your `.env` file:

```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
```

### Agent Configuration

Set the default agent name in `.env`:

```
DEFAULT_AGENT_NAME=your_agent_name
```

## How It Works

1. The plugin initializes a Reddit client using PRAW
2. Monitors r/ai_agents subreddit for new posts
3. When a new post is detected:
   - Creates a new chat session
   - Formats the post content
   - Sends it to the specified agent
4. Tracks processed posts to avoid duplicates
5. Cleans up old processed posts after 24 hours

## Services

- `init_reddit_client()`: Initialize the Reddit API client
- `monitor_subreddit()`: Check for new posts
- `process_reddit_post()`: Handle new posts and create chat sessions
- `start_monitoring()`: Main service that runs continuously

## Error Handling

The plugin includes comprehensive error handling and logging:
- API authentication issues
- Network errors
- Post processing failures
- Rate limiting

Logs are written to the standard output with appropriate log levels.

## Development

To modify or extend the plugin:

1. Update services in `mod.py`
2. Add new services to `plugin_info.json`
3. Update environment variables in `.env.example`
4. Test thoroughly before deployment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License
