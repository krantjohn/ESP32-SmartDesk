# ESP32-S3 SmartDesk (智能桌面多功能小终端) 🖥️

<p align="center">
  <a href="https://www.espressif.com/en/products/socs/esp32-s3"><img src="https://img.shields.io/badge/SoC-ESP32--S3-E7352C?logo=espressif&logoColor=white&style=flat-square" alt="ESP32-S3"></a>
  <a href="https://www.freertos.org/"><img src="https://img.shields.io/badge/RTOS-FreeRTOS-brightgreen?style=flat-square" alt="FreeRTOS"></a>
  <a href="https://platformio.org/"><img src="https://img.shields.io/badge/PlatformIO-Compatible-orange?logo=platformio&logoColor=white&style=flat-square" alt="PlatformIO"></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-blue.svg?style=flat-square" alt="License: MIT"></a>
</p>

<p align="center">
  <b>⚡ A feature-rich ESP32-S3 smart desktop terminal featuring FreeRTOS dual-task architecture, OLED telemetry UI, environmental sensing & cloud dashboard.</b><br>
  <i>基于 ESP32-S3 的高完成度桌面智能交互终端：集成了高精度环境温湿度、NTP 网络授时、动态天气查询、多级菜单状态机与轻量级 Python 数据大屏。</i>
</p>

---

## 🌟 核心特性

- **🌡️ 高精度环境温湿度监测**：通过 I2C 总线挂载 SHT30 传感器（地址 `0x44`），定期低抖动采集并刷新当前室内温度与湿度。
- **🌦️ WiFi 自动联网与实时天气**：
  - 具备 WiFi 自动连接与掉线指数退避重连机制；
  - 结合 `HTTPClient` 与 `ArduinoJson` 高性能解析聚合天气 RESTful API，获取实时天气现象、室外温度与湿度。
- **⏰ NTP 网络高精度授时**：开机联网后自动同步 NTP 时间服务器（东八区 UTC+8），精准计算并格式化显示年月日、星期与时分秒。
- **📋 模块化多级菜单与页面状态机**：
  - 基于 `U8g2` 驱动 128×64 SSD1306 OLED 屏幕，内嵌点阵中文字库；
  - 包含 **主页 (Home)**、**主菜单 (Menu)**、**室内环境 (Sensor)**、**天气详情 (Weather)**、**系统状态 (System)** 5 大页面；
  - 系统页面支持查看 ESP32 芯片型号、当前可用 RAM（Free Heap）及开机运行时间（$hh:mm:ss$）。
- **🎛️ 双模交互输入系统 (按键 + 旋转编码器)**：
  - **4 按键支持**：上翻 (UP)、下翻 (DOWN)、确认 (OK)、返回 (BACK)；
  - **EC11 旋转编码器支持**：内置 16 状态正交编码状态机，支持顺逆时针无级旋钮平滑翻页与导航。
- **📊 云端大屏联动与时序遥测 (`server/smartdesk_server.py`)**：
  - ESP32-S3 硬件端定时通过 HTTP POST 自动将传感器温湿度、天气、状态与授时上报至云端中枢；
  - 配套 **零依赖、极轻量** 的 Python 原生 Web 数据大屏，支持暗黑极客风可视化 UI、实时折线图走势、硬件在线心跳监测以及 SQLite 历史数据持久化存储。
- **⚡ FreeRTOS 双核多任务调度架构**：
  - **Core 0 (网络与 I/O 任务)**：专职处理 WiFi 重连、HTTP 天气拉取、NTP 授时与云端遥测上报，网络抖动绝不阻塞界面；
  - **Core 1 (UI 渲染与交互任务)**：以 30~60FPS 高刷新率处理按键消抖、EC11 旋转编码器脉冲捕获与 OLED 页面渲染；
  - **跨核心通信**：采用 FreeRTOS 队列 (`QueueHandle_t`) 与互斥量保障状态安全同步，界面丝滑无卡顿。

---

## 🏗️ FreeRTOS 双核任务划分模型

```text
┌────────────────────────────────────────────────────────┐
│                      ESP32-S3 双核架构                  │
├────────────────────────────┬───────────────────────────┤
│    Core 0: 通信与遥测任务    │     Core 1: 渲染与交互     │
│   (vTaskNetwork & Telemetry)│    (vTaskUI & Input Loop) │
├────────────────────────────┼───────────────────────────┤
│  • WiFi 掉线检测与自动重连   │  • EC11 旋转编码器状态机  │
│  • NTP 时间同步校准        │  • 按键长短按去抖动检测   │
│  • 聚合天气 REST API 拉取  │  • U8g2 页面与菜单渲染    │
│  • SQLite 云端数据上报     │  • 平滑光标动画更新       │
└─────────────┬──────────────┴─────────────▲─────────────┘
              │       FreeRTOS 状态队列     │
              └───────── Queue / Mutex ─────┘
```

---

## 🛠️ 硬件与引脚分配 (Pinout)

### 1. I2C 总线（OLED 屏幕 & SHT30 传感器共用）
| 设备 | ESP32-S3 引脚 | 说明 |
| :--- | :--- | :--- |
| **SDA** | `GPIO 5` | I2C 数据线（默认上拉） |
| **SCL** | `GPIO 4` | I2C 时钟线 |
| **VCC / GND** | `3V3 / GND` | 模块供电（3.3V） |

