import csv
from pathlib import Path

OLD_CSV = Path(r"D:\work\CTI\archive\mcgspro\csv_output\西门子_S7_Smart200_以太网.csv")
NEW_CSV = Path(r"D:\work\CTI\archive\mcgspro\csv_output\McgsPro变量导入_单元1.csv")
OUT_CSV = Path(r"D:\work\CTI\archive\mcgspro\csv_output\西门子_S7_Smart200_以太网_合并导入_最新.csv")


def read_csv(path: Path):
    with path.open(encoding="gbk", newline="") as f:
        rows = list(csv.reader(f))
    return rows[:5], rows[5:]


def key(row):
    # 寄存器名称、数据类型、寄存器地址；去掉寄存器名称中的空格以兼容新旧格式
    return (row[5].replace(" ", ""), row[6], row[7])


def main():
    meta, old_data = read_csv(OLD_CSV)
    _, new_data = read_csv(NEW_CSV)

    merged = {}
    for r in old_data:
        if len(r) >= 8:
            merged[key(r)] = r

    added = []
    for r in new_data:
        if len(r) >= 8 and key(r) not in merged:
            merged[key(r)] = r
            added.append(r)

    # 保持旧顺序，新增放最后
    ordered = []
    seen = set()
    for r in old_data:
        if len(r) >= 8:
            k = key(r)
            if k not in seen:
                ordered.append(r)
                seen.add(k)
    ordered.extend(added)

    # 重新编号通道号
    for i, r in enumerate(ordered):
        r[0] = str(i)

    with OUT_CSV.open("w", encoding="gbk", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(meta)
        writer.writerows(ordered)

    print(f"合并完成: {OUT_CSV}")
    print(f"旧表通道数: {len(old_data)}")
    print(f"新增通道数: {len(added)}")
    print("新增通道列表:")
    for r in added:
        print(f"  {r[0]:>3} | {r[1]} | {r[3]} | {r[5]} | {r[6]} | {r[7]}")


if __name__ == "__main__":
    main()
