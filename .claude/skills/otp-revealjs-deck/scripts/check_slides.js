#!/usr/bin/env node
// Рендерит каждый слайд презентации в PNG и ищет проблемы вёрстки:
//  - элементы, вылезающие за холст 1920×1080;
//  - контент, наезжающий на строку «Источник» / номер страницы внизу;
//  - заголовки h2 в две строки и больше (в шаблоне заголовок — одна строка);
//  - не загрузился Montserrat (тогда ширины текста в проверке неверные).
// Использование: node check_slides.js <path/to/index.html> <outdir>
const path = require( 'path' );
const fs = require( 'fs' );
const os = require( 'os' );
const { execSync } = require( 'child_process' );

// Локальная копия reveal.js нужной версии из npm — на случай, если cdnjs недоступен
// (например, в облачном контейнере). cdnjs раскладывает файлы пакета так: dist/** → корень,
// и добавляет .min-версии. По этому правилу и ищем файл в пакете.
const npmCache = {};
function localRevealFile( version, file ) {
	if( !npmCache[ version ] ) {
		const dir = path.join( os.tmpdir(), `reveal.js-${version}` );
		if( !fs.existsSync( path.join( dir, 'package' ) ) ) {
			fs.mkdirSync( dir, { recursive: true } );
			const tgz = execSync( `npm pack reveal.js@${version} --silent --pack-destination ${dir}` ).toString().trim().split( '\n' ).pop();
			execSync( `tar xzf ${path.join( dir, tgz )} -C ${dir}` );
		}
		npmCache[ version ] = path.join( dir, 'package' );
	}
	const plain = file.replace( /\.min\.(js|css)$/, '.$1' );
	for( const candidate of [ path.join( 'dist', plain ), plain ] ) {
		const full = path.join( npmCache[ version ], candidate );
		if( fs.existsSync( full ) ) return full;
	}
	return null;
}

function loadPlaywright() {
	try { return require( 'playwright' ); } catch ( e ) {}
	const root = execSync( 'npm root -g' ).toString().trim();
	return require( path.join( root, 'playwright' ) );
}

( async () => {
	const [ file, outdir ] = process.argv.slice( 2 );
	if( !file || !outdir ) {
		console.error( 'usage: node check_slides.js <index.html> <outdir>' );
		process.exit( 1 );
	}
	fs.mkdirSync( outdir, { recursive: true } );
	const { chromium } = loadPlaywright();
	const proxy = process.env.HTTPS_PROXY ? { server: process.env.HTTPS_PROXY } : undefined;
	const browser = await chromium.launch( { proxy } );
	const context = await browser.newContext( { viewport: { width: 1600, height: 900 } } );
	// Chromium за прокси может не доверять его CA. Шрифты Google качаем на стороне Node
	// (он доверяет CA через NODE_EXTRA_CA_CERTS) и отдаём браузеру — TLS при этом проверяется.
	await context.route( /^https:\/\/fonts\.(googleapis|gstatic)\.com\//, async route => {
		try { await route.fulfill( { response: await route.fetch() } ); }
		catch ( e ) { await route.abort(); }
	} );
	const missing = [];
	await context.route( /^https:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/reveal\.js\/([^/]+)\/(.+)$/, async route => {
		try {
			const response = await route.fetch();
			if( response.ok() ) return route.fulfill( { response } );
		} catch ( e ) {}
		const [ , version, file ] = route.request().url().match( /reveal\.js\/([^/]+)\/(.+)$/ );
		const local = localRevealFile( version, file );
		if( !local ) {
			missing.push( route.request().url() );
			return route.abort();
		}
		const type = local.endsWith( '.css' ) ? 'text/css' : 'application/javascript';
		await route.fulfill( { path: local, contentType: type } );
	} );
	const page = await context.newPage();
	page.on( 'pageerror', e => console.log( 'PAGE ERROR', e.message ) );
	await page.goto( 'file://' + path.resolve( file ), { waitUntil: 'networkidle' } );
	await page.evaluate( () => document.fonts.ready );
	if( !await page.evaluate( () => [ ...document.fonts ].some( f => f.family.replace( /"/g, '' ) === 'Montserrat' && f.status === 'loaded' ) ) ) {
		console.log( 'WARN Montserrat not loaded — text widths are approximate' );
	}

	if( missing.length ) {
		console.log( 'ERROR reveal.js file not found on cdnjs nor in the npm package — check the URL:\n  ' + missing.join( '\n  ' ) );
		await browser.close();
		process.exit( 2 );
	}
	const total = await page.evaluate( () => Reveal.getTotalSlides() );
	let problems = 0;
	for( let i = 0; i < total; i++ ) {
		await page.evaluate( i => Reveal.slide( i ), i );
		await page.waitForTimeout( 700 );
		const shot = path.join( outdir, `slide-${String( i + 1 ).padStart( 2, '0' )}.png` );
		await page.screenshot( { path: shot } );
		const issues = await page.evaluate( () => {
			const out = [];
			const canvas = Reveal.getCurrentSlide().firstElementChild;
			const c = canvas.getBoundingClientRect();
			const scale = c.width / 1920;
			const label = el => ( el.className && typeof el.className === 'string' ? '.' + el.className.split( ' ' )[ 0 ] : el.tagName.toLowerCase() )
				+ ' "' + ( el.textContent || '' ).trim().slice( 0, 40 ) + '"';
			for( const el of canvas.querySelectorAll( '*' ) ) {
				const r = el.getBoundingClientRect();
				if( r.right > c.right + 1 || r.bottom > c.bottom + 1 ) out.push( 'outside canvas: ' + label( el ) );
			}
			const footer = canvas.querySelector( '.source' );
			if( footer ) {
				const top = footer.getBoundingClientRect().top;
				for( const el of canvas.querySelectorAll( 'p, li, td, h2, h3, .callout, .pcard, .stat, .row, .panel, table' ) ) {
					if( el.closest( '.source' ) || el.classList.contains( 'page' ) ) continue;
					if( el.getBoundingClientRect().bottom > top - 8 * scale ) out.push( 'touches source line: ' + label( el ) );
				}
			}
			const h2 = canvas.querySelector( 'h2' );
			if( h2 ) {
				const lh = parseFloat( getComputedStyle( h2 ).lineHeight ) * scale;
				const lines = Math.round( h2.getBoundingClientRect().height / lh );
				if( lines > 1 ) out.push( `title wraps to ${lines} lines: "${h2.textContent.trim()}"` );
			}
			if( !Reveal.getCurrentSlide().querySelector( 'aside.notes' ) ) out.push( 'no speaker notes' );
			return [ ...new Set( out ) ];
		} );
		problems += issues.length;
		console.log( `slide ${i + 1}: ${issues.length ? issues.join( '; ' ) : 'ok'}  -> ${shot}` );
	}
	await browser.close();
	console.log( problems ? `${problems} issue(s) found` : 'all slides ok' );
	process.exit( problems ? 2 : 0 );
} )();
