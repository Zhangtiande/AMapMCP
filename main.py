import json
import os
import uuid
from typing import Optional, List, Union, Dict
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP
from pydantic import BaseModel, Field

# 从环境变量读取高德地图密钥
AMAP_API_KEY = os.getenv("AMAP_API_KEY")
AMAP_SECURITY_CODE = os.getenv("AMAP_SECURITY_CODE")
if not AMAP_API_KEY or not AMAP_SECURITY_CODE:
    raise ValueError("AMAP_API_KEY 和 AMAP_SECURITY_CODE 必须设置")

# 存储会话信息
mcp_session_ws_dict: Dict[str, WebSocket] = {}
# 存储每个会话的导航命令队列
session_navigation_queues: Dict[str, List] = {}


class NavigationPoint(BaseModel):
    # 经纬度方式
    lng: Optional[float] = Field(default=None, description="经度")
    lat: Optional[float] = Field(default=None, description="纬度")
    
    # 关键字方式
    keyword: Optional[str] = Field(default=None, description="地点关键词")
    city: Optional[str] = Field(default=None, description="城市名称")


class NavigationCommand(BaseModel):
    points: List[NavigationPoint] = Field(description="导航点列表，支持经纬度和关键字混合")
    policy: int = Field(default=0, description="驾车路线规划策略，0是速度优先的策略")
    nav_type: str = Field(default="driving", description="导航类型：driving(驾车), riding(骑行), walking(步行)")


# 创建 FastAPI 应用
app = FastAPI(title="AMap Navigation MCP Server")

# 创建 MCP 实例
mcp = FastMCP("AMap Navigation")


@app.get("/", response_class=HTMLResponse)
async def get_map_page(request: Request):
    """提供高德地图导航页面"""
    try:
        # 获取 sessionid 参数
        session_id = request.query_params.get("sessionid")
        
        if not session_id:
            return HTMLResponse(
                content="""
                <html>
                <head>
                    <title>访问被拒绝</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; }
                    </style>
                </head>
                <body>
                    <h1 class="error">访问被拒绝</h1>
                    <p>请先通过 MCP 服务获取 sessionid 才能访问地图页面</p>
                </body>
                </html>
                """,
                status_code=403
            )
        
        # 验证 sessionid 是否有效
        if session_id not in session_navigation_queues:
            return HTMLResponse(
                content="""
                <html>
                <head>
                    <title>会话无效</title>
                    <style>
                        body { font-family: Arial, sans-serif; text-align: center; padding: 50px; }
                        .error { color: red; }
                    </style>
                </head>
                <body>
                    <h1 class="error">会话无效</h1>
                    <p>无效的 sessionid 或会话已过期</p>
                </body>
                </html>
                """,
                status_code=401
            )
        
        # 读取HTML文件
        html_file_path = "main.html"
        with open(html_file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        return HTMLResponse(content=html_content)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="HTML文件不存在")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取HTML文件失败: {str(e)}")


