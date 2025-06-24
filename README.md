# What is GenAI-Pool?

GenAI pool is a Flask-based, proxy/load balancer for Google's AI APIs to handle concurrent API requests efficiently. Allows you to use multiple API keys (these can be free tier) as a single client over Socket.io network.

# Why you should use GenAI-Pool?

- Manages multiple Google AI API keys and clients
- Implements rate limiting and quota management via Redis
- Supports lazy loading of clients
- Rotates between different Gemini models based on user preferences, availability and quotas
- Can be easily deployed via Docker
- Handles multiple Socket.io connections for streaming AI responses
- Advanced configuration options