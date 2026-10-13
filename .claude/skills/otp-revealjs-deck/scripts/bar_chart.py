#!/usr/bin/env python3
"""Сгруппированная столбчатая диаграмма в цветах OTP как inline-SVG для слайда.

Вход — JSON-файл:
{
  "label": "Ошибки по категориям, май–сентябрь 2026",
  "series": [
    {"key": "an", "name": "analysis", "color": "#9e6ec6"},
    {"key": "ul", "name": "без метки", "style": "dashed"}
  ],
  "groups": [
    {"name": "май", "values": {"an": 3}},
    {"name": "июн", "values": {"an": 14, "ul": 2}}
  ]
}
Нулевые и отсутствующие значения не рисуются. style: "dashed" — пунктирный контур
без заливки (для «нет данных / не размечено»). Светлым цветам (лайм, серый) контур
добавляется автоматически.

Выход — <svg class="chart" ...> в stdout; вставьте его в разметку слайда
(класс .chart задаёт размер 1080×700 в otp.css).

Использование: python3 -I bar_chart.py spec.json > chart.svg
"""
import json
import sys

PALETTE = ['#9e6ec6', '#fe7c32', '#c1fd0e', '#262626', '#d8d8d8', '#c8dffc']
OUTLINE = {'#c1fd0e': '#9bcc00', '#d8d8d8': '#b5b5b5', '#c8dffc': '#9ab8e0'}


def esc(s):
	return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('"', '&quot;')


def main():
	if len(sys.argv) != 2:
		sys.exit(__doc__)
	spec = json.load(open(sys.argv[1], encoding='utf-8'))
	series, groups = spec['series'], spec['groups']
	for i, s in enumerate(series):
		s.setdefault('color', PALETTE[i % len(PALETTE)])

	W, base, top, left, right = 1080, 560, 120, 20, 1060
	peak = max([v for g in groups for v in g['values'].values()] + [1])
	k = (base - top) / peak
	slot = (right - left) / len(groups)
	most = max(sum(1 for s in series if g['values'].get(s['key'])) for g in groups)
	gap = 6
	w = int(min(34, (slot - 30 - gap * (most - 1)) / max(most, 1)))

	out = [f'<svg class="chart" viewBox="0 0 {W} 712" role="img" aria-label="{esc(spec.get("label", "Диаграмма"))}">',
	       f'\t<line x1="{left}" y1="{base}" x2="{right}" y2="{base}" stroke="#d8d8d8" stroke-width="2"/>',
	       '\t<g font-size="24" font-weight="600" fill="#000" text-anchor="middle">']
	months = []
	for i, g in enumerate(groups):
		items = [(s, g['values'][s['key']]) for s in series if g['values'].get(s['key'])]
		cx = left + slot * (i + 0.5)
		x0 = cx - (len(items) * w + (len(items) - 1) * gap) / 2
		for j, (s, v) in enumerate(items):
			x, h = x0 + j * (w + gap), round(v * k)
			y = base - h
			if s.get('style') == 'dashed':
				paint = 'fill="#ffffff" stroke="#8c8c8c" stroke-width="2" stroke-dasharray="6 4"'
			else:
				outline = OUTLINE.get(s['color'].lower())
				paint = f'fill="{s["color"]}"' + (f' stroke="{outline}"' if outline else '')
			out.append(f'\t\t<rect x="{x:.0f}" y="{y}" width="{w}" height="{h}" rx="3" {paint}/>'
			           f'<text x="{x + w / 2:.0f}" y="{y - 12}">{esc(v)}</text>')
		months.append(f'\t\t<text x="{cx:.0f}" y="{base + 40}">{esc(g["name"])}</text>')
	out += ['\t</g>', '\t<g font-size="24" fill="#4a4a4a" text-anchor="middle">', *months, '\t</g>',
	        '\t<g font-size="22" fill="#000">']

	# Легенда: по 4 в строке, две строки максимум
	for i, s in enumerate(series):
		x, y = left + (i % 4) * 250, 652 + (i // 4) * 44
		if s.get('style') == 'dashed':
			paint = 'fill="#ffffff" stroke="#8c8c8c" stroke-width="2" stroke-dasharray="4 3"'
		else:
			outline = OUTLINE.get(s['color'].lower())
			paint = f'fill="{s["color"]}"' + (f' stroke="{outline}"' if outline else '')
		out.append(f'\t\t<rect x="{x}" y="{y - 20}" width="24" height="24" rx="12" {paint}/>'
		           f'<text x="{x + 34}" y="{y}">{esc(s["name"])}</text>')
	out += ['\t</g>', '</svg>']
	print('\n'.join(out))


if __name__ == '__main__':
	main()
