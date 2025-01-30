# MindRoot Reddit Bot Plugin

A plugin for [MindRoot](https://github.com/runvnc/mindroot) that monitors a configured subreddit and creates chat sessions for new posts.

## Installation

1. In the MindRoot Admin page UI, go to the Plugins section
2. Click 'Install from Github' button
3. Enter: `runvnc/mr_reddit`
4. Click Install
5. Restart MindRoot

## Configuration

### Reddit Setup Requirements

1. **Create a Reddit Account for the Bot**:
   - Create a regular Reddit account
   - Username should include 'bot' (e.g., 'mindroot_bot')
   - Set up profile to clearly indicate it's a bot
   - Note the username and password

2. **Create a Reddit Application**:
   - Go to https://www.reddit.com/prefs/apps
   - Click "create another app..."
   - Fill in the required information:
     - Name: MindRoot Bot
     - Type: Script
     - Description: Bot for monitoring r/ai_agents
     - About URL: (optional)
     - Redirect URI: http://localhost:8080
   - After creating the app, you'll get:
     - client_id (under the app name)
     - client_secret

3. **Configure Environment Variables**:
   Create a `.env` file in the plugin directory with:
   ```
   REDDIT_CLIENT_ID=your_client_id
   REDDIT_CLIENT_SECRET=your_client_secret
   REDDIT_USERNAME=your_bot_username
   REDDIT_PASSWORD=your_bot_password
   REDDIT_USER_AGENT=MindRoot Reddit Bot v0.1.0
   REDDIT_SUBREDDIT=ai_agents
   DEFAULT_AGENT_NAME=your_agent_name
   ```

## How It Works

1. The plugin initializes a Reddit client using PRAW
2. Monitors the configured subreddit for new posts
3. When a new post is detected:
   - Creates a new chat session
   - Formats the post content
   - Sends it to the specified agent
4. The agent can reply using the `reddit_reply` command
5. Tracks processed posts to avoid duplicates
6. Cleans up old processed posts after 24 hours

## Available Commands

### reddit_reply
Allows the agent to reply to Reddit posts.

Example:
```json
{
    "reddit_reply": {
        "post_id": "abc123",
        "reply_text": "This is my response to the Reddit post."
    }
}
```

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
