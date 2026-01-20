
import os
import shutil
import PyInstaller.__main__
from pydub.utils import which
import static_ffmpeg

# 确保 static-ffmpeg 已配置
static_ffmpeg.add_paths()

# 获取 ffmpeg 和 ffprobe 路径
ffmpeg_path = which("ffmpeg")
ffprobe_path = which("ffprobe")

if not ffmpeg_path or not ffprobe_path:
    print("错误: 找不到 ffmpeg 或 ffprobe，请先运行项目确保环境正常")
    exit(1)

print(f"找到 ffmpeg: {ffmpeg_path}")
print(f"找到 ffprobe: {ffprobe_path}")

# 定义资源文件
# 格式: (源路径, 目标路径)
# 注意: Windows下分隔符为 ;
add_data = [
    ('templates', 'templates'),
    ('static', 'static'),
]

# 定义二进制文件
add_binary = [
    (ffmpeg_path, '.'),
    (ffprobe_path, '.'),
]

# 构建 PyInstaller 参数
args = [
    'gui.py',                      # 主程序改为 GUI 入口
    '--name=AudioCutterTool',      # exe 名称
    '--onefile',                   # 单文件模式
    '--noconfirm',                 # 不确认覆盖
    '--clean',                     # 清理缓存
    '--windowed',                  # 无控制台窗口
]

# 添加数据文件
for src, dst in add_data:
    args.append(f'--add-data={src}{os.pathsep}{dst}')

# 添加二进制文件
for src, dst in add_binary:
    args.append(f'--add-binary={src}{os.pathsep}.')

print("开始打包...")
PyInstaller.__main__.run(args)
print("打包完成！请查看 dist 目录。")
