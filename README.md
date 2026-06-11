# 🍅 Pomodoro Timer — 桌面番茄钟

[![GitHub Release](https://img.shields.io/github/v/release/daihongzhang/Pomodoro?style=flat&label=下载)](https://github.com/daihongzhang/Pomodoro/releases/latest)

一个基于 **番茄工作法** 的桌面计时器应用，使用 Python + PySide6 (Qt for Python) 构建。

> 番茄工作法：25 分钟专注工作 → 5 分钟短休息 → 每 4 个番茄后长休息 15 分钟。

---

## 📥 快速下载

前往 [Releases 页面](https://github.com/daihongzhang/Pomodoro/releases/latest) 下载 **Pomodoro.exe**，直接双击运行，无需安装任何环境。

数据自动保存在 `%APPDATA%\Pomodoro Timer\` 目录，卸载时清理即可。

## ✨ 功能

- ⏱ **三阶段计时** — 工作 / 短休息 / 长休息，自动循环切换
- ▶️ **完整计时控制** — 开始、暂停、继续、重置、跳过
- 🔔 **桌面通知** — 阶段完成时弹出系统托盘消息 + 窗口闪烁提示
- 🔊 **完成提示音** — 阶段完成时播放 Windows 系统提示音，可在设置中关闭
- 🖥 **系统托盘** — 关闭窗口默认最小化到托盘，后台静默运行
- 📊 **每日统计** — 自动记录每天完成的番茄数量
- ⚙️ **可自定义** — 工作时长 / 短休息 / 长休息 / 长休息间隔，全部可调
- 📌 **总在最前** — 可让窗口始终保持在其他窗口之上
- 🪟 **关闭按钮行为** — 可选择「最小化到托盘 / 退出程序 / 每次询问」
- 🖼 **单实例运行** — 只能启动一个实例，重复启动会激活已有窗口
- 🪟 **Windows 原生体验** — 自定义任务栏图标 (AppUserModelID)

## 📸 截图

| 主界面 | 设置 |
|-------|------|
| ![主界面](screenshots/main.png) | ![设置](screenshots/settings.png) |

> 截图目录 `screenshots/` 尚未添加，可自行截取后放入。

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
| **关闭窗口** | 最小化到托盘（可在设置中修改行为） |
| **托盘右键 → 退出程序** | 完全退出应用 |

### 阶段循环

```
工作(25min) → 短休息(5min) → 工作(25min) → 短休息(5min) → 
工作(25min) → 短休息(5min) → 工作(25min) → 长休息(15min) → 
回到第一组 🔄
```

每完成一个工作时段记作 1 个🍅，完成后自动进入下一阶段。

---

## ⚙️ 设置

在 **设置对话框**（文件 → 设置）中可调整：

| 设置项 | 默认值 | 说明 |
|--------|--------|------|
| 工作时间 | 25 分钟 | 范围 1–120 分钟 |
| 短休息 | 5 分钟 | 范围 1–60 分钟 |
| 长休息 | 15 分钟 | 范围 1–120 分钟 |
| 长休息间隔 | 4 个番茄 | 范围 1–20 |
| 窗口总在最前 | 关 | 开启后窗口始终置顶 |
| 完成时播放提示音 | 开 | 使用 Windows 系统提示音 |
| 开始计时时自动最小化到托盘 | 关 | 开启后点击「开始」自动隐藏 |
| 点击关闭按钮时 | 每次询问 | 可选「最小化到托盘 / 退出程序 / 每次询问」 |

设置自动保存，exe 打包模式下存储于 `%APPDATA%\Pomodoro Timer\settings.json`。

---

## 🔧 从源码构建

### 环境要求

- Python **3.11+**
- Windows（当前版本主要面向 Windows；托盘等特性依赖平台）

### 安装 & 运行

```bash
git clone https://github.com/daihongzhang/Pomodoro.git
cd Pomodoro

pip install -r requirements.txt

python main.py
```

开发阶段也可双击 **`main.pyw`** — `.pyw` 后缀自动用 `pythonw.exe` 运行，无控制台窗口。

### 自行打包 exe

```bash
pip install pyinstaller

pyinstaller --onefile --windowed --name "Pomodoro" ^
    --icon "src/resources/tomato.ico" ^
    --add-data "src/resources;src/resources" ^
    --noconfirm main.pyw
```

输出到 `dist/Pomodoro.exe`。打包后数据自动存储到 `%APPDATA%\Pomodoro Timer\`，即使升级版本也不会丢失。

### 项目结构

```
Pomodoro/
├── main.py                  # 入口（带控制台）
├── main.pyw                 # 入口（无控制台窗口）
├── requirements.txt         # 依赖：PySide6>=6.6
├── .gitignore
│
├── data/                    # 源码运行时的数据（自动生成）
│                              exe 模式下使用 %APPDATA%/Pomodoro Timer/
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
    │   └── worker.py        # 倒计时核心逻辑（QTimer 信号驱动）
    │
    ├── ui/
    │   ├── main_window.py   # 主窗口 UI、系统托盘、通知、提示音
    │   ├── settings_dialog.py # 设置对话框
    │   └── styles.py        # QSS 样式表
    │
    └── storage/
        ├── __init__.py      # 数据目录路由（源码/exe 自动切换）
        ├── settings.py      # 设置持久化（JSON）
        └── stats.py         # 统计持久化（JSON）
```

### 架构说明

- **单例模式** — `SettingsManager` 和 `StatsManager` 均为单例，避免重复加载
- **信号/槽** — `TimerWorker` 通过 Qt 信号 (`tick` / `phase_changed` / `state_changed` / `finished`) 与 UI 层解耦
- **QSS 主题** — 纯 QSS 样式，无额外 CSS 框架依赖
- **单实例** — 基于 `QLocalServer`/`QLocalSocket` 实现 IPC，确保只运行一个实例
- **数据目录自适应** — 源码运行存 `data/`，PyInstaller 打包后自动切换到 `%APPDATA%/Pomodoro Timer/`，支持无缝迁移

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
