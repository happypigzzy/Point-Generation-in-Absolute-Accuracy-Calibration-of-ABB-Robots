import random
import re
import numpy as np
import math
import os

# 原始点数据字符串
data_string = """    CONST robtarget Align_1:=[[2232.99,-1063.35,1475.78],[0.61087,-0.631826,0.409222,-0.245299],[-1,-2,0,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_2:=[[2374.52,-562.96,492.43],[0.61087,-0.631826,0.409222,-0.245298],[-1,-1,-1,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_3:=[[2374.52,-129.73,1567.50],[0.61087,-0.631827,0.409221,-0.245297],[-1,-2,0,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_4:=[[2500.97,507.75,920.17],[0.61087,-0.631827,0.409222,-0.245296],[0,-1,-1,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_5:=[[2679.66,153.39,402.60],[0.610803,-0.631786,0.409332,-0.245385],[0,-1,-1,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_6:=[[2018.11,1742.86,910.90],[0.610972,-0.631827,0.409141,-0.245175],[0,0,-2,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_7:=[[2129.92,1735.48,254.23],[0.610972,-0.631827,0.409142,-0.245176],[0,0,-2,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_8:=[[1608.68,1036.36,28.99],[0.610971,-0.631827,0.409142,-0.245176],[0,-1,-1,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_9:=[[1204.15,631.83,1134.12],[0.610971,-0.631827,0.409142,-0.245177],[0,-1,-1,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];
    CONST robtarget Align_10:=[[1701.38,-295.07,1607.85],[0.610972,-0.631826,0.409143,-0.245177],[-1,-2,0,1],[9E+9,9E+9,9E+9,9E+9,9E+9,9E+9]];"""


# 解析数据字符串
def parse_data_string(data_string):
    # 使用正则表达式提取每个点的数据
    pattern = r"CONST robtarget Align_\d+:=\[\[(.*?)\],\[(.*?)\],\[(.*?)\],\[(.*?)\]\]"
    matches = re.findall(pattern, data_string)

    points = []
    configs = []
    extras = []

    for match in matches:
        # 提取坐标
        coords = [float(x) for x in match[0].split(",")]

        # 提取四元数
        quats = [float(x) for x in match[1].split(",")]

        # 提取配置
        config = [int(x) for x in match[2].split(",")]

        # 提取额外数据
        extra_parts = match[3].split(",")
        extra = []
        for part in extra_parts:
            if 'E' in part or 'e' in part:
                # 处理科学计数法
                extra.append(float(part))
            else:
                try:
                    extra.append(int(part))
                except:
                    extra.append(float(part))

        points.append(coords + quats)
        configs.append(config)
        extras.append(extra)

    return points, configs, extras


# 计算每个维度的最小值和最大值
def calculate_ranges(points):
    points_array = np.array(points)
    min_vals = np.min(points_array, axis=0)
    max_vals = np.max(points_array, axis=0)
    return min_vals, max_vals


# 计算两点之间的欧氏距离
def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0]) ** 2 +
                     (point1[1] - point2[1]) ** 2 +
                     (point1[2] - point2[2]) ** 2)


# 生成新点
def generate_new_points(min_vals, max_vals, configs, extras, deadzone=40, max_radius=1853,
                        num_points=200, min_distance=100):
    new_points = []
    existing_points = []  # 存储已生成点的坐标

    # XYZ的范围
    x_min, x_max = min_vals[0], max_vals[0]
    y_min, y_max = min_vals[1], max_vals[1]
    z_min, z_max = min_vals[2], max_vals[2]

    # 四元数的范围
    q1_min, q1_max = min_vals[3], max_vals[3]
    q2_min, q2_max = min_vals[4], max_vals[4]
    q3_min, q3_max = min_vals[5], max_vals[5]
    q4_min, q4_max = min_vals[6], max_vals[6]

    for i in range(1, num_points + 1):
        attempts = 0
        while attempts < 1000:  # 防止无限循环
            attempts += 1

            # 生成坐标
            x = random.uniform(x_min, x_max)
            y = random.uniform(y_min, y_max)
            z = random.uniform(z_min, z_max)

            # 检查死区限制：XYZ必须同时都在正负deadzone范围外
            if abs(x) <= deadzone or abs(y) <= deadzone or abs(z) <= deadzone:
                continue

            # 检查工作范围限制：XYZ的平方和的根不能超过max_radius
            distance = math.sqrt(x ** 2 + y ** 2 + z ** 2)
            if distance > max_radius:
                continue

            # 检查与所有已有点的距离
            too_close = False
            for existing_point in existing_points:
                if calculate_distance([x, y, z], existing_point) < min_distance:
                    too_close = True
                    break

            if too_close:
                continue

            # 生成四元数
            q1 = random.uniform(q1_min, q1_max)
            q2 = random.uniform(q2_min, q2_max)
            q3 = random.uniform(q3_min, q3_max)
            q4 = random.uniform(q4_min, q4_max)

            # 随机选择配置和额外数据
            random_idx = random.randint(0, len(configs) - 1)
            config = configs[random_idx]
            extra = extras[random_idx]

            # 格式化额外数据中的科学计数法
            formatted_extra = []
            for item in extra:
                if isinstance(item, float) and (abs(item) >= 1e4 or abs(item) <= 1e-4):
                    formatted_extra.append(f"{item:.4E}")
                else:
                    formatted_extra.append(str(item))

            # 格式化新点
            new_point = {
                'x': x,
                'y': y,
                'z': z,
                'q1': q1,
                'q2': q2,
                'q3': q3,
                'q4': q4,
                'config': config,
                'extra': formatted_extra
            }

            new_points.append(new_point)
            existing_points.append([x, y, z])  # 添加新点的坐标到已有点列表
            break

        if attempts >= 1000:
            print(f"警告: 无法为第 {i} 个点找到满足条件的坐标")

    return new_points


