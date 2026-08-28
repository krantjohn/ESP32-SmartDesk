#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
====================================================================
ESP32-S3 SmartDesk Cloud Dashboard Server (智能桌面云端数据中枢)
====================================================================
- 纯 Python 原生标准库实现，零第三方依赖，一键即跑！
- 兼容任何 Linux 云服务器 / 树莓派 / 本地环境
- 默认监听端口: 5000 (可通过命令行参数修改，例如: python3 smartdesk_server.py 80)
====================================================================
"""

import sys
import json
import time
import sqlite3
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from datetime import datetime, timezone, timedelta

# 东八区北京时间时区定义 (UTC+8)
BEIJING_TZ = timezone(timedelta(hours=8))

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
DB_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "smartdesk_data.db")

# 初始化 SQLite 数据库
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS telemetry (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        indoor_temp REAL,
        indoor_hum REAL,
        city TEXT,
        outdoor_temp REAL,
        outdoor_hum REAL,
        weather TEXT,
        reported_time TEXT,
        server_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.commit()
    conn.close()

init_db()

# 内存最新状态缓存
latest_state = {
    "device_id": "ESP32S3_SmartDesk",
    "indoor_temp": 24.5,
    "indoor_hum": 52.0,
    "city": "衡水",
    "outdoor_temp": 26.0,
    "outdoor_hum": 58.0,
    "weather": "多云",
    "last_seen": int(time.time()),
    "is_online": True,
    "total_reports": 1
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartDesk · 智能桌面云端监控中枢</title>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    <style>
        :root {
            --bg-base: #0a0e17;
            --card-bg: rgba(16, 24, 40, 0.75);
            --card-border: rgba(255, 255, 255, 0.08);
            --accent-cyan: #00f2fe;
            --accent-blue: #4facfe;
            --accent-emerald: #10b981;
            --accent-amber: #f59e0b;
            --accent-rose: #f43f5e;
            --accent-purple: #8b5cf6;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Noto Sans CJK SC", sans-serif; }
        
        body {
            background-color: var(--bg-base);
            background-image: 
                radial-gradient(at 0% 0%, rgba(0, 242, 254, 0.15) 0px, transparent 50%),
                radial-gradient(at 100% 0%, rgba(139, 92, 246, 0.15) 0px, transparent 50%),
                radial-gradient(at 50% 100%, rgba(16, 185, 129, 0.1) 0px, transparent 50%);
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            padding: 24px;
        }

        .container { max-width: 1280px; margin: 0 auto; }

        /* 顶部 Header */
        header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 24px;
            border-bottom: 1px solid var(--card-border);
            margin-bottom: 24px;
            flex-wrap: wrap;
            gap: 16px;
        }

        .header-title { display: flex; align-items: center; gap: 14px; }
        .logo-icon {
            width: 46px; height: 46px;
            background: linear-gradient(135deg, var(--accent-cyan), var(--accent-purple));
            border-radius: 14px;
            display: flex; align-items: center; justify-content: center;
            font-size: 22px; color: #fff;
            box-shadow: 0 8px 24px rgba(0, 242, 254, 0.3);
        }
        .header-title h1 { font-size: 24px; font-weight: 700; letter-spacing: -0.5px; }
        .header-title p { font-size: 13px; color: var(--text-muted); margin-top: 2px; }

        .status-pill {
            display: inline-flex; align-items: center; gap: 8px;
            padding: 8px 16px; border-radius: 30px;
            background: rgba(16, 185, 129, 0.12);
            border: 1px solid rgba(16, 185, 129, 0.3);
            color: var(--accent-emerald);
            font-size: 13px; font-weight: 600;
        }
        .pulse-dot {
            width: 8px; height: 8px; border-radius: 50%;
            background-color: var(--accent-emerald);
            box-shadow: 0 0 12px var(--accent-emerald);
            animation: pulse 2s infinite;
        }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.4; transform: scale(1.3); } }

        /* 网格布局 */
        .grid-layout {
            display: grid;
            grid-template-columns: repeat(12, 1fr);
            gap: 20px;
            margin-bottom: 24px;
        }

        .glass-card {
            background: var(--card-bg);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--card-border);
            border-radius: 20px;
            padding: 24px;
            position: relative;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s ease, border-color 0.3s ease;
        }
        .glass-card:hover { border-color: rgba(255, 255, 255, 0.2); transform: translateY(-2px); }

        .col-4 { grid-column: span 4; }
        .col-6 { grid-column: span 6; }
        .col-8 { grid-column: span 8; }
        .col-12 { grid-column: span 12; }

        @media (max-width: 1024px) {
            .col-4, .col-6, .col-8 { grid-column: span 12; }
        }

        .card-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 20px;
        }
        .card-header h3 { font-size: 15px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.5px; }
        .card-icon {
            width: 36px; height: 36px; border-radius: 10px;
            display: flex; align-items: center; justify-content: center;
            font-size: 16px;
        }

        .icon-temp { background: rgba(244, 63, 94, 0.15); color: var(--accent-rose); }
        .icon-hum { background: rgba(0, 242, 254, 0.15); color: var(--accent-cyan); }
        .icon-weather { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }

        .stat-value {
            font-size: 42px; font-weight: 800; line-height: 1;
            margin-bottom: 8px; display: flex; align-items: baseline; gap: 4px;
        }
        .stat-unit { font-size: 18px; font-weight: 500; color: var(--text-muted); }
        .stat-desc { font-size: 13px; color: var(--text-muted); display: flex; align-items: center; gap: 6px; }

        .tag {
            display: inline-block; padding: 4px 10px; border-radius: 8px;
            font-size: 12px; font-weight: 600;
        }
        .tag-good { background: rgba(16, 185, 129, 0.15); color: var(--accent-emerald); }
        .tag-warn { background: rgba(245, 158, 11, 0.15); color: var(--accent-amber); }

        /* 图表容器 */
        #chart-container { width: 100%; height: 320px; }

        /* 底部信息 */
        footer {
            text-align: center; font-size: 13px; color: var(--text-muted);
            margin-top: 36px; padding-top: 20px; border-top: 1px solid var(--card-border);
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 头部区域 -->
        <header>
            <div class="header-title">
                <div class="logo-icon"><i class="fa-solid fa-microchip"></i></div>
                <div>
                    <h1>SmartDesk · 智能桌面云端中枢</h1>
                    <p>ESP32-S3 边缘物联终端 & 实时气象环境数据大屏</p>
                </div>
            </div>
            <div id="device-status" class="status-pill">
                <div class="pulse-dot"></div>
                <span id="status-text">终端在线 · 实时通信中</span>
            </div>
        </header>

        <!-- 实时环境数据卡片 -->
        <div class="grid-layout">
            <!-- 室内温度卡片 (SHT30) -->
            <div class="glass-card col-4">
                <div class="card-header">
                    <h3>桌面室内温度 (SHT30)</h3>
                    <div class="card-icon icon-temp"><i class="fa-solid fa-temperature-half"></i></div>
                </div>
                <div class="stat-value">
                    <span id="indoor-temp">--</span><span class="stat-unit">°C</span>
                </div>
                <div class="stat-desc">
                    <span id="temp-tag" class="tag tag-good">体感适宜</span>
                    <span>高精度微环境采样</span>
                </div>
            </div>

            <!-- 室内湿度卡片 (SHT30) -->
            <div class="glass-card col-4">
                <div class="card-header">
                    <h3>桌面室内湿度 (SHT30)</h3>
                    <div class="card-icon icon-hum"><i class="fa-solid fa-droplet"></i></div>
                </div>
                <div class="stat-value">
                    <span id="indoor-hum">--</span><span class="stat-unit">%</span>
                </div>
                <div class="stat-desc">
                    <span id="hum-tag" class="tag tag-good">舒适区</span>
                    <span>室内相对湿度</span>
                </div>
            </div>

            <!-- 衡水室外气象卡片 -->
            <div class="glass-card col-4">
                <div class="card-header">
                    <h3>室外天气气象 (<span id="city-name">衡水</span>)</h3>
                    <div class="card-icon icon-weather"><i class="fa-solid fa-cloud-sun"></i></div>
                </div>
                <div class="stat-value">
                    <span id="outdoor-temp">--</span><span class="stat-unit">°C</span>
                </div>
                <div class="stat-desc">
                    <span id="weather-tag" class="tag tag-warn">多云</span>
                    <span>室外湿度: <b id="outdoor-hum">--</b>%</span>
                </div>
            </div>

            <!-- 24小时动态趋势图表 -->
            <div class="glass-card col-12">
                <div class="card-header">
                    <h3>实时温湿度动态走势 (24小时连续遥测)</h3>
                    <span style="font-size: 12px; color: var(--text-muted);">自动轮询毫秒更新 · SQLite 持久化</span>
                </div>
                <div id="chart-container"></div>
            </div>
        </div>

        <footer>
            <p>ESP32-S3 Smart Desk Cloud Station · 衡水专属数据中枢 · Power by Linux Backend</p>
        </footer>
    </div>

    <script>
        // 初始化 ECharts
        const chartDom = document.getElementById('chart-container');
        const myChart = echarts.init(chartDom);

        const option = {
            backgroundColor: 'transparent',
            tooltip: {
                trigger: 'axis',
                backgroundColor: 'rgba(16, 24, 40, 0.9)',
                borderColor: 'rgba(255, 255, 255, 0.1)',
                textStyle: { color: '#f8fafc' }
            },
            legend: {
                data: ['室内温度(°C)', '室内湿度(%)', '室外温度(°C)'],
                textStyle: { color: '#94a3b8' },
                top: 0
            },
            grid: { left: '3%', right: '4%', bottom: '3%', top: '15%', containLabel: true },
            xAxis: {
                type: 'category',
                boundaryGap: false,
                data: [],
                axisLine: { lineStyle: { color: '#334155' } },
                axisLabel: { color: '#94a3b8' }
            },
            yAxis: [
                {
                    type: 'value',
                    name: '温度 (°C)',
                    position: 'left',
                    splitLine: { lineStyle: { color: 'rgba(255, 255, 255, 0.05)' } },
                    axisLabel: { color: '#94a3b8' }
                },
                {
                    type: 'value',
                    name: '湿度 (%)',
                    position: 'right',
                    splitLine: { show: false },
                    axisLabel: { color: '#94a3b8' }
                }
            ],
            series: [
                {
                    name: '室内温度(°C)',
                    type: 'line',
                    smooth: true,
                    showSymbol: false,
                    data: [],
                    itemStyle: { color: '#f43f5e' },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(244, 63, 94, 0.3)' },
                            { offset: 1, color: 'rgba(244, 63, 94, 0.0)' }
                        ])
                    }
                },
                {
                    name: '室内湿度(%)',
                    type: 'line',
                    yAxisIndex: 1,
                    smooth: true,
                    showSymbol: false,
                    data: [],
                    itemStyle: { color: '#00f2fe' },
                    areaStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: 'rgba(0, 242, 254, 0.3)' },
                            { offset: 1, color: 'rgba(0, 242, 254, 0.0)' }
                        ])
                    }
                },
                {
                    name: '室外温度(°C)',
                    type: 'line',
                    smooth: true,
                    showSymbol: false,
                    data: [],
                    itemStyle: { color: '#f59e0b' },
                    lineStyle: { type: 'dashed' }
                }
            ]
        };
        myChart.setOption(option);
        window.addEventListener('resize', () => myChart.resize());

        // 轮询更新数据
        async function fetchTelemetry() {
            try {
                const res = await fetch('/api/latest');
                const data = await res.json();
                
                document.getElementById('indoor-temp').innerText = (data.indoor_temp || 0).toFixed(1);
                document.getElementById('indoor-hum').innerText = (data.indoor_hum || 0).toFixed(1);
                document.getElementById('outdoor-temp').innerText = (data.outdoor_temp || 0).toFixed(1);
                document.getElementById('outdoor-hum').innerText = (data.outdoor_hum || 0).toFixed(0);
                document.getElementById('city-name').innerText = data.city || '衡水';
                document.getElementById('weather-tag').innerText = data.weather || '晴';

                // 舒适度评级
                const temp = data.indoor_temp;
                const hum = data.indoor_hum;
                const tempTag = document.getElementById('temp-tag');
                if (temp < 18) { tempTag.innerText = '偏冷'; tempTag.className = 'tag tag-warn'; }
                else if (temp > 28) { tempTag.innerText = '偏热'; tempTag.className = 'tag tag-warn'; }
                else { tempTag.innerText = '体感适宜'; tempTag.className = 'tag tag-good'; }

                const humTag = document.getElementById('hum-tag');
                if (hum < 40) { humTag.innerText = '偏干燥'; humTag.className = 'tag tag-warn'; }
                else if (hum > 70) { humTag.innerText = '潮湿'; humTag.className = 'tag tag-warn'; }
                else { humTag.innerText = '舒适区'; humTag.className = 'tag tag-good'; }

                // 心跳状态
                const nowSec = Math.floor(Date.now() / 1000);
                const isOnline = (nowSec - data.last_seen) < 15;
                const statusPill = document.getElementById('device-status');
                const statusText = document.getElementById('status-text');
                if (isOnline) {
                    statusPill.style.borderColor = 'rgba(16, 185, 129, 0.3)';
                    statusPill.style.color = '#10b981';
                    statusText.innerText = 'ESP32-S3 在线 · 实时遥测中';
                } else {
                    statusPill.style.borderColor = 'rgba(244, 63, 94, 0.3)';
                    statusPill.style.color = '#f43f5e';
                    statusText.innerText = 'ESP32-S3 待机 / 等待上报';
                }

                // 获取历史图表数据
                const histRes = await fetch('/api/history');
                const histData = await histRes.json();
                
                myChart.setOption({
                    xAxis: { data: histData.times },
                    series: [
                        { data: histData.indoor_temps },
                        { data: histData.indoor_hums },
                        { data: histData.outdoor_temps }
                    ]
                });
            } catch (err) {
                console.error("Fetch error:", err);
            }
        }

        setInterval(fetchTelemetry, 3000);
        fetchTelemetry();
    </script>
</body>
</html>
"""

