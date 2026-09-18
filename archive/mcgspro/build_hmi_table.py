import os,re,csv
from collections import defaultdict

# Load PLC usage
plc_usage = {}
with open(r"d:\work\CTI\archive\mcgspro\plc_addresses.txt", "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line: continue
        parts = line.split("\t")
        if len(parts) >= 3:
            plc_usage[parts[0]] = {"rw": parts[1], "files": parts[2]}

# Load CSV
csv_by_chan = {}
csv_by_addr = {}
with open(r"d:\work\CTI\archive\mcgspro\csv_output\西门子_S7_Smart200_以太网_通道处理.csv", "r", encoding="gbk") as f:
    reader = csv.reader(f)
    for i, row in enumerate(reader):
        if i < 5 or len(row) < 9 or not row[0].isdigit(): continue
        csv_by_chan[row[3]] = row
        # Build normalized address key from channel name
        m = re.match(r"(只读|读写)([IQMV]+)(.+)", row[3])
        if m:
            area, addr_str = m.group(2), m.group(3)
            if area in ("I","Q","M") and "." in addr_str:
                num, bit = addr_str.split(".")
                key = f"{area}{int(num)}.{bit}"
            elif area == "V" and "." in addr_str:
                num, bit = addr_str.split(".")
                key = f"V{int(num)}.{bit}"
            elif area == "V" and addr_str.startswith("BUB"):
                key = f"VB{int(addr_str[3:])}"
            elif area == "V" and addr_str.startswith("WB"):
                key = f"VW{int(addr_str[2:])}"
            elif area == "V" and addr_str.startswith("DF"):
                key = f"VD{int(addr_str[2:])}"
            else:
                key = row[3]
            csv_by_addr[key] = row

# Define HMI-relevant addresses and descriptions
hmi_vars = [
    # DI inputs
    ("I0.0", "上缸进水流量开关"),
    ("I0.1", "上→下转移流量开关"),
    ("I0.2", "下缸排水流量开关"),
    ("I0.3", "系统复位按钮"),
    ("I0.4", "消音按钮"),
    ("I0.5", "上缸液位高位"),
    ("I0.6", "上缸液位低位"),
    ("I0.7", "下缸液位高位"),
    ("I1.0", "下缸液位低位"),
    ("I1.1", "急停按钮"),
    ("I1.2", "安全继电器反馈"),
    ("I8.0", "阀A开到位"),
    ("I8.1", "阀A关到位"),
    ("I8.2", "阀B开到位"),
    ("I8.3", "阀B关到位"),
    ("I8.4", "阀C开到位"),
    ("I8.5", "阀C关到位"),
    # DO outputs
    ("Q0.0", "潜水泵1输出"),
    ("Q0.1", "潜水泵2输出"),
    ("Q0.2", "阀A输出"),
    ("Q0.3", "阀B输出"),
    ("Q0.4", "阀C输出"),
    ("Q0.5", "上缸NC球阀输出"),
    ("Q0.6", "下缸NC球阀输出"),
    ("Q0.7", "报警声音输出"),
    ("Q8.0", "报警灯光输出"),
    # System command bits
    ("V0.0", "启动命令"),
    ("V0.1", "暂停命令（预留未实现）"),
    ("V0.2", "停止命令"),
    ("V0.3", "报警确认命令"),
    ("V0.4", "消音命令"),
    ("V0.5", "强制上缸空命令（预留未实现）"),
    ("V0.6", "RTC校时命令"),
    ("V0.7", "安全继电器故障确认命令"),
    # System status bits
    ("V1.0", "启动命令确认"),
    ("V1.1", "暂停命令确认（预留）"),
    ("V1.2", "停止命令确认"),
    ("V1.3", "报警确认完成"),
    ("V1.4", "消音完成"),
    ("V1.5", "强制修正完成"),
    ("V1.6", "上缸状态 0=空 1=满"),
    ("V1.7", "下缸状态 0=空 1=满"),
    # State words
    ("VW2", "下缸主状态机当前状态"),
    ("VW4", "注射泵状态码"),
    ("VW6", "当前最高优先级报警码"),
    ("VW8", "实验总换水次数目标(=VD414×VD24/1440)"),
    ("VW304", "上缸配液子流程状态"),
    ("VW306", "已完成下缸换水次数"),
    # HMI parameters
    ("VD10", "目标浓度设定值（v2.0新增）"),
    ("VD14", "母液浓度设定值（v2.0新增）"),
    ("VD24", "实验时长目标设定值(min)"),
    ("VD28", "S2搅拌+加药固定时长(s)"),
    ("VD54", "阀C动作超时保护时长(s)"),
    ("VD58", "潜水泵1动作超时保护时长(s)"),
    ("VD62", "潜水泵2动作超时保护时长(s)"),
    ("VD66", "阀A关闭后延时验证时长(s)"),
    ("VD108", "首轮S6排水时长默认值(s)"),
    ("VD350", "注射泵单步分辨率(uL/步)"),
    ("VD358", "阀A动作超时保护时长(s)"),
    ("VD362", "阀B动作超时保护时长(s)"),
    ("VD366", "实验时长累加值(min)"),
    ("VD370", "目标抽取母液体积(uL)"),
    ("VD414", "24h换水目标次数（v2.2新增）"),
    ("VD426", "周期尾端转移余量(s)（v2.2新增）"),
    ("VD430", "上缸配液安全余量(s)（v2.2新增）"),
    ("VD448", "S4等待超时阈值(s)"),
    ("VD452", "手动注射泵总加药量(uL)"),
    ("VD584", "本轮目标抽取母液体积(uL)"),
    # Measured values
    ("VD70", "S1上缸进水实测时长(s)"),
    ("VD82", "阀A开启瞬间流量计快照"),
    ("VD86", "流量计当前累计值"),
    ("VD90", "本次当前进水量(L)"),
    ("VD94", "瞬时流速(L/min)"),
    ("VD102", "本轮加药目标步数"),
    ("VD116", "S6滚动实测时长(s)，首轮存S4实测"),
    ("VD178", "S5运行已用时长(s)"),
    ("VD244", "周期倒计时器B当前值(s)"),
    ("VD256", "周期倒计时器A当前值(s)"),
    ("VD308", "阀A关阀快照（HMI可查看）"),
    ("VD316", "目标进水量(L)"),
    ("VD440", "累计加药量(uL)"),
    ("VD444", "S4等待时长内部变量(s)"),
    # Alarm words (bits)
    ("V300.0", "上缸漫溢报警"),
    ("V300.1", "下缸漫溢报警"),
    ("V300.2", "NC球阀-上缸动作"),
    ("V300.3", "NC球阀-下缸动作"),
    ("V300.4", "急停触发锁存"),
    ("V300.5", "安全继电器故障"),
    ("V300.6", "配液节奏严重滞后"),
    ("V300.7", "配液节奏滞后提示"),
    ("V301.0", "阀A关后延时验证仍有流"),
    ("V301.2", "阀A关到位反馈超时"),
    ("V301.3", "阀A关到位但仍有流"),
    ("V301.4", "阀A开到位反馈超时"),
    ("V301.5", "阀A开到位但无流"),
    ("V301.6", "S5触发新一轮S1时上缸非空"),
    ("V302.0", "阀B四态诊断异常"),
    ("V302.1", "阀B开到位反馈超时"),
    ("V302.2", "阀B开到位但无流"),
    ("V302.3", "阀B关到位反馈超时"),
    ("V302.4", "阀B关到位但仍有流"),
    ("V302.5", "阀C四态诊断异常"),
    ("V302.6", "阀C开到位反馈超时"),
    ("V302.7", "阀C开到位但无流"),
    ("V303.0", "阀C关到位反馈超时"),
    ("V303.1", "阀C关到位但仍有流"),
    ("V303.2", "S4等待超时报警"),
    ("V303.4", "注射泵通讯/动作异常"),
    ("V303.5", "RTC时钟丢失"),
    ("V303.6", "单轮换水周期超时"),
    ("V303.7", "PLC请求HMI同步RTC"),
    # System status
    ("VB305", "系统总状态字(0=良好/1=故障/2=急停)"),
    ("M16.4", "系统初始化完成标志"),
    ("M16.5", "注射泵RTU从站在线"),
    ("M16.6", "流量计RTU从站在线"),
    # Manual control
    ("V306.0", "手动开阀A命令"),
    ("V306.1", "手动关阀A命令"),
    ("V306.2", "手动开阀B命令"),
    ("V306.3", "手动关阀B命令"),
    ("V306.4", "手动开阀C命令"),
    ("V306.5", "手动关阀C命令"),
    ("V306.6", "手动启动潜水泵1命令"),
    ("V306.7", "手动停止潜水泵1命令"),
    ("V307.0", "手动启动潜水泵2命令"),
    ("V307.1", "手动停止潜水泵2命令"),
    ("V307.2", "手动注射泵启动命令"),
    ("V307.3", "手动注射泵停止/回零命令"),
    # Debug mode
    ("V309.0", "调试模式开关"),
    # Alarm ack mode
    ("V200.0", "报警确认模式(0=自动/1=人工)"),
    # Modbus comm status
    ("VB378", "MBUS_CTRL Error错误码"),
    ("VB379", "MBUS_MSG任务0 Error"),
    ("VB380", "MBUS_MSG任务2 Error"),
    ("VB381", "MBUS_MSG任务1 Error"),
    ("VB382", "MBUS_MSG任务3 Error"),
    ("VB383", "MBUS_MSG任务4 Error"),
    ("VW294", "注射泵连续失败计数"),
    ("VW296", "流量计连续失败计数"),
    # Manual syringe pump
    ("VW388", "手动注射泵模式(0=单次/1=循环)"),
    ("VW390", "手动注射泵子状态"),
    ("VD392", "手动注射泵累计加药量(uL)"),
    ("VD396", "手动注射泵剩余加药量(uL)"),
    # RTC
    ("VB900", "RTC年(BCD)"),
    ("VB901", "RTC月(BCD)"),
    ("VB902", "RTC日(BCD)"),
    ("VB903", "RTC时(BCD)"),
    ("VB904", "RTC分(BCD)"),
    ("VB905", "RTC秒(BCD)"),
    ("VB906", "RTC星期"),
    ("VB907", "RTC保留"),
    # HMI mirror parameters (UD area)
    ("VB456", "HMI参数镜像标志字节"),
    ("VD460", "HMI镜像 VD24_ExpTarget"),
    ("VD464", "HMI镜像 VD28_PreMixTime"),
    ("VD488", "HMI镜像 VD66_DelayA"),
    ("VD492", "HMI镜像 VD108_S6Default"),
    ("VD500", "HMI镜像 VD316_InletVol"),
    ("VD504", "HMI镜像 VD350_StepRes"),
    ("VD512", "HMI镜像 VD358_TimeoutA"),
    ("VD516", "HMI镜像 VD362_TimeoutB"),
    ("VD524", "HMI镜像 VD448_WaitTimeout"),
    ("VD528", "HMI镜像 VD452_ManualDose"),
    ("V536.0", "HMI镜像 V200_0_AckMode"),
]

# Generate markdown table
lines = []
lines.append("| PLC地址 | HMI变量名（建议） | 类型 | 读写 | PLC实际用途 | 备注 |")
lines.append("|---------|------------------|------|------|------------|------|")

for addr, desc in hmi_vars:
    if addr in csv_by_addr:
        row = csv_by_addr[addr]
        hmi_name = row[1]
        dtype = row[2]
        rw = row[4]
        notes = ""
    else:
        hmi_name = f"U1_???_{addr.replace(".", "_").replace("VB", "VB").replace("VW", "VW").replace("VD", "VD")}"
        dtype = "-"
        rw = "-"
        notes = "需新增到HMI"
    if addr in plc_usage:
        plc_rw = plc_usage[addr]["rw"]
        if notes: notes += "；"
        notes += f"PLC代码{plc_rw}"
    else:
        if notes: notes += "；"
        notes += "PLC代码未使用"
    lines.append(f"| {addr} | {hmi_name} | {dtype} | {rw} | {desc} | {notes} |")

with open(r"d:\work\CTI\archive\mcgspro\hmi_plc_master_table.md", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print(f"Generated master table with {len(hmi_vars)} variables")
