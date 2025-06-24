![image](https://github.com/user-attachments/assets/d1b14e3a-48b3-4a6a-96ec-7abeac3be3a1)

GenAI pool is a Flask-based, proxy/load balancer for Google's AI APIs to handle concurrent API requests efficiently. Allows you to use multiple API keys (these can be free tier) as a single client over Socket.io network. Useful for people who wants to make AI applications with low cost.  

## Why you should use GenAI-Pool?

- Manages multiple Google AI API keys and clients
- Implements rate limiting and quota management via Redis
- Supports lazy loading of clients
- Rotates between different Gemini models based on user preferences, availability and quotas
- Can be easily deployed via Docker
- Handles multiple Socket.io connections for streaming AI responses
- Advanced configuration options

## License

[MIT](https://opensource.org/licenses/MIT)
