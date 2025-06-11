import os
import datetime
import math

# 获取当前脚本所在目录的上一级目录
script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)

# 定义输入和输出文件夹路径
raw_folder_path = os.path.join(parent_dir, 'raw_file')
local_folder_path = os.path.join(parent_dir, 'local_file')

# 如果 raw_file 文件夹不存在，退出程序
if not os.path.exists(raw_folder_path):
    print(f"原始文件目录不存在：{raw_folder_path}")
    exit()

# 如果 local_file 文件夹不存在，创建它
if not os.path.exists(local_folder_path):
    os.makedirs(local_folder_path)
    print(f"已创建输出目录：{local_folder_path}")

# 获取所有 .SRT 文件列表
srt_files = [f for f in os.listdir(raw_folder_path) if f.endswith('.SRT')]

# 处理每个 SRT 文件
for srt_filename in srt_files:
    srt_file_path = os.path.join(raw_folder_path, srt_filename)
    txt_filename = srt_filename.replace('.SRT', '.txt')
    txt_file_path = os.path.join(local_folder_path, txt_filename)

    # 如果同名的 .txt 文件已存在，跳过该 SRT 文件
    if os.path.exists(txt_file_path):
        print(f"跳过已存在的文件：{txt_file_path}")
        continue

    # 初始化数据列表
    timestamps, latitudes, longitudes, abs_alts = [], [], [], []

    # 读取 SRT 文件内容
    with open(srt_file_path, 'r') as file:
        for line in file:
            if '2025-' in line:  # 检查时间戳行
                dt = datetime.datetime.strptime(line.strip(), "%Y-%m-%d %H:%M:%S.%f")
                timestamps.append(dt)

            if '[latitude:' in line:  # 检查坐标和高度数据行
                lat_start = line.find('[latitude:') + len('[latitude:')
                lat_end = line.find('] [longitude:')
                latitude = float(line[lat_start:lat_end])
                latitudes.append(latitude)

                lon_start = line.find('[longitude:') + len('[longitude:')
                lon_end = line.find('] [rel_alt:')
                longitude = float(line[lon_start:lon_end])
                longitudes.append(longitude)

                alt_start = line.find('abs_alt:') + len('abs_alt:')
                alt_end = line.find('] </font>')
                altitude = float(line[alt_start:alt_end])
                abs_alts.append(altitude)

    # 如果数据为空，跳过该文件
    if not timestamps:
        print(f"文件无有效数据：{srt_file_path}")
        continue

    # 计算相对于初始点的 xyz 位置
    x_coords = [(lon - longitudes[0]) * 111320 * math.cos(math.radians(latitudes[0])) for lon in longitudes]
    y_coords = [(lat - latitudes[0]) * 111320 for lat in latitudes]
    z_coords = [alt - abs_alts[0] for alt in abs_alts]

    # 保存结果到 .txt 文件
    with open(txt_file_path, 'w') as txt_file:
        for i in range(len(timestamps)):
            txt_file.write(f"{timestamps[i]} {x_coords[i]} {y_coords[i]} {z_coords[i]}\n")

    print(f"已处理文件：{srt_file_path}，数据保存到：{txt_file_path}")
