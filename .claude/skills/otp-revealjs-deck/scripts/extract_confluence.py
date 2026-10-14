#!/usr/bin/env python3
"""Разбирает экспорт страницы Confluence (.doc, который на деле MIME/HTML-письмо).

Пишет в <outdir>:
  page.html    — исходный HTML страницы
  page.txt     — текст, ячейки таблиц разделены " | ", картинки как [IMG ...]
  tables.json  — все таблицы: список таблиц, таблица = список строк, строка = список ячеек
  img-N.<ext>  — вложенные картинки (скриншоты, диаграммы) с правильным расширением

Использование: python3 -I extract_confluence.py <file.doc> <outdir>
"""
import email
import html
import json
import os
import re
import sys

IMAGE_EXT = {b'\x89PNG': 'png', b'\xff\xd8\xff': 'jpg', b'GIF8': 'gif'}


def text_of(fragment):
	t = re.sub(r'(?is)<img[^>]*?(?:src|data-image-src)="([^"]*)"[^>]*>', r' [IMG \1] ', fragment)
	t = re.sub(r'<[^>]+>', ' ', t)
	return re.sub(r'\s+', ' ', html.unescape(t)).strip()


def page_text(page):
	t = re.sub(r'(?is)<(style|script)\b.*?</\1>', '', page)
	t = re.sub(r'(?i)<br\s*/?>|</(p|div|h\d|li|tr|table)>', '\n', t)
	t = re.sub(r'(?i)</t[dh]>', ' | ', t)
	t = re.sub(r'(?is)<img[^>]*?src="([^"]*)"[^>]*>', r'[IMG \1]', t)
	t = html.unescape(re.sub(r'<[^>]+>', '', t))
	t = re.sub(r'[ \t\xa0]+', ' ', t)
	return re.sub(r'\n\s*\n+', '\n', t).strip() + '\n'


def tables_of(page):
	tables = []
	for table in re.findall(r'(?is)<table\b.*?</table>', page):
		rows = []
		for row in re.findall(r'(?is)<tr\b.*?</tr>', table):
			cells = [text_of(c) for c in re.findall(r'(?is)<t[dh]\b[^>]*>(.*?)</t[dh]>', row)]
			if cells:
				rows.append(cells)
		if rows:
			tables.append(rows)
	return tables


def main():
	if len(sys.argv) != 3:
		sys.exit(__doc__)
	src, out = sys.argv[1], sys.argv[2]
	os.makedirs(out, exist_ok=True)
	msg = email.message_from_bytes(open(src, 'rb').read())

	page, images = None, 0
	for part in msg.walk():
		if part.is_multipart():
			continue
		data = part.get_payload(decode=True) or b''
		if part.get_content_type() == 'text/html' and page is None:
			page = data.decode(part.get_content_charset() or 'utf-8', 'replace')
			continue
		ext = next((e for sig, e in IMAGE_EXT.items() if data.startswith(sig)), None)
		if ext:
			images += 1
			name = os.path.basename(part.get('Content-Location', '')) or f'part{images}'
			path = os.path.join(out, f'img-{images}.{ext}')
			open(path, 'wb').write(data)
			print(f'image {path}  (в HTML: src="{name}")')

	if page is None:
		sys.exit('no text/html part found — is this a Confluence export?')
	open(os.path.join(out, 'page.html'), 'w', encoding='utf-8').write(page)
	open(os.path.join(out, 'page.txt'), 'w', encoding='utf-8').write(page_text(page))
	tables = tables_of(page)
	json.dump(tables, open(os.path.join(out, 'tables.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
	print(f'page.txt, page.html, tables.json ({len(tables)} tables, rows: {[len(t) for t in tables]}) -> {out}')


if __name__ == '__main__':
	main()