@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket 端点，用于实时通信"""
    await websocket.accept()
    
    # 存储 WebSocket 连接
    mcp_session_ws_dict[session_id] = websocket
    
    # 初始化会话的导航命令队列
    if session_id not in session_navigation_queues:
        session_navigation_queues[session_id] = []
    
    print(f"WebSocket 连接已建立，会话 ID: {session_id}")
    
    try:
        while True:
            # 保持连接活跃
            await websocket.receive_text()
    except WebSocketDisconnect:
        # 清理会话信息
        if session_id in mcp_session_ws_dict:
            del mcp_session_ws_dict[session_id]
        print(f"WebSocket 连接已断开，会话 ID: {session_id}")


async def send_navigation_to_session(session_id: str, command: dict):
    """向指定会话发送导航命令"""
    if session_id in mcp_session_ws_dict:
        websocket = mcp_session_ws_dict[session_id]
        try:
            await websocket.send_text(json.dumps({
                "type": "navigation",
                "command": command
            }))
            return True
        except Exception as e:
            print(f"发送导航命令失败: {e}")
            # 如果发送失败，移除无效连接
            if session_id in mcp_session_ws_dict:
                del mcp_session_ws_dict[session_id]
            return False
    return False


@app.get("/navigation-command")
async def get_navigation_command():
    """获取待执行的导航命令（保留兼容性）"""
    # 这个端点保留用于向后兼容
    return {"command": None}


@app.post("/send-navigation")
async def send_navigation_command(command: NavigationCommand):
    """接收并存储导航命令（保留兼容性）"""
    return {"message": "请使用 MCP 工具发送导航命令", "command": command}


@mcp.tool()
def create_session() -> str:
    """
    创建新的地图会话
    
    返回一个 sessionid，用于访问地图页面。
    每个会话都是独立的，支持多用户同时使用。
    """
    session_id = str(uuid.uuid4())
    # 预先创建会话条目，但不创建 WebSocket 连接
    session_navigation_queues[session_id] = []
    
    return f"会话已创建，sessionid: {session_id}\n" \
           f"请先引导用户访问: http://localhost:8000?sessionid={session_id}&apikey={AMAP_API_KEY}&securitycode={AMAP_SECURITY_CODE}\n" \
           f"然后使用 MCP tool 'send_navigation_to_map' 发送导航命令"


@mcp.tool()
async def send_navigation_to_map(
    session_id: str = Field(description="会话 ID"),
    points: List[dict] = Field(description="导航点列表，每个点可以包含lng/lat（经纬度）或keyword/city（关键字）字段"),
    policy: int = Field(default=0, description="驾车路线规划策略，0是速度优先的策略"),
    nav_type: str = Field(default="driving", description="导航类型：driving(驾车), riding(骑行), walking(步行)")
) -> str:
    """
    向指定会话的高德地图发送导航命令
    
    支持灵活的点位格式：
    - 经纬度格式：{"lng": 116.379028, "lat": 39.865042}
    - 关键字格式：{"keyword": "北京站", "city": "北京"}
    - 混合使用：起点用经纬度，终点用关键字等
    
    导航类型：
    - driving: 驾车导航（默认，支持 policy 参数）
    - riding: 骑行导航（不支持 policy 参数）
    - walking: 步行导航（不支持 policy 参数）
    
    示例：
    - 纯经纬度：[{"lng": 116.379028, "lat": 39.865042}, {"lng": 116.427281, "lat": 39.903719}]
    - 纯关键字：[{"keyword": "北京站", "city": "北京"}, {"keyword": "天安门", "city": "北京"}]
    - 混合使用：[{"lng": 116.379028, "lat": 39.865042}, {"keyword": "天安门", "city": "北京"}]
    
    请确保已创建会话并且地图页面已经打开。
    """
    # 验证会话 ID
    if session_id not in session_navigation_queues:
        raise ValueError(f"无效的会话 ID: {session_id}")
    
    # 验证导航类型
    valid_nav_types = ["driving", "riding", "walking"]
    if nav_type not in valid_nav_types:
        raise ValueError(f"无效的导航类型: {nav_type}，支持的类型: {valid_nav_types}")
    
    # 验证输入参数
    if not points or len(points) < 2:
        raise ValueError("至少需要提供2个点（起点和终点）")
    
    # 验证每个点的格式
    navigation_points = []
    for i, point in enumerate(points):
        nav_point = NavigationPoint(**point)
        
        # 检查点的有效性
        has_coords = nav_point.lng is not None and nav_point.lat is not None
        has_keyword = nav_point.keyword is not None
        
        if not has_coords and not has_keyword:
            raise ValueError(f"第{i+1}个点必须包含经纬度(lng/lat)或关键字(keyword)信息")
        
        if has_keyword and nav_point.city is None:
            raise ValueError(f"第{i+1}个点使用关键字时必须提供城市信息")
            
        navigation_points.append(nav_point)
    
    command = NavigationCommand(
        points=navigation_points,
        policy=policy,
        nav_type=nav_type
    )
    
    await send_navigation_to_session(session_id, command.dict())
    
    # 生成描述信息
    point_descriptions = []
    for i, point in enumerate(navigation_points):
        if point.lng is not None and point.lat is not None:
            point_descriptions.append(f"点{i+1}: ({point.lng}, {point.lat})")
        else:
            point_descriptions.append(f"点{i+1}: {point.keyword}({point.city})")
    
    nav_type_names = {"driving": "驾车", "riding": "骑行", "walking": "步行"}
    result_msg = f"导航命令已发送到会话 {session_id}\n导航类型：{nav_type_names.get(nav_type, nav_type)}\n{chr(10).join(point_descriptions)}\n策略：{policy}"
    
    return result_msg


@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "ok", "service": "AMap Navigation MCP Server"}


@app.get("/queue-status")
async def get_queue_status():
    """查看导航命令队列状态"""
    return {
        "active_sessions": len(mcp_session_ws_dict),
        "session_queues": {k: len(v) for k, v in session_navigation_queues.items()}
    }


@app.get("/sessions")
async def get_sessions():
    """获取所有活跃会话"""
    return {
        "active_sessions": list(mcp_session_ws_dict.keys()),
        "total_sessions": len(session_navigation_queues)
    }


# 将 MCP 集成到 FastAPI 应用
app.mount("/mcp", mcp.http_app(transport="sse"))

# 提供静态文件服务
app.mount("/static", StaticFiles(directory="."), name="static")


def main():
    import uvicorn
    print("🚀 启动高德地图导航 MCP 服务器...")
    print("🔧 MCP 端点: http://localhost:8000/mcp")
    print("📚 API 文档: http://localhost:8000/docs")
    print("\n⚠️  重要安全警告:")
    print("🔒 本服务仅用于学习测试，严禁在生产环境中使用！")
    print("🔑 API 密钥通过 URL 参数传递，存在泄露风险")
    print("🌐 请确保仅在本地安全环境中运行")
    print("📝 注意清理包含密钥的日志文件")
    print("\n使用说明:")
    print("1. 使用 MCP tool 'create_session' 创建会话")
    print("2. 使用返回的完整链接访问地图页面（包含密钥参数）")
    print("3. 使用 MCP tool 'send_navigation_to_map' 发送导航命令")
    print("4. 支持驾车(driving)、骑行(riding)、步行(walking)三种导航类型")
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    main()
