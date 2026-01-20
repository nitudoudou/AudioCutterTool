// 音频切割工具 - 前端交互逻辑

class AudioCutterApp {
    constructor() {
        this.uploadedFileId = null;
        this.uploadedFileName = '';
        this.uploadedFileSize = 0;
        this.init();
    }

    init() {
        this.bindUploadEvents();
        this.bindModeEvents();
        this.bindCutButton();
        this.bindResetButton();
        this.bindDownloadAllButton();
    }

    // 上传相关事件
    bindUploadEvents() {
        const uploadArea = document.getElementById('uploadArea');
        const fileInput = document.getElementById('fileInput');
        const changeFileBtn = document.getElementById('changeFileBtn');

        // 点击上传区域
        uploadArea.addEventListener('click', () => fileInput.click());

        // 文件选择
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                this.handleFileSelect(e.target.files[0]);
            }
        });

        // 拖拽上传
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });

        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });

        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            if (e.dataTransfer.files.length > 0) {
                this.handleFileSelect(e.dataTransfer.files[0]);
            }
        });

        // 更换文件
        changeFileBtn.addEventListener('click', () => fileInput.click());
    }

    // 处理文件选择
    async handleFileSelect(file) {
        const validTypes = ['audio/mpeg', 'audio/wav', 'audio/ogg', 'audio/flac', 'audio/aac', 'audio/x-m4a', 'audio/wma'];
        const validExtensions = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma'];
        const fileExtension = '.' + file.name.split('.').pop().toLowerCase();

        if (!validExtensions.includes(fileExtension)) {
            alert('请选择有效的音频文件（MP3、WAV、OGG、FLAC、AAC、M4A、WMA）');
            return;
        }

        // 显示文件信息
        document.getElementById('uploadArea').style.display = 'none';
        document.getElementById('fileInfo').style.display = 'flex';
        document.getElementById('fileName').textContent = file.name;
        document.getElementById('fileSize').textContent = this.formatFileSize(file.size);

        // 上传文件到服务器
        await this.uploadFile(file);
    }

    // 上传文件
    async uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await fetch('/api/upload', {
                method: 'POST',
                body: formData
            });

            const result = await response.json();

            if (result.success) {
                this.uploadedFileId = result.file_id;
                this.uploadedFileName = result.filename;
                this.uploadedFileSize = file.size;
                document.getElementById('cutBtn').disabled = false;
            } else {
                alert('上传失败: ' + result.error);
                this.resetUpload();
            }
        } catch (error) {
            alert('上传失败: ' + error.message);
            this.resetUpload();
        }
    }

    // 模式切换事件
    bindModeEvents() {
        const modeBtns = document.querySelectorAll('.mode-btn');
        const sizeGroup = document.getElementById('sizeGroup');
        const durationGroup = document.getElementById('durationGroup');
        const countGroup = document.getElementById('countGroup');

        modeBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // 切换激活状态
                modeBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // 切换输入组显示
                const mode = btn.dataset.mode;
                sizeGroup.style.display = 'none';
                durationGroup.style.display = 'none';
                countGroup.style.display = 'none';

                switch (mode) {
                    case 'size':
                        sizeGroup.style.display = 'block';
                        break;
                    case 'duration':
                        durationGroup.style.display = 'block';
                        break;
                    case 'count':
                        countGroup.style.display = 'block';
                        break;
                }
            });
        });
    }

    // 切割按钮
    bindCutButton() {
        const cutBtn = document.getElementById('cutBtn');
        cutBtn.addEventListener('click', () => this.cutAudio());
    }

    // 执行切割
    async cutAudio() {
        const activeModeBtn = document.querySelector('.mode-btn.active');
        const cutMode = activeModeBtn ? activeModeBtn.dataset.mode : 'size';
        let cutValue;

        switch (cutMode) {
            case 'size':
                cutValue = parseFloat(document.getElementById('sizeInput').value);
                if (!cutValue || cutValue <= 0) {
                    alert('请输入有效的文件大小');
                    return;
                }
                break;
            case 'duration':
                const minutes = parseInt(document.getElementById('durationMinutes').value) || 0;
                const seconds = parseInt(document.getElementById('durationSeconds').value) || 0;
                cutValue = minutes * 60 + seconds;
                if (cutValue <= 0) {
                    alert('请输入有效的时长');
                    return;
                }
                break;
            case 'count':
                cutValue = parseInt(document.getElementById('countInput').value);
                if (!cutValue || cutValue < 2) {
                    alert('请输入有效的数量（至少2份）');
                    return;
                }
                break;
        }

        const outputFormat = document.getElementById('formatSelect').value;

        // 显示进度
        this.showProgress();

        try {
            const response = await fetch('/api/cut', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    file_id: this.uploadedFileId,
                    cut_mode: cutMode,
                    cut_value: cutValue,
                    output_format: outputFormat || null
                })
            });

            const result = await response.json();

            if (result.success) {
                this.hideProgress();
                this.showResults(result.files, result.zip_filename);
            } else {
                this.hideProgress();
                alert('切割失败: ' + result.error);
            }
        } catch (error) {
            this.hideProgress();
            alert('切割失败: ' + error.message);
        }
    }

    // 显示进度
    showProgress() {
        const progressSection = document.getElementById('progressSection');
        const progressFill = document.getElementById('progressFill');
        const progressText = document.getElementById('progressText');
        const cutBtn = document.getElementById('cutBtn');

        progressSection.style.display = 'block';
        progressFill.style.width = '0%';
        progressText.textContent = '正在上传...';

        // 模拟进度
        let progress = 0;
        const interval = setInterval(() => {
            progress += Math.random() * 15;
            if (progress > 90) progress = 90;
            progressFill.style.width = progress + '%';

            if (progress < 30) {
                progressText.textContent = '正在处理音频...';
            } else if (progress < 60) {
                progressText.textContent = '正在切割...';
            } else {
                progressText.textContent = '正在生成文件...';
            }
        }, 500);

        this.progressInterval = interval;
        cutBtn.disabled = true;
    }

    // 隐藏进度
    hideProgress() {
        const progressSection = document.getElementById('progressSection');
        const progressFill = document.getElementById('progressFill');
        const cutBtn = document.getElementById('cutBtn');

        clearInterval(this.progressInterval);
        progressFill.style.width = '100%';
        setTimeout(() => {
            progressSection.style.display = 'none';
            cutBtn.disabled = false;
        }, 500);
    }

    // 显示结果
    showResults(files, zipFilename) {
        const resultSection = document.getElementById('resultSection');
        const fileList = document.getElementById('fileList');
        const fileCount = document.getElementById('fileCount');

        this.zipFilename = zipFilename; // 保存 zip 文件名
        fileList.innerHTML = '';
        fileCount.textContent = files.length;

        files.forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <div class="file-item-info">
                    <p class="file-item-name">${file.name}</p>
                    <p class="file-item-size">${file.size_mb} MB</p>
                </div>
                <button class="file-item-download" onclick="app.downloadFile('${file.name}')">
                    下载
                </button>
            `;
            fileList.appendChild(fileItem);
        });

        const downloadAllBtn = document.getElementById('downloadAllBtn');
        if (zipFilename) {
            downloadAllBtn.textContent = '打包下载 (ZIP)';
            downloadAllBtn.style.display = 'inline-block';
        } else {
            downloadAllBtn.style.display = 'none';
        }

        resultSection.style.display = 'block';
        resultSection.scrollIntoView({ behavior: 'smooth' });
    }

    // 下载单个文件
    downloadFile(filename) {
        window.open(`/api/download/${encodeURIComponent(filename)}`, '_blank');
    }

    // 重置按钮
    bindResetButton() {
        document.getElementById('resetBtn').addEventListener('click', () => this.reset());
    }

    // 下载所有按钮
    bindDownloadAllButton() {
        document.getElementById('downloadAllBtn').addEventListener('click', () => {
            if (this.zipFilename) {
                this.downloadFile(this.zipFilename);
            } else {
                alert('打包文件未生成');
            }
        });
    }

    // 重置
    reset() {
        this.uploadedFileId = null;
        this.uploadedFileName = '';
        this.uploadedFileSize = 0;

        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('resultSection').style.display = 'none';
        document.getElementById('fileInput').value = '';
        document.getElementById('cutBtn').disabled = false;
    }

    resetUpload() {
        document.getElementById('uploadArea').style.display = 'block';
        document.getElementById('fileInfo').style.display = 'none';
        document.getElementById('fileInput').value = '';
    }

    // 格式化文件大小
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }
}

// 初始化应用
const app = new AudioCutterApp();