class SmartDeskHandler(BaseHTTPRequestHandler):
    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(status=204)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/" or parsed.path == "/index.html":
            self._set_headers(content_type="text/html; charset=utf-8")
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        elif parsed.path == "/api/latest":
            self._set_headers()
            self.wfile.write(json.dumps(latest_state, ensure_ascii=False).encode("utf-8"))
        elif parsed.path == "/api/history":
            conn = sqlite3.connect(DB_FILE)
            cursor = conn.cursor()
            cursor.execute("SELECT reported_time, indoor_temp, indoor_hum, outdoor_temp FROM telemetry ORDER BY id DESC LIMIT 40")
            rows = cursor.fetchall()
            conn.close()

            rows.reverse()
            times = [r[0] if r[0] else datetime.now(BEIJING_TZ).strftime("%H:%M:%S") for r in rows]
            indoor_temps = [r[1] for r in rows]
            indoor_hums = [r[2] for r in rows]
            outdoor_temps = [r[3] for r in rows]

            # 初始空数据垫底
            if not times:
                now_str = datetime.now(BEIJING_TZ).strftime("%H:%M:%S")
                times = [now_str]
                indoor_temps = [latest_state["indoor_temp"]]
                indoor_hums = [latest_state["indoor_hum"]]
                outdoor_temps = [latest_state["outdoor_temp"]]

            payload = {
                "times": times,
                "indoor_temps": indoor_temps,
                "indoor_hums": indoor_hums,
                "outdoor_temps": outdoor_temps
            }
            self._set_headers()
            self.wfile.write(json.dumps(payload, ensure_ascii=False).encode("utf-8"))
        else:
            self._set_headers(status=404)
            self.wfile.write(b'{"error": "Not Found"}')

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/report":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8")
            try:
                data = json.loads(body)
                indoor_temp = float(data.get("indoor_temp", 0.0))
                indoor_hum = float(data.get("indoor_hum", 0.0))
                city = str(data.get("city", "衡水"))
                outdoor_temp = float(data.get("outdoor_temp", 0.0))
                outdoor_hum = float(data.get("outdoor_hum", 0.0))
                weather = str(data.get("weather", "晴"))
                
                # 优先提取 ESP32 硬件端上报的 NTP 北京时间 (格式 "YYYY-MM-DD HH:MM:SS")
                esp_ts = str(data.get("timestamp", ""))
                if esp_ts and len(esp_ts) >= 19 and "ERROR" not in esp_ts:
                    reported_time = esp_ts[11:19]  # 提取 "HH:MM:SS"
                else:
                    reported_time = datetime.now(BEIJING_TZ).strftime("%H:%M:%S")

                latest_state["indoor_temp"] = indoor_temp
                latest_state["indoor_hum"] = indoor_hum
                latest_state["city"] = city
                latest_state["outdoor_temp"] = outdoor_temp
                latest_state["outdoor_hum"] = outdoor_hum
                latest_state["weather"] = weather
                latest_state["last_seen"] = int(time.time())
                latest_state["total_reports"] += 1

                # 插入持久化数据库
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("""
                INSERT INTO telemetry (device_id, indoor_temp, indoor_hum, city, outdoor_temp, outdoor_hum, weather, reported_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, ("ESP32S3_SmartDesk", indoor_temp, indoor_hum, city, outdoor_temp, outdoor_hum, weather, reported_time))
                conn.commit()
                conn.close()


                self._set_headers()
                self.wfile.write(json.dumps({"status": "success", "message": "Telemetry received"}, ensure_ascii=False).encode("utf-8"))
            except Exception as e:
                self._set_headers(status=400)
                self.wfile.write(json.dumps({"status": "error", "message": str(e)}).encode("utf-8"))
        else:
            self._set_headers(status=404)
            self.wfile.write(b'{"error": "Not Found"}')

if __name__ == "__main__":
    server = HTTPServer(("0.0.0.0", PORT), SmartDeskHandler)
    print(f"[SmartDesk Hub] Server running at http://0.0.0.0:{PORT}")
    print(f"[SmartDesk Hub] Open browser: http://localhost:{PORT}")
    print(f"[SmartDesk Hub] ESP32 Endpoint: http://<SERVER_IP>:{PORT}/api/report")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[SmartDesk Hub] Server stopped.")
