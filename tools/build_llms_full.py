"""Build llms-full.txt: the readable text of every indexable page, as Markdown.

Usage (from the repository root): python3 tools/build_llms_full.py .
Run after tools/build_pages.py, or after any change to page copy."""
import re, sys, html as H
ROOT = sys.argv[1]
B = 'https://www.allcleanz.co.uk/'
ORDER = ['index', 'services', 'end-of-tenancy-cleaning', 'deep-cleaning', 'domestic-cleaning', 'carpet-upholstery-cleaning',
         'office-cleaning', 'oven-cleaning', 'after-build-cleaning', 'pre-post-party-cleaning', 'fridge-cleaning',
         'window-cleaning', 'car-valeting', 'jet-washing', 'gutter-cleaning', 'bbq-cleaning', 'areas-we-cover', 'cleaners-huyton', 'cleaners-st-helens', 'cleaners-liverpool', 'about', 'join-the-team', 'privacy-policy']
SKIP = {'form', 'nav', 'script', 'style', 'svg', 'button', 'noscript'}
BLOCK = {'h1': '# ', 'h2': '## ', 'h3': '### ', 'p': '', 'li': '- ', 'blockquote': '> ', 'figcaption': '', 'dt': '', 'dd': ''}

def text_of(main):
    # remove skipped regions with regex first (simpler and reliable for this markup)
    for t in ('form', 'nav', 'script', 'style', 'svg', 'button'):
        main = re.sub(r'<%s\b.*?</%s>' % (t, t), ' ', main, flags=re.S)
    main = re.sub(r'<div class="ticker".*?</div>\s*</div>', ' ', main, flags=re.S)
    main = re.sub(r'<p class="dry-badge".*?</p>', ' ', main, flags=re.S)
    main = re.sub(r'<span class="ba__label[^>]*>.*?</span>', ' ', main, flags=re.S)
    out = []
    leaf = r'<(h1|h2|h3|p|li|blockquote|figcaption|dt|dd)\b[^>]*>((?:(?!<(?:h1|h2|h3|p|li|blockquote|figcaption|dt|dd)\b).)*?)</\1>'
    for m in re.finditer(leaf, main, re.S):
        t, inner = m.group(1), m.group(2)
        inner = re.sub(r'<br\s*/?>', ' ', inner)
        def link(a):
            href, label = a.group(1), re.sub(r'<[^>]+>', '', a.group(2)).strip()
            if not label: return ''
            if href.startswith('./'): href = href[2:]
            if not re.match(r'(https?:|mailto:|tel:|#)', href): href = B + href
            if href.startswith('#'): return label
            return '[%s](%s)' % (label, href)
        inner = re.sub(r'<a\b[^>]*href="([^"]+)"[^>]*>(.*?)</a>', link, inner, flags=re.S)
        txt = H.unescape(re.sub(r'<[^>]+>', '', inner))
        txt = re.sub(r'\s+', ' ', txt).strip()
        if txt: out.append(BLOCK[t] + txt)
    return out

parts = ['# All Cleanz: full site content', '',
         '> The text of every page on www.allcleanz.co.uk, for AI assistants and search tools. A shorter summary is at ' + B + 'llms.txt', '']
for slug in ORDER:
    s = open('%s/%s.html' % (ROOT, slug)).read()
    url = B if slug == 'index' else B + slug
    title = H.unescape(re.search(r'<title>(.*?)</title>', s).group(1))
    main = s[s.index('<main id="main">'):s.index('</main>')]
    lines = text_of(main)
    # demote page headings one level so each page sits under its own H1 marker
    body = [('#' + l) if l.startswith('#') else l for l in lines]
    block = []
    for i, l in enumerate(body):
        block.append(l)
        nxt = body[i + 1] if i + 1 < len(body) else ''
        if not (l.startswith('- ') and nxt.startswith('- ')):
            block.append('')
    parts += ['---', '', '# ' + title, '', 'URL: ' + url, ''] + block
txt = '\n'.join(parts)
txt = re.sub(r'\n{3,}', '\n\n', txt)
assert '—' not in txt
open(ROOT + '/llms-full.txt', 'w').write(txt)
print(len(txt), 'chars')