# 获取轴配置标签
def get_axis_config_label(config):
    # 配置数据格式: [cfg1, cfg2, cfg3, cfg4]
    # 我们关心的是第4、5、6轴，对应索引1、2、3
    axis4 = "正" if config[1] >= 0 else "负"
    axis5 = "正" if config[2] >= 0 else "负"
    axis6 = "正" if config[3] >= 0 else "负"

    return f"4{axis4}5{axis5}6{axis6}"


# 格式化输出
def format_output(points):
    output_lines = []
    for i, point in enumerate(points, 1):
        # 格式化坐标和四元数
        coords = f"{point['x']:.5g},{point['y']:.5g},{point['z']:.5g}"
        quats = f"{point['q1']:.6f},{point['q2']:.6f},{point['q3']:.6f},{point['q4']:.6f}"

        # 格式化配置和额外数据
        config_str = ",".join(str(x) for x in point['config'])
        extra_str = ",".join(str(x) for x in point['extra'])

        # 组合成完整的目标点定义
        line = f"CONST robtarget Calib_{i}:=[[{coords}],[{quats}],[{config_str}],[{extra_str}]];"
        output_lines.append(line)

    return output_lines


# 主程序
if __name__ == "__main__":
    # 获取用户输入的死区值和工作半径
    try:
        deadzone = float(input("请输入死区值（例如106，表示XYZ坐标必须同时都在±106范围外）: "))
        max_radius = float(input("请输入机器人工作半径（例如1853，表示XYZ的平方和的根不能超过此值）: "))
        min_distance = float(input("请输入最小距离（例如100，表示两点之间的最小距离）: "))
    except ValueError:
        print("输入无效，使用默认值（IRB2600-20/1.65）：死区值=469，工作半径=1653，最小距离=100")
        deadzone = 469
        max_radius = 1653
        min_distance = 100

    # 解析原始数据
    points, configs, extras = parse_data_string(data_string)

    # 计算范围
    min_vals, max_vals = calculate_ranges(points)

    # 生成新点
    new_points = generate_new_points(min_vals, max_vals, configs, extras, deadzone, max_radius,
                                     min_distance=min_distance)

    # 按轴配置分类
    config_groups = {}
    for point in new_points:
        label = get_axis_config_label(point['config'])
        if label not in config_groups:
            config_groups[label] = []
        config_groups[label].append(point)

    # 创建输出目录
    output_dir = "output_points"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # 为每个配置组创建文件
    for label, points_in_group in config_groups.items():
        filename = os.path.join(output_dir, f"points_{label}.txt")
        with open(filename, 'w') as f:
            formatted_lines = format_output(points_in_group)
            for line in formatted_lines:
                f.write(line + '\n')
        print(f"已创建文件: {filename}，包含 {len(points_in_group)} 个点")

    # 创建汇总文件
    summary_filename = os.path.join(output_dir, "summary.txt")
    with open(summary_filename, 'w') as f:
        f.write("轴配置分类汇总:\n")
        for label, points_in_group in config_groups.items():
            f.write(f"{label}: {len(points_in_group)} 个点\n")

    print(f"汇总文件已创建: {summary_filename}")

    # 在控制台显示所有点
    print("\n所有生成的点:")
    formatted_lines = format_output(new_points)
    for line in formatted_lines:
        print(line)
    with open("sum_output.txt", "w") as f:
        for line in formatted_lines:
            f.write(line + "\n")