import sys
import xlrd
from collections import defaultdict


def num(v):
    if isinstance(v, (int, float)):
        return float(v)
    try:
        return float(str(v).strip())
    except (ValueError, TypeError):
        return None


def analyze(path):
    sheet = xlrd.open_workbook(path).sheets()[0]
    title = str(sheet.cell_value(0, 1)).strip()

    overview = {}
    trend_start = None
    for r in range(sheet.nrows):
        key = str(sheet.cell_value(r, 1)).strip()
        if key == '阅读数据趋势明细':
            trend_start = r + 2
        val = num(sheet.cell_value(r, 2))
        if key and val is not None:
            overview[key] = val

    daily_total = {}
    channel_total = defaultdict(float)
    daily_channel = defaultdict(dict)
    if trend_start:
        for r in range(trend_start, sheet.nrows):
            date = str(sheet.cell_value(r, 1)).strip()
            channel = str(sheet.cell_value(r, 2)).strip()
            reads = num(sheet.cell_value(r, 3))
            shares = num(sheet.cell_value(r, 4))
            if not date or reads is None:
                continue
            if channel == '全部':
                daily_total[date] = (reads, shares or 0)
            elif channel:
                channel_total[channel] += reads
                daily_channel[date][channel] = reads

    reads = overview.get('阅读(人)', 0)
    sent = overview.get('送达人数', 0)
    msg_reads = overview.get('公众号消息阅读人数', 0)
    shares = overview.get('分享(人)', 0)
    share_reads = overview.get('分享产生的阅读人数', 0)
    likes = overview.get('点赞(人)', 0)
    favs = overview.get('收藏(人)', 0)
    looks = overview.get('在看(人)', 0)
    follows = overview.get('新增关注（人）', 0)
    finish = overview.get('完读率', 0)
    stay = overview.get('平均停留时长(秒)', 0)
    comments = overview.get('评论（条）', 0)

    days = sorted(daily_channel.keys())
    rec_by_day = [(d, daily_channel[d].get('推荐', 0)) for d in days]
    rec_total = channel_total.get('推荐', 0)

    pct = lambda a, b: f'{a / b * 100:.2f}%' if b else 'n/a'
    print(f'标题: {title}')
    print(f'阅读 {int(reads)} | 送达 {int(sent)} | 粉丝打开率 {pct(msg_reads, sent)}')
    print(f'完读率 {finish * 100 if finish < 1 else finish:.1f}% | 停留 {int(stay)}s')
    print(f'点赞 {int(likes)}({pct(likes, reads)}) | 收藏 {int(favs)}({pct(favs, reads)}) | '
          f'在看 {int(looks)}({pct(looks, reads)}) | 评论 {int(comments)}')
    print(f'分享 {int(shares)}({pct(shares, reads)}) | 分享回流 {int(share_reads)} | '
          f'回流效率 {share_reads / shares if shares else 0:.2f} 阅读/分享')
    print(f'新增关注 {int(follows)}({pct(follows, reads)})')
    print(f'推荐渠道合计 {int(rec_total)}（占阅读 {pct(rec_total, reads)}）')
    head = ' → '.join(f'{d[5:]}:{int(v)}' for d, v in rec_by_day[:5])
    print(f'推荐逐日: {head}')
    if days:
        first = days[0]
        fans_d1 = daily_channel[first].get('公众号消息', 0)
        rec_d1 = daily_channel[first].get('推荐', 0)
        share_d1 = daily_total.get(first, (0, 0))[1]
        print(f'首日({first}): 粉丝阅读 {int(fans_d1)} | 推荐阅读 {int(rec_d1)} | 分享 {int(share_d1)}')


if __name__ == '__main__':
    for p in sys.argv[1:]:
        analyze(p)
        print('-' * 60)
