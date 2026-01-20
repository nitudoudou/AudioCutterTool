"""
音频切割工具核心模块
支持多种音频格式的切割功能
"""
import os
import sys
from pathlib import Path
from pydub import AudioSegment
from pydub.utils import mediainfo
import static_ffmpeg

# 自动配置 ffmpeg 和 ffprobe 路径到环境变量
# 如果是打包环境，将临时目录加入 PATH
if getattr(sys, 'frozen', False):
    os.environ["PATH"] += os.pathsep + sys._MEIPASS
else:
    static_ffmpeg.add_paths()


class AudioCutter:
    """音频切割器类"""

    # 支持的音频格式
    SUPPORTED_FORMATS = ['.mp3', '.wav', '.ogg', '.flac', '.aac', '.m4a', '.wma']

    def __init__(self, output_dir: str = None):
        """
        初始化音频切割器

        Args:
            output_dir: 输出目录，默认为当前目录下的 output 文件夹
        """
        if output_dir is None:
            output_dir = os.path.join(os.getcwd(), 'output')

        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def validate_audio_file(self, file_path: str) -> bool:
        """
        验证音频文件是否有效

        Args:
            file_path: 音频文件路径

        Returns:
            bool: 是否为支持的音频格式
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"文件不存在: {file_path}")

        if path.suffix.lower() not in self.SUPPORTED_FORMATS:
            raise ValueError(
                f"不支持的音频格式: {path.suffix}. "
                f"支持的格式: {', '.join(self.SUPPORTED_FORMATS)}"
            )

        return True

    def _get_bitrate(self, file_path: str) -> str:
        """尝试获取音频文件的比特率"""
        try:
            info = mediainfo(file_path)
            # mediainfo 返回的 bit_rate 是字符串，如 '320000'
            if 'bit_rate' in info:
                # 转换为 kbps 字符串，例如 "320k"
                return f"{int(info['bit_rate']) // 1000}k"
        except Exception as e:
            print(f"无法获取比特率: {e}")
        return None

    def cut_by_size(self, input_file: str, chunk_size_mb: float,
                    output_format: str = None) -> list:
        """
        根据文件大小切割音频
        优化策略：通过采样计算目标格式的比特率，转换为按时长切割，大幅提升速度

        Args:
            input_file: 输入音频文件路径
            chunk_size_mb: 每个分片的大小（MB）
            output_format: 输出格式，默认与输入相同

        Returns:
            list: 生成的文件路径列表
        """
        self.validate_audio_file(input_file)

        input_path = Path(input_file)
        if output_format is None:
            output_format = input_path.suffix[1:]  # 去掉点号

        chunk_size_bytes = int(chunk_size_mb * 1024 * 1024)

        # 尝试获取原始比特率
        original_bitrate = self._get_bitrate(input_file)
        print(f"原始比特率: {original_bitrate}")

        # 加载音频文件
        audio = AudioSegment.from_file(input_file)
        total_duration_ms = len(audio)

        # 采样逻辑优化：取中间 10 秒（避免片头静音）
        sample_duration_ms = min(10000, total_duration_ms)
        start_ms = (total_duration_ms - sample_duration_ms) // 2
        sample_segment = audio[start_ms : start_ms + sample_duration_ms]

        temp_sample_file = self.output_dir / f"sample_rate_test_{os.urandom(4).hex()}.{output_format}"
        
        # 导出采样文件时使用原始比特率（如果可用）
        export_params = {}
        if original_bitrate and output_format in ['mp3', 'aac', 'm4a', 'wma', 'ogg']:
             export_params['bitrate'] = original_bitrate

        sample_segment.export(temp_sample_file, format=output_format, **export_params)
        
        sample_size = temp_sample_file.stat().st_size
        
        # 清理临时文件
        if temp_sample_file.exists():
            temp_sample_file.unlink()

        if sample_size == 0:
             raise ValueError("无法估算输出文件大小，采样生成文件为空")

        # 计算每毫秒的字节数
        bytes_per_ms = sample_size / sample_duration_ms

        # 计算目标时长
        # 留 5% 的缓冲空间，防止文件略微超出限制（因为VBR波动）
        target_duration_ms = int((chunk_size_bytes / bytes_per_ms) * 0.95)

        # 确保最小切割时长不小于 1 秒
        target_duration_ms = max(1000, target_duration_ms)
        
        print(f"估算比特率: {bytes_per_ms * 1000 / 1024:.2f} KB/s")
        print(f"目标分片时长: {target_duration_ms / 1000:.2f} 秒")

        # 转换为秒
        target_duration_seconds = target_duration_ms // 1000
        
        # 复用按时长切割的逻辑，并传递比特率参数
        return self.cut_by_duration(input_file, target_duration_seconds, output_format, bitrate=original_bitrate)

    def cut_by_duration(self, input_file: str, duration_seconds: int,
                        output_format: str = None, bitrate: str = None) -> list:
        """
        根据时长切割音频

        Args:
            input_file: 输入音频文件路径
            duration_seconds: 每个分片的时长（秒）
            output_format: 输出格式，默认与输入相同
            bitrate: 目标比特率（如 "192k"），如果为 None 则使用默认值

        Returns:
            list: 生成的文件路径列表
        """
        self.validate_audio_file(input_file)

        input_path = Path(input_file)
        if output_format is None:
            output_format = input_path.suffix[1:]

        # 加载音频文件
        audio = AudioSegment.from_file(input_file)

        # 获取原始文件名
        base_name = input_path.stem

        chunk_duration_ms = duration_seconds * 1000
        output_files = []

        # 计算总分片数
        total_chunks = len(audio) // chunk_duration_ms + (1 if len(audio) % chunk_duration_ms else 0)

        export_params = {}
        if bitrate and output_format in ['mp3', 'aac', 'm4a', 'wma', 'ogg']:
            export_params['bitrate'] = bitrate

        for i in range(total_chunks):
            start_ms = i * chunk_duration_ms
            end_ms = start_ms + chunk_duration_ms

            # 切割音频
            chunk = audio[start_ms:end_ms]

            # 保存文件
            output_file = self.output_dir / f"{base_name}_part{i + 1}.{output_format}"
            chunk.export(output_file, format=output_format, **export_params)
            output_files.append(str(output_file))

            duration_minutes = duration_seconds // 60
            duration_secs = duration_seconds % 60
            print(f"已生成: {output_file.name} (时长: {duration_minutes}分{duration_secs}秒)")

        return output_files

    def cut_by_count(self, input_file: str, num_parts: int,
                     output_format: str = None, bitrate: str = None) -> list:
        """
        将音频平均切割为指定数量的部分

        Args:
            input_file: 输入音频文件路径
            num_parts: 切割成的数量
            output_format: 输出格式，默认与输入相同
            bitrate: 目标比特率（如 "192k"）

        Returns:
            list: 生成的文件路径列表
        """
        self.validate_audio_file(input_file)

        input_path = Path(input_file)
        if output_format is None:
            output_format = input_path.suffix[1:]

        # 加载音频文件
        audio = AudioSegment.from_file(input_file)

        # 获取原始文件名
        base_name = input_path.stem

        total_duration_ms = len(audio)
        chunk_duration_ms = total_duration_ms // num_parts

        output_files = []

        export_params = {}
        if bitrate and output_format in ['mp3', 'aac', 'm4a', 'wma', 'ogg']:
            export_params['bitrate'] = bitrate

        for i in range(num_parts):
            start_ms = i * chunk_duration_ms
            # 最后一段包含剩余所有音频
            if i == num_parts - 1:
                end_ms = total_duration_ms
            else:
                end_ms = start_ms + chunk_duration_ms

            # 切割音频
            chunk = audio[start_ms:end_ms]

            # 保存文件
            output_file = self.output_dir / f"{base_name}_part{i + 1}.{output_format}"
            chunk.export(output_file, format=output_format, **export_params)
            output_files.append(str(output_file))

            chunk_duration_seconds = (end_ms - start_ms) // 1000
            print(f"已生成: {output_file.name} (时长: {chunk_duration_seconds}秒)")

        return output_files


def main():
    """测试代码"""
    cutter = AudioCutter()

    # 示例用法
    print("音频切割工具已就绪")
    print(f"输出目录: {cutter.output_dir}")
    print(f"支持的格式: {', '.join(AudioCutter.SUPPORTED_FORMATS)}")


if __name__ == "__main__":
    main()
