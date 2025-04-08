# CORS Middleware Configuration in Python

A practical guide to configuring CORS middleware in Python web applications (FastAPI/Flask), focusing on headers and HTTP methods.

## Table of Contents

- [CORS Middleware Configuration in Python](#cors-middleware-configuration-in-python)
  - [Table of Contents](#table-of-contents)
  - [Key Parameters](#key-parameters)
  - [Allowed HTTP Methods](#allowed-http-methods)
    - [Recommended Configuration](#recommended-configuration)
  - [Essential Headers](#essential-headers)
  - [Configuration Examples](#configuration-examples)
    - [FastAPI](#fastapi)
    - [Flask](#flask)
  - [Best Practices](#best-practices)
  - [Troubleshooting](#troubleshooting)
  - [Next.js Integration with FastAPI](#nextjs-integration-with-fastapi)

## Key Parameters

| Parameter          | Description                             | Example                           |
| ------------------ | --------------------------------------- | --------------------------------- |
| `allow_origins`    | Allowed domains                         | `["https://yourdomain.com"]`      |
| `allow_methods`    | Allowed HTTP methods                    | `["GET", "POST"]`                 |
| `allow_headers`    | Allowed headers                         | `["Authorization", "Content-Type"]` |
| `allow_credentials`| Allow cookies/credentials               | `True`                            |

## Allowed HTTP Methods

### Recommended Configuration

```python
# Development
allow_methods = ["*"]

# Production
allow_methods = ["GET", "POST", "PUT", "DELETE"]
```

## Essential Headers

The most relevant CORS headers include:

- Access-Control-Allow-Origin
- Access-Control-Allow-Methods
- Access-Control-Allow-Headers
- Access-Control-Allow-Credentials

## Configuration Examples

Below are two examples (FastAPI and Flask):

### FastAPI

```python
# ...existing code...
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Authorization", "Content-Type"],
    allow_credentials=True,
)
```

### Flask

```python
# ...existing code...
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/*": {
        "origins": ["https://example.com"],
        "methods": ["GET", "POST"],
        "allow_headers": ["Authorization", "Content-Type"],
        "supports_credentials": True
    }
})
```

## Best Practices

- Keep domain and method lists updated.
- Restrict domains in production.
- Validate headers and methods before enabling them.

## Troubleshooting

- Check that CORS headers are being sent correctly.
- Use tools like a browser or cURL to inspect responses.
- Review server or proxy settings in production.

## Next.js Integration with FastAPI

When integrating FastAPI with a Next.js frontend:

- Configure your FastAPI CORS settings to include the Next.js development or production domain (e.g., `<http://localhost:3000>` or your hosted domain).
- Ensure you allow the required headers (e.g., "Content-Type", "Authorization") for API requests from Next.js.  
- Provide support for credentials if your Next.js app needs to handle user sessions or tokens.
