# Макеты слайдов

Все классы уже есть в `assets/otp.css`. Каждый контентный слайд — это `<section>` → `<div class="slide">` с плашкой раздела, заголовком, телом и строкой источника; номер страницы скрипт ставит сам. Готовые примеры всех макетов — в `otp/index.html` в корне репозитория.

```html
<section id="уникальный-id">
	<div class="slide">
		<div class="section-bar">Раздел · подраздел</div>
		<h2>Заголовок — одна строка</h2>
		<!-- тело: один из макетов ниже -->
		<p class="source"><span>Источник:</span> Confluence · «Страница»</p>
	</div>
	<aside class="notes">
		<p>Абзац подстрочника.</p>
	</aside>
</section>
```

Тело слайда занимает примерно 780 px по высоте. Большинство рядов (`.row`, `.flow`, `.grid`, `.routes`) имеют высоту по содержимому и центрируются в свободном месте (`margin: auto 0`). Поэтому слайд с небольшим количеством текста не выглядит пустым сверху.

## Содержание
1. Карточки с фиолетовой шапкой — три тезиса
2. Шаги + макет формы
3. Таблица с метками-плашками
4. График + панель «Комментарии и выводы»
5. Большие числа + выноска
6. Чек-лист
7. Цепочка этапов (flow)
8. Сетка полей 3×2
9. Маршруты «метка → кто»

---

## 1. Три карточки (`.row` + `.pcard`)
Цель / подход / важно, шаги плана, итоги. Две–четыре карточки, по 15–25 слов в каждой.

```html
<div class="row">
	<div class="pcard">
		<div class="head">Что</div>
		<p class="body">Каждой ошибке в Jira ставим метку причины</p>
	</div>
	<!-- ещё 2 карточки -->
</div>
<div class="callout"><span class="bang">!</span><p>Главная мысль одной строкой</p></div>
```

## 2. Шаги + макет формы
Процесс «как заполнить». Слева нумерованные шаги, справа форма, нарисованная заново в HTML. Скриншоты с ФИО и клиентскими данными не вставлять.

```html
<div class="row" style="gap:64px">
	<div class="steps" style="gap:36px">
		<div class="item"><span class="n">1</span><p>Проект — <b>Liabilities and Investments (LICT)</b></p></div>
	</div>
	<div class="form">
		<div class="head">Создание задачи</div>
		<div class="fields">
			<div class="field"><span>Проект*</span><b>Liabilities and Investments (LICT)</b></div>
		</div>
	</div>
</div>
```

## 3. Таблица (`table.summary`, справочник — `table.summary.ref`)
Не больше 5–6 строк. Если строк больше, разбейте таблицу на два слайда или покажите выборку.

```html
<table class="summary ref">
	<tr><th>Метка</th><th>Название</th><th>Когда ставим</th></tr>
	<tr>
		<td class="label"><span class="tag analysis">analysis_error</span></td>
		<td class="name">Ошибка анализа / требований</td>
		<td>Кейс описан неполно или неверно…</td>
	</tr>
</table>
```

Плашки: `.tag.analysis` (фиолетовая), `.tag.impl` (оранжевая), `.tag.test` (лайм), `.tag.env` (тёмная), `.tag.none` (серая), `.tag.unlabeled` (пунктир — «нет значения»). Для другой предметной области переименуйте классы в `otp.css`, цвета оставьте.

## 4. График + панель выводов
SVG строит `scripts/bar_chart.py`. Цвета серий должны совпадать с цветами плашек на других слайдах.

```html
<div class="row" style="flex:1; margin:0">
	<!-- сюда вывод bar_chart.py -->
	<div class="panel" style="flex:1">
		<p class="pill-head">Комментарии и выводы</p>
		<div class="panel-body" style="gap:28px">
			<div class="item"><span class="n">1</span><p><b>88</b> ошибок, из них <b>62</b> с меткой</p></div>
		</div>
	</div>
</div>
```

## 5. Большие числа (`.stat`) + выноска
Три числа с подписью в одно предложение. `.num.small` — для длинных значений вроде «0 → 8 → 18».

```html
<div class="row">
	<div class="stat">
		<p class="num" style="color:#9e6ec6">62</p>
		<p class="text">ошибки разметили один раз, когда разрабатывали процесс</p>
	</div>
</div>
<div class="callout"><span class="bang">!</span><p>Вывод — <b>что делаем</b></p></div>
```

## 6. Чек-лист (`.asks`)
«Что просим от команды». Три–четыре пункта, каждый в одну строку.

```html
<div class="asks" style="gap:20px">
	<div class="ask">
		<svg viewBox="0 0 52 52" aria-hidden="true"><circle cx="26" cy="26" r="26" fill="#c1fd0e"/><path d="m16 27 7 7 13-15" fill="none" stroke="#000" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></svg>
		<p>Ставить метку причины сразу при создании задачи</p>
	</div>
</div>
```

## 7. Цепочка этапов (`.flow`)
Шаблон из 4–5 блоков. Ключевой блок выделяется классом `.accent` (лаймовый фон).

```html
<div class="flow">
	<div class="step-card">
		<span class="n">1</span>
		<h3>Тестовые данные</h3>
		<p>Клиент, логи и т.&nbsp;д.</p>
	</div>
	<div class="step-card accent">
		<span class="n" style="background:#ffffff">5</span>
		<h3>Ожидаемый результат</h3>
		<p>Со <b>ссылкой на документ</b></p>
	</div>
</div>
```

## 8. Сетка полей 3×2 (`.grid` + `.field-card`)
Шесть коротких карточек: название поля, что в нём, варианты значений (`.muted`).

```html
<div class="grid">
	<div class="field-card">
		<div class="fhead"><span class="n">6</span>Приоритет</div>
		<p>По умолчанию «Средний»</p>
		<p class="muted">Блокирующий · Критичный ·<br>Средний · Низкий</p>
	</div>
</div>
```

## 9. Маршруты (`.routes` + `.route`)
Правила вида «если X — то Y». Пояснение пишется мелким текстом в `<small>`.

```html
<div class="routes">
	<div class="route">
		<span><span class="tag analysis">analysis_error</span></span>
		<span class="arrow">→</span>
		<p><b>Аналитик по задаче</b><small>Пояснение к правилу</small></p>
	</div>
</div>
```