### 2. 交互输入引脚
| 功能 | ESP32-S3 引脚 | 类型 | 说明 |
| :--- | :--- | :--- | :--- |
| **KEY_UP** | `GPIO 9` | 内部上拉输入 | 向上翻页 / 菜单前一项 |
| **KEY_DOWN** | `GPIO 10` | 内部上拉输入 | 向下翻页 / 菜单后一项 |
| **KEY_OK** | `GPIO 11` | 内部上拉输入 | 确认进入菜单 / 子页面 |
| **KEY_BACK** | `GPIO 12` | 内部上拉输入 | 返回上一级页面 |
| **ENC_A** | `GPIO 35` | 内部上拉输入 | 编码器 A 相 |
| **ENC_B** | `GPIO 36` | 内部上拉输入 | 编码器 B 相 |
| **ENC_SW** | `GPIO 37` | 内部上拉输入 | 编码器中键按压 |

---

## 🏗️ 页面状态机与流转逻辑

```mermaid
stateDiagram-v2
    [*] --> HOME_PAGE: 系统开机
    
    HOME_PAGE --> MENU_PAGE: 按下 KEY_OK
    MENU_PAGE --> HOME_PAGE: 按下 KEY_BACK
    
    state MENU_PAGE {
        [*] --> 室内环境
        室内环境 --> 天气信息: 编码器顺时针 / KEY_DOWN
        天气信息 --> 系统状态: 编码器顺时针 / KEY_DOWN
        系统状态 --> 室内环境: 编码器顺时针 / KEY_DOWN
    }
    
    MENU_PAGE --> SENSOR_PAGE: 选中 [室内环境] + KEY_OK
    SENSOR_PAGE --> MENU_PAGE: 按下 KEY_BACK
    
    MENU_PAGE --> WEATHER_PAGE: 选中 [天气信息] + KEY_OK
    WEATHER_PAGE --> MENU_PAGE: 按下 KEY_BACK
    
    MENU_PAGE --> SYSTEM_PAGE: 选中 [系统状态] + KEY_OK
    SYSTEM_PAGE --> MENU_PAGE: 按下 KEY_BACK
```

---

## 📁 目录结构

```text
SmartDesk/
├── .gitignore              # Git 忽略规则
├── platformio.ini          # PlatformIO 构建与库依赖配置
├── README.md               # 项目详细说明文档
├── LICENSE                 # MIT 开源协议
├── server/                 # 云端大屏与数据中枢 (Python 原生轻量服务)
│   └── smartdesk_server.py # 独立 Web 大屏服务 (SQLite + REST API + 极客仪表盘)
├── include/                # 头文件目录
└── src/
    ├── config.h            # 全局引脚、WiFi、天气 API、云端上报等集中配置
    ├── main.cpp            # 主循环任务调度与定时器轮询
    ├── system_state.h/.cpp # 全局状态单例 (SystemState)
    ├── uploader.h/.cpp     # ESP32 云端数据上报模块 (HTTPClient + JSON)
    ├── display.h/.cpp      # U8g2 OLED 页面渲染与文字排版
    ├── page.h/.cpp         # 页面导航与状态机跳转控制
    ├── menu.h/.cpp         # 菜单条目与高亮游标渲染
    ├── input.h/.cpp        # 按键与 EC11 编码器消抖状态机
    ├── sensor.h/.cpp       # SHT30 驱动与数据采集
    ├── wifilink.h/.cpp     # WiFi 状态监测与自动连接
    ├── weather.h/.cpp      # 聚合数据天气 API 请求与 JSON 解析
    └── time_manager.h/.cpp # NTP 网络授时与时间格式化
```

---

## 🚀 快速上手 (Getting Started)

### 1. 配置个人凭据
在编译前，打开 [`src/config.h`](src/config.h) 修改你的 WiFi、天气 API 及云端上报配置：

```cpp
// 1. 设置 WiFi 账号密码
#define DEFAULT_WIFI_SSID "你的WiFi名称"
#define DEFAULT_WIFI_PASS "你的WiFi密码"

// 2. 设置天气城市与 API Key (可在聚合数据免费申请)
#define WEATHER_CITY      "衡水"
#define WEATHER_API_KEY   "你的聚合数据API_KEY"

// 3. 设置云端数据大屏上报地址 (支持公网服务器 IP/域名 或 本地电脑局域网 IP)
#define SERVER_UPLOAD_URL "http://YOUR_SERVER_IP:5000/api/report"
#define SERVER_UPLOAD_INTERVAL_MS 5000
```

### 2. 编译与烧录固件
1. 使用 VS Code 打开 `SmartDesk` 目录；
2. 安装 PlatformIO 扩展；
3. 点击底部状态栏的 **Build (✓)** 编译，连接 ESP32-S3 开发板后点击 **Upload (→)** 烧录。

### 3. 启动云端数据大屏 (可选)
在云服务器或本地电脑上运行大屏服务（纯 Python 标准库，零安装依赖）：
```bash
# 启动服务 (默认端口 5000，可自定义)
python3 server/smartdesk_server.py 5000
```
启动后在浏览器打开 `http://<服务器IP>:5000` 即可实时查看桌面终端的温湿度折线、天气同步状态与硬件心跳！

---

## 🔮 后续规划 (Roadmap)

- [x] **云端 Web 数据大屏与时序存储**：ESP32 实时遥测数据 HTTP 上报与仪表盘展示。
- [x] **FreeRTOS 多任务调度架构**：双核任务隔离（Core 0 网络/传感器 + Core 1 渲染/按键）。
- [ ] **WebServer 网页配网**：支持开机 AP 模式 Web 网页配置 WiFi 与城市，无需重新编译固件。
- [ ] **番茄钟 / 倒计时小工具**：增加专注时钟与蜂鸣器提醒。
- [ ] **PC 硬件监视器 (AIDA64 联动)**：通过串口或 BLE 接收电脑 CPU/GPU 温度与占用率并展示。

---

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源。


