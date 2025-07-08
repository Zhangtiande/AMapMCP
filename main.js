let map = null;
let apiKey = null;
let ws = null;
let sessionId = null;

// 从 URL 参数获取 sessionid
function getSessionIdFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('sessionid');
}

// 从 URL 参数获取 API 密钥
function getApiKeyFromUrl() {
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get('apikey');
}

// 初始化地图
function initMap() {
    // 动态加载高德地图API
    const script = document.createElement('script');
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${apiKey}&plugin=AMap.Driving,AMap.Riding,AMap.Walking`;
    script.onload = function() {
        // 创建地图实例
        map = new AMap.Map("container", {
            resizeEnable: true,
            center: [116.397428, 39.90923],
            zoom: 13
        });
        
        console.log('地图初始化完成');
        showStatus('地图初始化完成');
    };
    script.onerror = function() {
        alert('地图加载失败，请检查API Key');
    };
    document.head.appendChild(script);
}

// 显示状态信息
function showStatus(message) {
    const status = document.getElementById('status');
    status.textContent = message;
    status.style.display = 'block';
    setTimeout(() => {
        status.style.display = 'none';
    }, 3000);
}

// 转换导航点为高德地图格式
function convertNavigationPoint(point) {
    if (point.lng !== null && point.lat !== null) {
        // 经纬度格式
        return new AMap.LngLat(point.lng, point.lat);
    } else if (point.keyword) {
        // 关键字格式
        return point.city ? {keyword: point.keyword, city: point.city} : point.keyword;
    }
    throw new Error('无效的导航点格式');
}

// 执行导航
function performNavigation(points, policy = 0, navType = 'driving') {
    if (!map) {
        throw new Error('地图未初始化');
    }
    
    if (!points || points.length < 2) {
        throw new Error('至少需要2个导航点');
    }
    
    // 根据导航类型选择对应的插件
    let pluginName = "AMap.Driving";
    let navigationOptions = {
        policy: policy,
        map: map,
        panel: "panel"
    };
    
    switch (navType) {
        case 'driving':
            pluginName = "AMap.Driving";
            break;
        case 'riding':
            pluginName = "AMap.Riding";
            // 骑行导航不需要 policy 参数
            navigationOptions = {
                map: map,
                panel: "panel"
            };
            break;
        case 'walking':
            pluginName = "AMap.Walking";
            // 步行导航不需要 policy 参数
            navigationOptions = {
                map: map,
                panel: "panel"
            };
            break;
        default:
            throw new Error(`不支持的导航类型: ${navType}`);
    }
    
    // 使用插件方式创建导航
    AMap.plugin(pluginName, function () {
        let navigation;
        
        switch (navType) {
            case 'driving':
                navigation = new AMap.Driving(navigationOptions);
                break;
            case 'riding':
                navigation = new AMap.Riding(navigationOptions);
                break;
            case 'walking':
                navigation = new AMap.Walking(navigationOptions);
                break;
        }
        
        try {
            // 转换所有导航点
            const convertedPoints = points.map(point => convertNavigationPoint(point));
            // 多个点，使用途径点模式
            navigation.search(convertedPoints, function(status, result) {
                handleNavigationResult(status, result, points.length, navType);
            });
            
        } catch (error) {
            console.error('导航点转换失败:', error);
            showStatus('导航点转换失败: ' + error.message);
        }
    });
}

// 处理导航结果
function handleNavigationResult(status, result, pointCount, navType = 'driving') {
    const navTypeNames = {
        'driving': '驾车',
        'riding': '骑行',
        'walking': '步行'
    };
    
    const navTypeName = navTypeNames[navType] || navType;
    
    if (status === 'complete') {
        console.log(`${navTypeName}导航路线规划完成`);
        showStatus(`${navTypeName}导航路线规划完成（${pointCount}个点）`);
    } else {
        console.error(`${navTypeName}导航路线规划失败：`, result);
        showStatus(`${navTypeName}导航路线规划失败`);
    }
}

// 处理导航命令
function handleNavigationCommand(command) {
    try {
        if (command.points && command.points.length > 0) {
            performNavigation(
                command.points, 
                command.policy || 0, 
                command.nav_type || 'driving'
            );
        } else {
            console.error('导航命令缺少点位信息');
            showStatus('导航命令缺少点位信息');
        }
    } catch (error) {
        console.error('导航执行失败:', error);
        showStatus('导航执行失败: ' + error.message);
    }
}

// 初始化 WebSocket 连接
function initWebSocket() {
    if (!sessionId) {
        showStatus('缺少 sessionid 参数');
        return;
    }
    
    // 构建 WebSocket URL
    const wsUrl = `ws://localhost:8000/ws/${sessionId}`;
    
    ws = new WebSocket(wsUrl);
    
    ws.onopen = function(event) {
        console.log('WebSocket 连接已建立');
        showStatus('已连接到导航服务');
    };
    
    ws.onmessage = function(event) {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'navigation' && data.command) {
                handleNavigationCommand(data.command);
            }
        } catch (error) {
            console.error('处理 WebSocket 消息失败:', error);
        }
    };
    
    ws.onclose = function(event) {
        console.log('WebSocket 连接已关闭');
        showStatus('与导航服务的连接已断开');
        // 尝试重新连接
        setTimeout(initWebSocket, 5000);
    };
    
    ws.onerror = function(error) {
        console.error('WebSocket 错误:', error);
        showStatus('WebSocket 连接错误');
    };
}

// 页面加载完成后初始化
window.onload = function() {
    // 获取 sessionid 和 apiKey
    sessionId = getSessionIdFromUrl();
    apiKey = getApiKeyFromUrl();
    
    if (!sessionId) {
        showStatus('错误：缺少 sessionid 参数');
        return;
    }
    
    // 初始化地图
    initMap();
    
    // 初始化 WebSocket 连接
    initWebSocket();
};

// 页面关闭时关闭 WebSocket 连接
window.onbeforeunload = function() {
    if (ws) {
        ws.close();
    }
}; 
