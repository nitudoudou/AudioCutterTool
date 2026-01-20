# 音频切割工具

一个简单易用的音频文件切割工具，支持多种音频格式（MP3、WAV、OGG、FLAC、AAC、M4A、WMA等），可以按文件大小、时长或数量进行切割。

## 功能特点

- **两种使用方式**
  - Web 界面：图形化操作，简单直观
  - 命令行：适合批量处理和脚本调用

- **多种切割模式**
  - 按文件大小切割（如每个分片 10MB）
  - 按时长切割（如每个分片 5 分钟）
  - 平均切割为指定数量的部分

- **支持多种音频格式**
  - 输入: MP3, WAV, OGG, FLAC, AAC, M4A, WMA
  - 输出: 可保持原格式或转换为其他格式

- **简单易用**
  - 拖拽上传文件
  - 实时处理进度显示
  - 自动创建输出目录

## 安装

### 1. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 2. 安装 FFmpeg

**Windows:**
- 下载: https://www.gyan.dev/ffmpeg/builds/
- 解压并将 `bin` 目录添加到系统 PATH

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

### 方式一：Web 界面（推荐）

启动 Web 服务：

```bash
python app.py
```

然后在浏览器中打开：**http://localhost:5000**

#### Web 界面功能

1. **上传文件**
   - 点击上传区域选择文件
   - 或直接拖拽音频文件到上传区域
   - 支持最大 500MB 的文件

2. **选择切割模式**
   - 按文件大小：指定每个分片的最大 MB 数
   - 按时长：指定每个分片的时长（分钟 + 秒）
   - 按数量：将文件平均分成 N 份

3. **选择输出格式**（可选）
   - 默认保持原格式
   - 可转换为其他支持的格式

4. **下载结果**
   - 单独下载每个文件
   - 批量下载所有文件

### 方式二：命令行

#### 基本语法

```bash
python main.py <输入文件> <切割模式> [选项]
```

#### 切割模式（三选一）

##### 1. 按文件大小切割

将音频文件切割为指定大小的分片：

```bash
python main.py input.mp3 --size 10
```

每个分片最大 10MB。

##### 2. 按时长切割

将音频文件按指定时长切割：

```bash
python main.py input.mp3 --duration 300
```

每个分片 300 秒（5 分钟）。

##### 3. 按数量切割

将音频文件平均切割为指定数量：

```bash
python main.py input.mp3 --count 5
```

切割为 5 个部分。

#### 高级选项

##### 指定输出目录

```bash
python main.py input.mp3 --size 10 --output ./my_output
```

##### 转换格式

切割时转换音频格式：

```bash
python main.py input.wav --size 5 --format mp3
```

#### 完整示例

```bash
# 将 podcast.mp3 切割为每片 20MB
python main.py podcast.mp3 --size 20

# 将 recording.wav 切割为每段 10 分钟，输出为 MP3
python main.py recording.wav --duration 600 --format mp3

# 将长音频平均分为 3 部分，保存到指定目录
python main.py long_audio.mp3 --count 3 --output D:\AudioClips
```

## 项目结构

```
音频切割工具/
├── audio_cutter.py    # 核心切割功能
├── app.py            # Web 服务端
├── main.py           # 命令行入口
├── requirements.txt   # Python 依赖
├── templates/        # HTML 模板
│   └── index.html
├── static/          # 静态资源
│   ├── style.css
│   └── app.js
├── uploads/         # 上传文件目录（自动创建）
├── output/          # 输出目录（自动创建）
└── README.md        # 使用说明
```

## Web API 接口

如果需要集成到其他系统，可以使用以下 API：

### 上传文件

```
POST /api/upload
Content-Type: multipart/form-data

参数: file (音频文件)

返回:
{
  "success": true,
  "file_id": "uuid",
  "filename": "原文件名",
  "filepath": "服务器路径"
}
```

### 切割音频

```
POST /api/cut
Content-Type: application/json

参数:
{
  "file_id": "上传时返回的文件ID",
  "cut_mode": "size | duration | count",
  "cut_value": 数值,
  "output_format": "输出格式（可选）"
}

返回:
{
  "success": true,
  "files": [...],
  "count": 文件数量
}
```

### 下载文件

```
GET /api/download/<filename>
```

## 输出文件命名

切割后的文件按以下规则命名：

```
<原文件名>_part<序号>.<格式>
```

例如：`music.mp3` → `music_part1.mp3`, `music_part2.mp3`, ...

## 常见问题

### Q: 提示 "ffmpeg not found"？

A: 需要安装 FFmpeg 并添加到系统 PATH。参见上方安装说明。

### Q: 切割后文件大小不精确？

A: 这是正常现象。音频编码复杂，文件大小会略有偏差，但会尽量接近指定大小。

### Q: 支持哪些格式？

A: 支持 MP3、WAV、OGG、FLAC、AAC、M4A、WMA 等常见格式。

### Q: Web 界面无法访问？

A: 确保 5000 端口未被占用，检查防火墙设置。

## 依赖

- Python 3.6+
- Flask - Web 框架
- pydub - 音频处理库
- ffmpeg - 底层音视频处理工具

## 许可证

MIT License
