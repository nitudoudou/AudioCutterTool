"""
音频切割工具 - 命令行接口
支持多种音频格式的切割
"""
import argparse
import sys
from audio_cutter import AudioCutter


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='音频切割工具 - 支持按大小、时长或数量切割音频文件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 按文件大小切割 (每个分片 10MB)
  python main.py input.mp3 --size 10

  # 按时长切割 (每个分片 5 分钟)
  python main.py input.mp3 --duration 300

  # 切割成 5 个部分
  python main.py input.mp3 --count 5

  # 指定输出目录
  python main.py input.mp3 --size 10 --output ./my_output

  # 转换格式并切割
  python main.py input.wav --size 5 --format mp3
        """
    )

    parser.add_argument('input', help='输入音频文件路径')

    # 切割方式（三选一）
    cut_mode = parser.add_mutually_exclusive_group(required=True)
    cut_mode.add_argument('--size', '-s', type=float,
                          help='按文件大小切割 (单位: MB)')
    cut_mode.add_argument('--duration', '-d', type=int,
                          help='按时长切割 (单位: 秒)')
    cut_mode.add_argument('--count', '-c', type=int,
                          help='切割成指定数量的部分')

    # 可选参数
    parser.add_argument('--output', '-o', default=None,
                        help='输出目录 (默认: ./output)')
    parser.add_argument('--format', '-f', default=None,
                        help='输出格式 (默认: 与输入相同)')

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 检查输入文件
    try:
        cutter = AudioCutter(output_dir=args.output)
        cutter.validate_audio_file(args.input)
    except (FileNotFoundError, ValueError) as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"正在处理: {args.input}")
    print(f"输出目录: {cutter.output_dir}")
    print("-" * 50)

    # 根据不同模式切割
    try:
        if args.size:
            print(f"切割模式: 按文件大小 ({args.size} MB/分片)")
            output_files = cutter.cut_by_size(
                args.input,
                chunk_size_mb=args.size,
                output_format=args.format
            )
        elif args.duration:
            minutes = args.duration // 60
            seconds = args.duration % 60
            print(f"切割模式: 按时长 ({minutes}分{seconds}秒/分片)")
            output_files = cutter.cut_by_duration(
                args.input,
                duration_seconds=args.duration,
                output_format=args.format
            )
        else:  # args.count
            print(f"切割模式: 平均切割为 {args.count} 个部分")
            output_files = cutter.cut_by_count(
                args.input,
                num_parts=args.count,
                output_format=args.format
            )

        print("-" * 50)
        print(f"完成! 共生成 {len(output_files)} 个文件:")
        for f in output_files:
            print(f"  - {f}")

    except Exception as e:
        print(f"切割失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
