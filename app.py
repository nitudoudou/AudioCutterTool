"""
音频切割工具 - Web 服务端
"""
import os
import sys
import uuid
import zipfile
from pathlib import Path
from flask import Flask, render_template, request, send_file, jsonify
from werkzeug.utils import secure_filename
from audio_cutter import AudioCutter

# 确定基础路径
if getattr(sys, 'frozen', False):
    # 如果是打包后的 EXE，使用可执行文件所在的目录
    BASE_DIR = Path(sys.executable).parent
    # 如果是 PyInstaller 打包，模板和静态文件在临时目录中
    TEMPLATE_DIR = Path(sys._MEIPASS) / 'templates'
    STATIC_DIR = Path(sys._MEIPASS) / 'static'
    app = Flask(__name__, template_folder=str(TEMPLATE_DIR), static_folder=str(STATIC_DIR))
else:
    # 开发模式
    BASE_DIR = Path(__file__).parent
    app = Flask(__name__)

app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 最大 500MB
app.config['UPLOAD_FOLDER'] = BASE_DIR / 'uploads'
app.config['OUTPUT_FOLDER'] = BASE_DIR / 'output'

# 确保目录存在
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

# 允许的音频格式
ALLOWED_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'wma'}


def allowed_file(filename):
    """检查文件格式是否允许"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件接口"""
    if 'file' not in request.files:
        return jsonify({'error': '没有上传文件'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': '没有选择文件'}), 400

    if not allowed_file(file.filename):
        return jsonify({'error': f'不支持的文件格式，支持的格式: {", ".join(ALLOWED_EXTENSIONS)}'}), 400

    # 生成唯一文件名
    file_id = str(uuid.uuid4())
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{file_id}.{file_ext}"
    filepath = app.config['UPLOAD_FOLDER'] / unique_filename

    file.save(filepath)

    return jsonify({
        'success': True,
        'file_id': file_id,
        'filename': filename,
        'filepath': str(filepath)
    })


@app.route('/api/cut', methods=['POST'])
def cut_audio():
    """切割音频接口"""
    data = request.get_json()

    file_id = data.get('file_id')
    cut_mode = data.get('cut_mode')  # 'size', 'duration', 'count'
    cut_value = data.get('cut_value')
    output_format = data.get('output_format')

    if not file_id or not cut_mode or not cut_value:
        return jsonify({'error': '缺少必要参数'}), 400

    # 查找上传的文件
    upload_files = list(app.config['UPLOAD_FOLDER'].glob(f'{file_id}.*'))
    if not upload_files:
        return jsonify({'error': '找不到上传的文件'}), 404

    input_file = str(upload_files[0])

    try:
        cutter = AudioCutter(output_dir=str(app.config['OUTPUT_FOLDER']))

        if cut_mode == 'size':
            output_files = cutter.cut_by_size(input_file, cut_value, output_format)
        elif cut_mode == 'duration':
            output_files = cutter.cut_by_duration(input_file, cut_value, output_format)
        elif cut_mode == 'count':
            output_files = cutter.cut_by_count(input_file, cut_value, output_format)
        else:
            return jsonify({'error': '无效的切割模式'}), 400

        # 获取输出文件信息
        file_info = []
        for f in output_files:
            path = Path(f)
            file_info.append({
                'name': path.name,
                'size': path.stat().st_size,
                'size_mb': round(path.stat().st_size / 1024 / 1024, 2)
            })

        # 创建 ZIP 压缩包
        zip_filename = None
        if output_files:
            original_stem = Path(input_file).stem
            # 如果文件名包含UUID，尝试去除它以保持友好的文件名
            # 这里的 input_file 是 uploads/uuid.ext，所以 stem 只是 uuid
            # 我们应该使用用户上传时的原始文件名，但这里只有 uuid
            # 为了简单起见，我们使用 output_files[0] 的前缀，通常是 uuid_partX
            
            # 使用上传的文件ID作为基础，或者生成一个新的ID
            zip_name = f"cut_result_{file_id}.zip"
            zip_path = app.config['OUTPUT_FOLDER'] / zip_name
            
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for f in output_files:
                    path = Path(f)
                    zipf.write(path, arcname=path.name)
            
            zip_filename = zip_name

        return jsonify({
            'success': True,
            'files': file_info,
            'count': len(output_files),
            'zip_filename': zip_filename
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/download/<filename>')
def download_file(filename):
    """下载文件接口"""
    filepath = app.config['OUTPUT_FOLDER'] / secure_filename(filename)
    if filepath.exists():
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': '文件不存在'}), 404


@app.route('/api/files', methods=['GET'])
def list_files():
    """列出可下载的文件"""
    files = []
    for f in app.config['OUTPUT_FOLDER'].iterdir():
        if f.is_file():
            files.append({
                'name': f.name,
                'size': f.stat().st_size,
                'size_mb': round(f.stat().st_size / 1024 / 1024, 2)
            })

    return jsonify({'files': files})


@app.route('/api/clean', methods=['POST'])
def clean_files():
    """清理所有文件"""
    try:
        # 清理上传目录
        for f in app.config['UPLOAD_FOLDER'].iterdir():
            if f.is_file():
                f.unlink()

        # 清理输出目录
        for f in app.config['OUTPUT_FOLDER'].iterdir():
            if f.is_file():
                f.unlink()

        return jsonify({'success': True})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 60)
    print("音频切割工具 Web 服务")
    print("=" * 60)
    print("服务地址: http://localhost:5000")
    print("按 Ctrl+C 停止服务")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
