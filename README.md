# 音频切割工具

一个简单易用的音频文件切割工具，支持多种音频格式（MP3、WAV、OGG、FLAC、AAC、M4A、WMA等），可以按文件大小、时长或数量进行切割。

## 功能特点

- **三种使用方式**
  - **桌面应用**: 提供原生窗口体验，无需浏览器 (推荐)
  - **Web 界面**: 在浏览器中进行图形化操作
  - **命令行**: 适合批量处理和脚本调用

- **多种切割模式**
  - 按文件大小切割（如每个分片 10MB）
  - 按时长切割（如每个分片 5 分钟）
  - 平均切割为指定数量的部分

- **智能依赖管理**
  - 内置 `ffmpeg`，大多数情况下无需手动安装

- **支持多种音频格式**
  - 输入: MP3, WAV, OGG, FLAC, AAC, M4A, WMA
  - 输出: 可保持原格式或转换为其他格式

- **简单易用**
  - 拖拽上传文件
  - 实时处理进度显示
  - 自动创建输出目录并打包下载

## 安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 关于 FFmpeg

本项目使用 `static-ffmpeg` 库，在首次运行时会自动下载并配置 `ffmpeg`。通常情况下，你 **无需手动安装**。

如果自动下载失败或需要使用特定版本的 `ffmpeg`，可以按以下传统方式手动安装：

**Windows:**
- 下载: https://www.gyan.dev/ffmpeg/builds/
- 解压并将 `bin` 目录添加到系统 `PATH` 环境变量

**macOS:**
```bash
brew install ffmpeg
```

**Linux:**
```bash
sudo apt install ffmpeg  # Ubuntu/Debian
sudo yum install ffmpeg  # CentOS/RHEL
```

## 使用方法

### 方式一：桌面应用 (推荐)

直接运行 `gui.py` 启动桌面版应用程序：

```bash
python gui.py
```

这会打开一个原生窗口，体验与桌面软件一致，无需依赖外部浏览器。

### 方式二：Web 界面

如果你希望在浏览器中使用，或者在另一台电脑上访问，可以启动 Web 服务：

```bash
python app.py
```

然后在浏览器中打开：**http://localhost:5000**

#### Web/桌面 界面功能

1. **上传文件**
   - 点击上传区域选择文件，或直接拖拽音频文件到上传区域。
   - 支持最大 500MB 的文件。
2. **选择切割模式**
   - **按文件大小**：指定每个分片的最大 MB 数。
   - **按时长**：指定每个分片的时长（分钟 + 秒）。
   - **按数量**：将文件平均分成 N 份。
3. **选择输出格式**（可选）
   - 默认保持原格式，也可转换为其他支持的格式。
4. **下载结果**
   - 切割完成后，可以单独下载每个文件，或 **一键下载包含所有分片的 ZIP 压缩包**。

### 方式三：命令行

适合自动化、批量处理等高级场景。

#### 基本语法

```bash
python main.py <输入文件> <切割模式> [选项]
```

#### 切割模式（三选一）

- **按文件大小切割**:
  ```bash
  # 将 input.mp3 切割为每个分片最大 10MB
  python main.py input.mp3 --size 10
  ```
- **按时长切割**:
  ```bash
  # 将 input.mp3 切割为每 300 秒（5分钟）一个分片
  python main.py input.mp3 --duration 300
  ```
- **按数量切割**:
  ```bash
  # 将 input.mp3 平均切割为 5 个部分
  python main.py input.mp3 --count 5
  ```

#### 高级选项

- **指定输出目录**:
  ```bash
  python main.py input.mp3 --size 10 --output ./my_output
  ```
- **转换格式**:
  ```bash
  python main.py input.wav --size 5 --format mp3
  ```

## 如何打包成可执行文件 (.exe)

你可以将此工具打包成一个独立的 Windows 可执行文件，方便在没有 Python 环境的电脑上使用。

1. **安装开发依赖**
   确保 `requirements.txt` 中的 `pyinstaller` 已安装。

2. **运行打包脚本**
   ```bash
   python build_exe.py
   ```

3. **获取结果**
   打包成功后，在 `dist` 目录下会生成 `AudioCutterTool.exe` 文件。

## 项目结构

```
音频切割工具/
├── gui.py             # 桌面应用入口 (新增)
├── build_exe.py       # 打包脚本 (新增)
├── app.py             # Web 服务端
├── main.py            # 命令行入口
├── audio_cutter.py     # 核心切割功能
├── requirements.txt   # Python 依赖
├── templates/         # HTML 模板
│   └── index.html
├── static/           # 静态资源
│   ├── style.css
│   └── app.js
├── uploads/          # 上传文件目录（自动创建）
├── output/           # 输出目录（自动创建）
└── README.md         # 使用说明
```

## Web API 接口

如果需要集成到其他系统，可以使用以下 API：

### 上传文件 (`POST /api/upload`)
- **Content-Type**: `multipart/form-data`
- **参数**: `file` (音频文件)
- **成功返回**:
  ```json
  {
    "success": true,
    "file_id": "unique-uuid",
    "filename": "原文件名.mp3",
    "filepath": "服务器上的临时路径"
  }
  ```

### 切割音频 (`POST /api/cut`)
- **Content-Type**: `application/json`
- **参数**:
  ```json
  {
    "file_id": "上传时返回的 file_id",
    "cut_mode": "size" | "duration" | "count",
    "cut_value": 10,
    "output_format": "mp3" 
  }
  ```
- **成功返回**:
  ```json
  {
    "success": true,
    "files": [
      { "name": "file_part1.mp3", "size": 10485760, "size_mb": 10.0 },
      { "name": "file_part2.mp3", "size": 8388608, "size_mb": 8.0 }
    ],
    "count": 2,
    "zip_filename": "cut_result_unique-uuid.zip"
  }
  ```

### 下载文件 (`GET /api/download/<filename>`)
- **说明**: 下载单个切割后的文件或 ZIP 压缩包。

### 清理文件 (`POST /api/clean`)
- **说明**: 清理服务器上所有已上传和已切割的文件，用于释放空间。
- **成功返回**: `{"success": true}`

## 技术实现细节

- **按大小切割的原理**: 为了提高效率，本工具采用 **估算策略**。它会先对一小段音频进行目标格式的转码，计算出大概的码率（字节/秒），然后依此推算出目标大小对应的切割时长。因此，最终分片大小可能与设定值有轻微偏差，这属于正常现象。
- **FFmpeg 自动管理**: 项目通过 `static-ffmpeg` 库实现了 `ffmpeg` 的按需下载和路径自动配置，简化了用户的初始设置步骤。

## 常见问题

- **Q: 提示 "ffmpeg not found"？**
  A: 本项目会自动下载 `ffmpeg`。如果失败，请检查网络连接或防火墙设置。您也可以尝试手动安装 `ffmpeg` 并将其添加到系统 PATH 中（详见安装章节）。

- **Q: 切割后文件大小不精确？**
  A: 这是设计如此。为了速度，我们通过估算码率来决定切割点，因此会有轻微误差。

- **Q: 支持哪些格式？**
  A: 支持 MP3, WAV, OGG, FLAC, AAC, M4A, WMA 等所有 `ffmpeg` 支持的主流格式。

- **Q: 桌面版/Web 界面无法启动？**
  A: 确保端口（5000 或 54321）未被其他程序占用，并检查防火墙设置。

## 依赖

- Python 3.7+
- Flask - Web 框架
- pydub - 音频处理库
- pywebview - GUI 框架
- static-ffmpeg - FFmpeg 自动下载器
- PyInstaller - （开发依赖）打包工具

## 许可证

MIT License
