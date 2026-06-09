# 🍅 Pomodoro Timer — 桌面番茄钟

一个基于 **番茄工作法** 的桌面计时器应用，使用 Python + PySide6 (Qt for Python) 构建。

> 番茄工作法：25 分钟专注工作 → 5 分钟短休息 → 每 4 个番茄后长休息 15 分钟。

---

## ✨ 功能

- ⏱ **三阶段计时** — 工作 / 短休息 / 长休息，自动循环切换
- ▶️ **完整计时控制** — 开始、暂停、继续、重置、跳过
- 🔔 **桌面通知** — 阶段完成时弹出系统托盘消息 + 窗口闪烁提示
- 🖥 **系统托盘** — 关闭窗口自动最小化到托盘，后台静默运行
- 📊 **每日统计** — 自动记录每天完成的番茄数量，帮你看清自己的节奏
- ⚙️ **可自定义** — 工作时长 / 短休息 / 长休息 / 长休息间隔，全部可调
- 📌 **总在最前** — 可让窗口始终保持在其他窗口之上
- 🖼 **单实例运行** — 只能启动一个实例，重复启动会激活已有窗口
- 🪟 **Windows 原生体验** — 自定义任务栏图标 (AppUserModelID)、可打包为独立 `.exe`

## 📸 截图

| 主界面 | 设置 |
|-------|------|
| ![主界面](screenshots/main.png) | ![设置](screenshots/settings.png) |

> 截图目录 `screenshots/` 尚未添加，可自行截取后放入。

---

## 📦 安装

### 环境要求

- Python **3.11+**
- 操作系统：Windows（当前版本主要面向 Windows；托盘等特性依赖平台）

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/your-username/pomodoro.git
cd pomodoro

# 2. 安装依赖
pip install -r requirements.txt

# 3. 启动
python main.py
```

### 一键启动（Windows）

打包后双击 **`dist\Pomodoro.exe`** 即可运行，无需安装 Python 环境。

开发阶段可双击 **`main.pyw`** — `.pyw` 后缀会自动用 `pythonw.exe` 运行，不会弹出命令行窗口。

---

## 🚀 使用指南

### 基本操作

| 操作 | 说明 |
|------|------|
| **🍅 工作 / ☕ 休息 / ☕ 长休** | 切换阶段（仅闲置时可手动切换） |
| **▶ 开始** | 开始倒计时；运行中点击变为暂停 |
| **⏸ 暂停 / ▶ 继续** | 暂停或恢复倒计时 |
| **◀ 重置** | 重置当前阶段倒计时 |
| **跳过 ▶** | 跳过当前阶段，进入下一阶段 |
| **文件 → 设置** | 打开设置对话框 |
| **文件 → 总在最前** | 切换窗口置顶 |
| **关闭窗口** | 最小化到系统托盘（不会退出） |
| **托盘右键 → 退出程序** | 完全退出应用 |

### 阶段循环

```
工作(25min) → 短休息(5min) → 工作(25min) → 短休息(5min) → 
工作(25min) → 短休息(5min) → 工作(25min) → 长休息(15min) → 
回到第一组 🔄
```

每完成一个工作时段记作 1 个🍅，完成后自动进入下一阶段。

---

## ⚙️ 自定义设置

在 **设置对话框** 中可调整：

| 设置项 | 默认值 | 范围 |
|--------|--------|------|
| 工作时间 | 25 分钟 | 1–120 |
| 短休息 | 5 分钟 | 1–60 |
| 长休息 | 15 分钟 | 1–120 |
| 长休息间隔 | 4 个番茄 | 1–20 |
| 窗口总在最前 | 关 | 开关 |
| 完成时播放提示音 | 开 | 开关 |
| 开始计时时自动最小化到托盘 | 关 | 开关 |

设置会自动保存到 `data/settings.json`。

---

## 📁 项目结构

```
Pomodoro/
├── main.py                  # 入口（带控制台）
├── main.pyw                 # 入口（无控制台窗口）
├── requirements.txt         # 依赖：PySide6>=6.6
├── .gitignore
│
├── dist/                    # 打包输出（首次构建后生成）
│   └── Pomodoro.exe         # 独立可执行文件
│
├── data/                    # 运行时数据（自动生成）
│   ├── settings.json        # 用户设置
│   └── stats.json           # 每日统计数据
│
└── src/
    ├── app_main.py          # QApplication 初始化、图标加载
    ├── single_instance.py   # 单实例 IPC（QLocalServer）
    │
    ├── resources/
    │   ├── tomato.png       # 番茄图标（PNG）
    │   └── tomato.ico       # 番茄图标（ICO，用于窗口/任务栏）
    │
    ├── timer/
    │   ├── state.py         # TimerState / Phase 枚举
    │   └── worker.py        # 倒计时核心逻辑（QTimer）
    │
    ├── ui/
    │   ├── main_window.py   # 主窗口 UI
    │   ├── settings_dialog.py # 设置对话框
    │   └── styles.py        # QSS 样式表
    │
    └── storage/
        ├── settings.py      # 设置持久化（JSON）
        └── stats.py         # 统计持久化（JSON）
```

### 架构说明

- **单例模式** — `SettingsManager` 和 `StatsManager` 均为单例，避免重复加载
- **信号/槽** — `TimerWorker` 通过 Qt 信号与 UI 层解耦
- **QSS 主题** — 纯 QSS 样式，无额外 CSS 框架依赖
- **单实例** — 基于 `QLocalServer/QLocalSocket` 实现 IPC

---

## 🔧 开发

```bash
# 克隆仓库
git clone https://github.com/your-username/pomodoro.git
cd pomodoro

# 创建虚拟环境（可选但推荐）
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows

# 安装开发依赖
pip install -r requirements.txt

# 启动
python main.py
```

---

## 📄 许可证

本项目为开源软件，基于 [MIT License](LICENSE) 发布。

---

## 💡 关于番茄工作法

> 番茄工作法（Pomodoro Technique）是由 Francesco Cirillo 在 1980 年代末提出的时间管理方法。
>
> 核心理念：将工作时间分割成 25 分钟的「番茄时段」，每个时段之间穿插短休息，每 4 个番茄后进行一次长休息。这种方法有助于保持专注、避免疲劳，并让工作进度变得可量化。

---

**用 🍅 记录每一个专注的时刻。**
