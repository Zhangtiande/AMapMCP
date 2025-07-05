# Amap Navigation MCP Tool

[简体中文](README.md) | [日本語](README_JA.md) | [English](README_EN.md)

This is an Amap Navigation MCP (Model Context Protocol) tool based on FastAPI and fastmcp. The tool provides an interactive map page that supports three types of navigation: driving, cycling, and walking. Navigation commands can be sent through the MCP interface for real-time route planning. The system uses WebSocket real-time communication and sessionid-based session management to ensure security and independence for multiple users.

## ⚠️ Important Security Notice

**This service is for learning and development testing purposes only. Production use is strictly prohibited!**

- 🔒 **API Key Exposure Risk**: Amap API key is passed through URL parameters, posing exposure risk
- 🌐 **Public Network Access Danger**: No key encryption or access control implemented, deployment to public networks is prohibited
- 📊 **Log Leakage Risk**: Keys may be recorded in server access logs
- 🔐 **No Security Protection**: Lacks HTTPS, key encryption, access restrictions, and other security measures

**Usage Recommendations:**
- ✅ Use only in local development environment
- ✅ Use test API keys
- ✅ Ensure firewall blocks external access
- ❌ Do not use production environment keys
- ❌ Do not deploy to public servers

## 🏗️ Architecture Design

- **Session Management**: Multi-user session isolation system based on sessionid
- **Map Page**: Interactive HTML page provided by FastAPI, requires valid sessionid
- **WebSocket Communication**: Real-time bidirectional communication, supports instant navigation command push
- **MCP Tools**: `create_session` for creating sessions, `send_navigation_to_map` for sending navigation commands
- **Multiple Navigation Types**: Supports driving, cycling, and walking navigation modes
- **Hybrid Input**: Supports mixed use of latitude/longitude coordinates and keyword locations

## 🚀 Quick Start

### 1. Environment Setup

We use `uv` for Python environment management. First, ensure you have `uv` installed:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create new virtual environment
uv venv

# Activate virtual environment
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
# Install dependencies using uv
uv pip install -r requirements.txt

# Sync dependencies (recommended)
uv sync
```

### 3. Set Environment Variables (Optional)

If you have your own Amap API key, you can set environment variables:

```bash
# Set environment variables
export AMAP_API_KEY="your-amap-api-key"
export AMAP_SECURITY_CODE="your-amap-security-code"
```

### 4. Start Server

```bash
# Direct run
python main.py

# Or using uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

When the server starts, you'll see the following information:
```
🚀 Starting Amap Navigation MCP Server...
🔧 MCP Endpoint: http://localhost:8000/mcp
📚 API Documentation: http://localhost:8000/docs

Usage Instructions:
1. Use MCP tool 'create_session' to create a session
2. Use the returned sessionid to access the map page
3. Use MCP tool 'send_navigation_to_map' to send navigation commands
```

## 🔌 API Interface

### Main Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | Get map page (requires sessionid parameter) |
| `/ws/{session_id}` | WebSocket | WebSocket connection endpoint |
| `/sessions` | GET | View all active sessions |
| `/queue-status` | GET | View command queue status |
| `/health` | GET | Health check |
| `/mcp` | - | MCP protocol endpoint |
| `/static` | GET | Static file service |

### Check System Status

```bash
# View all sessions
curl "http://localhost:8000/sessions"

# Check command queue status
curl "http://localhost:8000/queue-status"

# Health check
curl "http://localhost:8000/health"
```

## 🗝️ Get Amap API Key

1. Visit [Amap Open Platform](https://lbs.amap.com/)
2. Register account and login
3. Create application and get API Key
4. Enable JavaScript API in Web services

## 🎬 Usage Flow

1. **Set Environment Variables** → (Optional) Set `AMAP_API_KEY` and `AMAP_SECURITY_CODE`
2. **Start Service** → Run `python main.py`
3. **Create Session** → Use MCP tool `create_session`
4. **Access Map** → Use returned complete link to access map page (includes key parameters)
5. **Send Navigation Commands** → Use MCP tool `send_navigation_to_map`
6. **View Results** → Map displays navigation route in real-time via WebSocket

## 🌟 Features

- **WebSocket Real-time Communication**: Map page receives navigation commands in real-time via WebSocket
- **Session Isolation**: Each user has independent map session and connection
- **Multiple Navigation Types**: Supports driving, cycling, and walking navigation
- **Hybrid Input**: Supports mixed use of latitude/longitude coordinates and keywords
- **Auto Reconnection**: Automatically reconnects when WebSocket connection is lost
- **Secure Access**: Access control based on sessionid
- **Environment Variable Support**: Supports custom API key setting via environment variables
- **URL Parameter Passing**: Keys passed dynamically via URL parameters, flexible and secure
- **Responsive Design**: Adapts to various screen sizes

## 📂 Project Structure

```
08.amap/
├── main.py                 # Main program file
├── main.js                 # Client JavaScript file
├── main.html              # Map page HTML file
├── pyproject.toml         # Project configuration file
├── README.md             # Project documentation (Chinese)
├── README_EN.md         # Project documentation (English)
├── README_JA.md         # プロジェクトドキュメント（日本語）
└── uv.lock              # Dependency lock file
```

## 🛠️ Technology Stack

- **FastAPI**: Modern, fast web framework with WebSocket support
- **fastmcp**: MCP (Model Context Protocol) implementation
- **uvicorn**: ASGI server
- **WebSocket**: Real-time bidirectional communication protocol
- **Amap JavaScript API**: Map, driving, cycling, walking navigation services

## ⚠️ Important Notes

1. **🔐 Security First**: This service is for learning and testing only, prohibited in production!
2. **🔑 Key Security**: API key passed via URL parameters, leak risk exists, local use only
3. **🌐 Network Requirements**: Network connection needed to load map resources
4. **🔒 Session Management**: Must create session before accessing map page
5. **💻 Browser Compatibility**: Recommended to use in modern browsers (WebSocket support required)
6. **📍 Coordinate System**: Uses WGS84 coordinate system
7. **🚲 Navigation Limitations**: Cycling and walking navigation don't support policy parameter
8. **🔍 Search Requirements**: City information required for keyword search
9. **📝 Log Risk**: Keys may be recorded in various logs, cleanup needed
10. **🔒 Access Control**: Ensure service runs only in trusted networks

## 🤝 Contributing

Issues and Pull Requests are welcome!

## 📄 License

MIT License

**Disclaimer**:
This project is for learning and technical research purposes only. Users must:
- Comply with Amap API Terms of Service
- Not use this project in commercial production environments
- Take responsibility for API key leakage and other security risks
- Ensure compliance with local laws and regulations

The author bears no responsibility for any direct or indirect losses arising from the use of this project. 