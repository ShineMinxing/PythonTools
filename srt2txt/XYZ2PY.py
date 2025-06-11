import os
import math
from datetime import datetime

# 预设观察点位置 (观察者坐标)
OBSERVER_POSITION = (0, 0, -1)  # (X, Y, Z)

# 全局变量用于跟踪前一个方向角
previous_azimuth = None
total_rotations = 0  # 跟踪完整的旋转圈数

def calculate_angles(target_pos, observer_pos):
    """
    计算从观察者位置到目标位置的方向角和俯仰角
    :param target_pos: 目标位置 (X, Y, Z)
    :param observer_pos: 观察者位置 (X, Y, Z)
    :return: 方向角(度), 俯仰角(度)
    """
    global previous_azimuth, total_rotations
    
    # 计算相对位置
    dx = target_pos[0] - observer_pos[0]
    dy = target_pos[1] - observer_pos[1]
    dz = target_pos[2] - observer_pos[2]
    
    # 计算原始方向角 (azimuth) - 在XY平面上的角度
    azimuth = math.degrees(math.atan2(dy, dx))
    azimuth = (90 - azimuth)  # 转换为正北为0度的坐标系
    
    # 如果是第一次计算，不做连续化处理
    if previous_azimuth is None:
        previous_azimuth = azimuth
    else:
        # 计算角度差
        delta = azimuth - previous_azimuth
        
        # 处理跨越360度的情况
        if delta > 180:
            total_rotations -= 1
        elif delta < -180:
            total_rotations += 1
        
        # 更新方向角为连续值
        azimuth += total_rotations * 360
        previous_azimuth = azimuth - total_rotations * 360  # 保存原始值
    
    # 计算俯仰角 (elevation) - 相对于水平面的角度 (-90到90度)
    distance_xy = math.sqrt(dx**2 + dy**2)
    elevation = math.degrees(math.atan2(dz, distance_xy))
    
    return azimuth, elevation

def process_file(input_path, output_path):
    """
    处理单个文件，将XYZ坐标转换为角度并保存
    :param input_path: 输入文件路径
    :param output_path: 输出文件路径
    """
    global previous_azimuth, total_rotations
    previous_azimuth = None  # 重置前一个方向角
    total_rotations = 0      # 重置旋转圈数
    
    with open(input_path, 'r') as infile, open(output_path, 'w') as outfile:
        for line in infile:
            # 跳过空行
            if not line.strip():
                continue
                
            try:
                # 解析每行数据
                parts = line.split()
                timestamp = ' '.join(parts[:2])  # 合并日期和时间
                x, y, z = map(float, parts[2:5])
                
                # 计算角度
                azimuth, elevation = calculate_angles((x, y, z), OBSERVER_POSITION)
                
                # 写入结果
                outfile.write(f"{timestamp} {azimuth:.6f} {elevation:.6f}\n")
            except (ValueError, IndexError) as e:
                print(f"处理文件 {input_path} 时出错，行内容: {line.strip()} - 错误: {e}")
                continue

def main():
    # 获取脚本所在目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 获取上一级目录
    parent_dir = os.path.dirname(script_dir)
    # 构建local_file目录路径
    local_file_dir = os.path.join(parent_dir, 'local_file')
    
    # 确保输入目录存在
    if not os.path.exists(local_file_dir):
        print(f"错误: 目录 {local_file_dir} 不存在")
        return
    
    # 遍历目录中的所有文件
    processed_count = 0
    skipped_count = 0
    
    for filename in os.listdir(local_file_dir):
        # 只处理.txt文件且不以RP结尾的文件
        if filename.endswith('_xyz.txt'):
            input_path = os.path.join(local_file_dir, filename)
            
            # 创建输出文件名 (在原文件名后添加RP)
            base_name = os.path.splitext(filename)[0]
            output_filename = base_name.replace('_xyz', '_py') + '.txt'
            output_path = os.path.join(local_file_dir, output_filename)
            
            # 检查RP文件是否已存在
            if os.path.exists(output_path):
                print(f"跳过文件: {filename} (已存在对应的RP文件: {output_filename})")
                skipped_count += 1
                continue
            
            print(f"处理文件: {filename} -> {output_filename}")
            process_file(input_path, output_path)
            processed_count += 1
    
    print(f"处理完成! 已处理 {processed_count} 个文件，跳过 {skipped_count} 个已存在RP文件的文件。")

if __name__ == "__main__":
    main()
