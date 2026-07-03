#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""读取 references/gongzhonghao.xlsx，按阅读人数倒序输出高阅读标题清单
输出格式：阅读数<TAB>字数<TAB>标题（字数含标点和空格，供字数误差 ≤2 的复刻校验用）"""

import os
import sys

try:
    import openpyxl
except ImportError:
    print("缺少 openpyxl，请先执行: pip3 install openpyxl")
    sys.exit(1)

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "references", "gongzhonghao.xlsx")

wb = openpyxl.load_workbook(path)
ws = wb.active

rows = []
for row in ws.iter_rows(values_only=True):
    vals = list(row)
    if len(vals) < 4 or vals[1] is None or vals[3] is None:
        continue
    title = str(vals[1]).strip()
    try:
        reads = int(float(vals[3]))
    except (ValueError, TypeError):
        continue  # 表头等非数据行
    # 跳过朋友圈式长文（不是标题）
    if not title or "\n" in title or len(title) > 100:
        continue
    rows.append((reads, title))

rows.sort(reverse=True)
for reads, title in rows:
    print(f"{reads}\t{len(title)}字\t{title}")
