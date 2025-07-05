# 高德地图导航 MCP Tool

[简体中文](README.md) | [日本語](README_JA.md) | [English](README_EN.md)

这是一个基于 FastAPI 和 fastmcp 的高德地图导航 MCP (Model Context Protocol) 工具。该工具提供了一个交互式的地图页面，支持驾车、骑行、步行三种导航类型，可以通过 MCP 接口发送导航命令进行实时路线规划。系统采用 WebSocket 实时通信和基于 sessionid 的会话管理，确保多用户使用的安全性和独立性。

## ⚠️ 重要安全声明

**本服务仅用于学习和开发测试目的，严禁在生产环境中使用！**

- 🔒 **API 密钥暴露风险**：高德地图 API 密钥通过 URL 参数传递，存在暴露风险
- 🌐 **公网访问危险**：未实施密钥加密和访问控制，不得部署到公网
- 📊 **日志泄露风险**：密钥可能被记录在服务器访问日志中
- 🔐 **无安全防护**：缺乏 HTTPS、密钥加密、访问限制等安全措施

**使用建议：**
- ✅ 仅在本地开发环境使用
- ✅ 使用测试用的 API 密钥
- ✅ 确保防火墙阻止外部访问
- ❌ 禁止使用生产环境密钥
- ❌ 禁止部署到公网服务器

## 🏗️ 架构设计

- **会话管理**：基于 sessionid 的多用户会话隔离系统
- **地图页面**：FastAPI 提供的交互式 HTML 页面，需要有效的 sessionid 才能访问
- **WebSocket 通信**：实时双向通信，支持导航命令的即时推送
- **MCP Tools**：`create_session` 创建会话，`send_navigation_to_map` 发送导航命令
- **多种导航类型**：支持驾车、骑行、步行三种导航模式
- **混合输入**：支持经纬度坐标和关键字地点混合使用

## 🚀 快速开始

### 1. 环境设置

我们使用 `uv` 进行 Python 环境管理。首先确保已安装 `uv`：

```bash
# 安装 uv（如果尚未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 创建新的虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
.venv\Scripts\activate     # Windows
```

### 2. 安装依赖

```bash
# 使用 uv 安装依赖
uv pip install -r requirements.txt

# 同步依赖（推荐）
uv sync
```

### 3. 设置环境变量（可选）

如果你有自己的高德地图 API 密钥，可以设置环境变量：

```bash
# 设置环境变量
export AMAP_API_KEY="你的高德地图API密钥"
export AMAP_SECURITY_CODE="你的高德地图安全密钥"
```

### 4. 启动服务器

```bash
# 直接运行
python main.py

# 或者使用 uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000
```

服务器启动后，你会看到以下信息：
```
🚀 启动高德地图导航 MCP 服务器...
🔧 MCP 端点: http://localhost:8000/mcp
📚 API 文档: http://localhost:8000/docs

使用说明:
1. 使用 MCP tool 'create_session' 创建会话
2. 使用返回的 sessionid 访问地图页面
3. 使用 MCP tool 'send_navigation_to_map' 发送导航命令
```

## 🔌 API 接口

### 主要端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 获取地图页面（需要 sessionid 参数） |
| `/ws/{session_id}` | WebSocket | WebSocket 连接端点 |
| `/sessions` | GET | 查看所有活跃会话 |
| `/queue-status` | GET | 查看命令队列状态 |
| `/health` | GET | 健康检查 |
| `/mcp` | - | MCP 协议端点 |
| `/static` | GET | 静态文件服务 |

### 查看系统状态

```bash
# 查看所有会话
curl "http://localhost:8000/sessions"

# 查看命令队列状态
curl "http://localhost:8000/queue-status"

# 健康检查
curl "http://localhost:8000/health"
```

## 🗝️ 获取高德地图 API Key

1. 访问 [高德开放平台](https://lbs.amap.com/)
2. 注册账号并登录
3. 创建应用并获取 API Key
4. 在 Web 服务中启用 JavaScript API

## 🎬 使用流程

1. **设置环境变量** → （可选）设置 `AMAP_API_KEY` 和 `AMAP_SECURITY_CODE`
2. **启动服务** → 运行 `python main.py`
3. **创建会话** → 使用 MCP tool `create_session`
4. **访问地图** → 使用返回的完整链接访问地图页面（包含密钥参数）
5. **发送导航命令** → 使用 MCP tool `send_navigation_to_map`
6. **查看结果** → 地图通过 WebSocket 实时显示导航路线

## 🌟 特色功能

- **WebSocket 实时通信**：地图页面通过 WebSocket 实时接收导航命令
- **会话隔离**：每个用户有独立的地图会话和连接
- **多种导航类型**：支持驾车、骑行、步行导航
- **混合输入**：支持经纬度坐标和关键字混合使用
- **自动重连**：WebSocket 连接断开时自动重连
- **安全访问**：基于 sessionid 的访问控制
- **环境变量支持**：支持通过环境变量设置自定义 API 密钥
- **URL 参数传递**：密钥通过 URL 参数动态传递，灵活安全
- **响应式设计**：适配各种屏幕尺寸

## 📂 项目结构

```
08.amap/
├── main.py                 # 主程序文件
├── main.js                 # 客户端JavaScript文件
├── main.html              # 地图页面HTML文件
├── pyproject.toml         # 项目配置文件
├── README.md             # 项目说明文档（中文）
├── README_EN.md         # Project documentation (English)
├── README_JA.md         # プロジェクトドキュメント（日本語）
└── uv.lock              # 依赖锁定文件
```

## 🛠️ 技术栈

- **FastAPI**: 现代、快速的 Web 框架，支持 WebSocket
- **fastmcp**: MCP (Model Context Protocol) 实现
- **uvicorn**: ASGI 服务器
- **WebSocket**: 实时双向通信协议
- **高德地图 JavaScript API**: 地图、驾车、骑行、步行导航服务

## ⚠️ 注意事项

1. **🔐 安全第一**：本服务仅用于学习测试，严禁生产环境使用！
2. **🔑 密钥安全**：API 密钥通过 URL 参数传递，存在泄露风险，仅限本地使用
3. **🌐 网络要求**：需要网络连接加载地图资源
4. **🔒 会话管理**：必须先创建会话才能访问地图页面
5. **💻 浏览器兼容**：建议在现代浏览器中使用（支持 WebSocket）
6. **📍 坐标系统**：坐标使用 WGS84 坐标系统
7. **🚲 导航限制**：骑行和步行导航不支持 policy 参数
8. **🔍 搜索要求**：关键字搜索时必须提供城市信息
9. **📝 日志风险**：密钥可能被记录在各级日志中，注意清理
10. **🔒 访问控制**：确保服务只在可信网络中运行

## 🤝 贡献

欢迎提交 Issues 和 Pull Requests！

## 📄 许可证

MIT License

**免责声明**：
本项目仅用于学习和技术研究目的。使用者应当：
- 遵守高德地图API使用条款
- 不得将本项目用于商业生产环境
- 自行承担API密钥泄露等安全风险
- 确保符合当地法律法规要求

作者不承担因使用本项目而产生的任何直接或间接损失。
