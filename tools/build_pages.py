#!/usr/bin/env python3
"""Generate every inner page from index.html's header and footer plus the content below.

Usage (from the repository root):
    python3 tools/build_pages.py . <version>
    python3 tools/build_llms_full.py .

<version> is the ?v= cache-busting value for styles.css and main.js, e.g. 20261116-1.
Bump it whenever either file changes.

Edit the header, footer or homepage sections in index.html, or page copy in this file,
then run both commands. Service copy is taken from the client's old Wix pages
(lightly tidied, nothing added)."""
import json, re, sys
from urllib.parse import quote as q

ROOT = sys.argv[1]
SITE = 'https://www.allcleanz.co.uk/'
VER = sys.argv[2]

# ---------- 1. Point existing links at the new pages ----------
LINKS = {
    'end-of-tenancy': 'end-of-tenancy-cleaning',
    'deep-clean': 'deep-cleaning',
    'domestic-clean': 'domestic-cleaning',
    'carpet-upholstery': 'carpet-upholstery-cleaning',
    'office-cleaning': 'office-cleaning',
    'oven-cleaning': 'oven-cleaning',
    'after-build-clean': 'after-build-cleaning',
    'party-cleaning': 'pre-post-party-cleaning',
    'fridge-cleaning': 'fridge-cleaning',
    'window-cleaning': 'window-cleaning',
    'car-valeting': 'car-valeting',
    'jet-washing': 'jet-washing',
    'gutter-cleaning': 'gutter-cleaning',
    'bbq-cleaning': 'bbq-cleaning',
    'services': 'services',
    'about': 'about',
    'join-the-team': 'join-the-team',
    'clients': './#clients',
    'testimonials': './#testimonials',
}
OG_IMG = 'https://lukebrennan.github.io/AllCleanz/assets/img/og-image.jpg'
OG_NOTE = '  <!-- Preview: sharing image served from GitHub Pages. At launch, change og:image and twitter:image back to https://www.allcleanz.co.uk/assets/img/og-image.jpg -->\n'

def relink(html):
    for old, new in LINKS.items():
        html = html.replace('href="under-construction.html?page=%s"' % old, 'href="%s"' % new)
    # Services menu parent and footer link go to the services page (Book now stays on the homepage grid)
    html = html.replace('href="./#services" class="nav__parent"', 'href="services" class="nav__parent"')
    html = html.replace('<li><a href="./#services">Services</a></li>', '<li><a href="services">Services</a></li>')
    return html

for name in ('index.html', '404.html'):
    path = '%s/%s' % (ROOT, name)
    html = open(path).read()
    html = relink(html)
    html = re.sub(r'\?v=\d{8}-\d+', '?v=' + VER, html)
    if name == 'index.html':
        html = html.replace('<section class="section clients" aria-labelledby', '<section class="section clients" id="clients" aria-labelledby')
    open(path, 'w').write(html)

index = open(ROOT + '/index.html').read()
chrome_top = index[index.index('<body>'):index.index('<main id="main">')]
chrome_bottom = index[index.index('</main>'):]
# Same-page links on the homepage need the homepage path elsewhere
for frag in ('#quote-form', '#contact', '#services'):
    chrome_top = chrome_top.replace('href="%s"' % frag, 'href="./%s"' % frag)
    chrome_bottom = chrome_bottom.replace('href="%s"' % frag, 'href="./%s"' % frag)
chrome_top = chrome_top.replace('<li><a href="./" aria-current="page">Home</a></li>', '<li><a href="./">Home</a></li>')

ICON = '<svg class="ico"><use href="#i-%s"/></svg>'

def wa(text):
    return 'https://wa.me/447721938429?text=' + q(text, safe='')

def ticks(items):
    return '<ul class="ticks">' + ''.join('<li>%s<span>%s</span></li>' % (ICON % 'check', i) for i in items) + '</ul>'

def rooms(cards, label=None):
    out = '<ul class="rooms">'
    for title, body in cards:
        out += '<li class="room reveal"><h3>%s</h3>%s</li>' % (title, body)
    return out + '</ul>'

ALL_ROOMS = [
    ('All rooms', '<p>We vacuum and mop floors, clean doors and frames, polish door handles, remove cobwebs, wipe skirting, clean light switches, polish interior glass and window sills, spot clean dirt and stains from walls and remove waste.</p>'),
    ('The bedrooms', '<p>Clean wardrobes, bed frames, decorative items and electronics.</p>'),
    ('The bathroom', '<p>Disinfect and clean bathtub, shower and toilet bowl, clean tiles, polish mirrors, clean cabinets, descale sinks and clean taps.</p>'),
    ('The kitchen', '<p>Clean cupboards, clean dirt and stains off counter tops, clean the vent, scrub hob, knobs and burners, clean refrigerator and kitchen appliances.</p>'),
    ('The living room', '<p>Dust furniture (emphasis on fine details), dust all accessories, decorative items, shelves and hangings, clean electronics and vacuum upholstery.</p>'),
    ('Hallway &amp; stairs', '<p>Polish the front door and clean rugs.</p>'),
]


# ---------- Real work: before/after sliders, side-by-side pairs, photo galleries ----------
W = 'assets/img/work/'

def ba_slider(name, alt_before, alt_after, base=None):
    W = base or globals()['W']
    return (f'<div class="ba reveal" style="--pos: 50%">'
            f'<img class="ba__img" src="{W}{name}-after.webp" srcset="{W}{name}-after-500.webp 500w, {W}{name}-after-700.webp 700w, {W}{name}-after.webp 900w" sizes="(max-width: 960px) 92vw, 460px" alt="{alt_after}" width="900" height="1088" loading="lazy">'
            f'<div class="ba__before"><img class="ba__img" src="{W}{name}-before.webp" srcset="{W}{name}-before-500.webp 500w, {W}{name}-before-700.webp 700w, {W}{name}-before.webp 900w" sizes="(max-width: 960px) 92vw, 460px" alt="{alt_before}" width="900" height="1088" loading="lazy"></div>'
            '<span class="ba__label ba__label--before" aria-hidden="true">Before</span><span class="ba__label ba__label--after" aria-hidden="true">After</span>'
            '<span class="ba__handle" aria-hidden="true"><span class="ba__knob"><svg class="ico"><use href="#i-arrows"/></svg></span></span>'
            '<input class="ba__range" type="range" min="0" max="100" value="50" step="1" aria-label="Before and after comparison. Move to reveal more of the before or after photo">'
            '</div>')

def ba_pair(name, w, h, alt_before, alt_after):
    def fig(side, alt, label):
        return (f'<figure><img src="{W}{name}-{side}.webp" srcset="{W}{name}-{side}-400.webp 400w, {W}{name}-{side}.webp {w}w" '
                f'sizes="(max-width: 760px) 46vw, 370px" alt="{alt}" width="{w}" height="{h}" loading="lazy"><figcaption>{label}</figcaption></figure>')
    return '<div class="ba-pair reveal">' + fig('before', alt_before, 'Before') + fig('after', alt_after, 'After') + '</div>'

def gallery(items):
    sizes = '(max-width: 760px) 46vw, 370px' if len(items) == 2 else '(max-width: 1100px) 46vw, 270px'
    return ('<ul class="work-gallery%s">' % (' work-gallery--two' if len(items) == 2 else '')
            + ''.join(f'<li class="reveal"><img src="{W}{n}.webp" srcset="{W}{n}-400.webp 400w, {W}{n}.webp 720w" '
                      f'sizes="{sizes}" alt="{alt}" width="720" height="540" loading="lazy"></li>'
                      for n, alt in items)
            + '</ul>')

def work_section(title_id, h2, intro, inner, mint=True):
    cls = 'section section--mint work' if mint else 'section work'
    return (f'<section class="{cls}" aria-labelledby="{title_id}"><div class="container">'
            f'<div class="section-head reveal"><h2 id="{title_id}" class="section-title">{h2}</h2><p>{intro}</p></div>'
            f'{inner}</div></section>')

def inc(tagline, items):
    return '<p>%s</p><p class="room__inc"><strong>What&rsquo;s included:</strong> %s</p>' % (tagline, items)

PAGES = [
  {
    'slug': 'end-of-tenancy-cleaning',
    'name': 'End of Tenancy Cleaning',
    'short': 'End of Tenancy',
    'h1': ('End of Tenancy', 'Cleaning'),
    'title': 'End of Tenancy Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'End of tenancy cleaning across Merseyside and the North West, using a checklist approved by agencies so you get your deposit back. Call 07721 938429.',
    'lead': 'Using a comprehensive end of tenancy cleaning checklist approved by agencies, this professional commercial and domestic cleaning service will help to take the stress out of moving. It will also ensure your landlord receives a sparkly clean property, and you get your deposit back.',
    'img': ('services/end-of-tenancy-room', 1200, 900, ['-400 400w', '-720 720w', ' 1200w'], 'Bright, empty room with a fireplace and clean wooden floor'),
    'wa': "Hi All Cleanz, I'd like a quote for an end of tenancy clean please.",
    'body': lambda: (
      '<section class="section section--mint" aria-labelledby="inc-title"><div class="container">'
      '<div class="section-head reveal"><h2 id="inc-title" class="section-title">What&rsquo;s included</h2>'
      '<p>This service takes place once all your belongings have been removed and includes, but is not limited to, the following:</p></div>'
      + rooms(ALL_ROOMS) + '</div></section>'),
    'related': ['deep-cleaning', 'carpet-upholstery-cleaning', 'oven-cleaning', 'domestic-cleaning'],
  },
  {
    'slug': 'deep-cleaning',
    'name': 'Deep Cleaning',
    'short': 'Deep Cleaning',
    'h1': ('Deep', 'Cleaning'),
    'title': 'Deep Cleaning Services Merseyside &amp; North West | All Cleanz',
    'desc': 'A top to bottom deep clean of your home across Merseyside and the North West. Ideal before selling, after moving in or before a new baby. Call 07721 938429.',
    'lead': 'We know your time is precious, so let us take care of your domestic deep cleaning needs by getting into all the nooks and crannies around your home.',
    'img': ('services/deep-clean', 1200, 900, ['-400 400w', '-720 720w', ' 1200w'], 'Clean, organised kitchen shelf and worktop after a deep clean'),
    'wa': "Hi All Cleanz, I'd like a quote for a deep clean please.",
    'body': lambda: (
      '<section class="section" aria-labelledby="about-title"><div class="container split">'
      '<div class="reveal"><h2 id="about-title" class="section-title">Our deep clean is</h2>'
      + ticks([
          'A tailored service to all our cleaning customers',
          'A top to bottom thorough &lsquo;Spring&rsquo; clean, guaranteed to get your home in tip-top shape',
          'Ideal before selling your property or if you&rsquo;ve just moved into your new home',
          'Perfect to get your home ready before your new baby arrives',
        ]) + '</div>'
      '<div class="note reveal"><h3>No need to move belongings</h3><p>Deep clean services are done with all your belongings in place, whilst reaching those neglected areas during the cleaning process.</p></div>'
      '</div></section>'
      '<section class="section section--mint" aria-labelledby="inc-title"><div class="container">'
      '<div class="section-head reveal"><h2 id="inc-title" class="section-title">What&rsquo;s included</h2></div>'
      + rooms(ALL_ROOMS) + '</div></section>'),
    'related': ['end-of-tenancy-cleaning', 'domestic-cleaning', 'oven-cleaning', 'carpet-upholstery-cleaning'],
  },
  {
    'slug': 'domestic-cleaning',
    'name': 'Domestic Cleaning',
    'short': 'Domestic Cleaning',
    'h1': ('Domestic', 'Cleaning'),
    'title': 'Domestic Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'A personalised daily, weekly or monthly home clean tailored to your needs, across Merseyside and the North West. Call or WhatsApp All Cleanz on 07721 938429.',
    'lead': 'This personalised service will help to keep on top of all your domestic cleaning chores. A daily, weekly or monthly clean that is tailored to meet your needs.',
    'img': ('services/domestic-kitchen', 720, 540, ['-400 400w', ' 720w'], 'Clean, tidy kitchen with fitted units'),
    'wa': "Hi All Cleanz, I'd like a quote for a regular domestic clean please.",
    'body': lambda: (
      '<section class="section section--mint" aria-labelledby="inc-title"><div class="container">'
      '<div class="section-head reveal"><h2 id="inc-title" class="section-title">Room by room</h2></div>'
      + rooms([
          ('The bedrooms', inc('Your haven for relaxation and a peaceful night&rsquo;s sleep. Let us clean away the mess to create a soothing space.',
              'dust and wipe all accessible surfaces; wipe switches and handles; make the bed (if fresh linen has been left out); vacuum and mop the floor and remove rubbish.')),
          ('The bathroom', inc('A place for privacy and peace, for soaking and unwinding. Let us leave you singing in the shower.',
              'clean the toilet; scrub shower, bath and sink; clean cabinet exteriors and mirrors; wipe switches and handles; vacuum and mop the floor and rubbish removal.')),
          ('The kitchen', inc('The place of family congregations, the heart of the home. Let us make yours spotlessly clean and sanitised from any hazards to health.',
              'wash dishes or load the dishwasher; dust and wipe all accessible surfaces; wipe exterior of kitchen cupboards, oven, fridge and fixtures; wipe switches and handles; vacuum and mop floors; scrub the hob; wipe counter tops; clean the sink; put away clean dishes; rubbish and recycling removed.')),
          ('The living room', inc('One of the most used rooms in any household. Whether you&rsquo;re snuggling down on the sofa eating snacks, playing with the kids or entertaining friends, you&rsquo;re creating dirt, stains and smears on all the surfaces and floors. Let us bring a warm glow back to your hearth.',
              'dust and wipe all accessible surfaces; wipe switches and handles; clean mirrors; vacuum and mop floor and rubbish removal.')),
          ('Hallway &amp; stairs', inc('Often these are the areas that get dirtier than most as we pass along them on our way to the other rooms in the house. Let us light up the entrance to your home.',
              'polish the front door; dust woodwork; mopping and vacuuming; spot removal of mud, dirt and stains from walls, railings and stairs; wipe skirting and clean rugs.')),
        ]) + '</div></section>'),
    'related': ['deep-cleaning', 'oven-cleaning', 'carpet-upholstery-cleaning', 'end-of-tenancy-cleaning'],
  },
  {
    'slug': 'carpet-upholstery-cleaning',
    'name': 'Carpet &amp; Upholstery Cleaning',
    'short': 'Carpet &amp; Upholstery',
    'h1': ('Carpet &amp; Upholstery', 'Cleaning'),
    'title': 'Carpet &amp; Upholstery Cleaning Merseyside | All Cleanz',
    'desc': 'Texatherm® carpet, upholstery and hard floor cleaning across Merseyside and the North West. Textiles dry in 30 minutes, guaranteed. Call 07721 938429.',
    'lead': 'For carpet, upholstery and hard floor cleaning we use the most advanced cleaning system: the patented <a href="https://www.texatherm.com/" target="_blank" rel="noopener">Texatherm<sup>&reg;</sup> process</a>. This process combines market leading technology with state of the art equipment to produce a variety of cleaning methods, each with its own benefits.',
    'img': ('services/carpet-sofa', 720, 540, ['-400 400w', ' 720w'], 'Freshly cleaned grey corner sofa showing clean lines from upholstery cleaning'),
    'wa': "Hi All Cleanz, I'd like a quote for carpet or upholstery cleaning please.",
    'body': lambda: (
      '<section class="section" aria-labelledby="methods-title"><div class="container split">'
      '<div class="reveal"><h2 id="methods-title" class="section-title">Advanced carpet, upholstery &amp; hard floor cleaning</h2>'
      '<p>Our Texatherm<sup>&reg;</sup> trained technicians can clean carpets, upholstery and hard floors using multiple cleaning methods, all from just one machine. They can adapt immediately whilst on site, switching between cleaning methods and processes in minutes, depending on our client&rsquo;s needs.</p></div>'
      '<div class="note reveal"><h3>These methods include</h3>'
      + ticks(['Hot water extraction', 'Texatherm<sup>&reg;</sup> low moisture cleaning', 'Texatherm<sup>&reg;</sup> dual combination cleaning', 'Restorative cleaning', 'Hard floor cleaning', 'Upholstery and sofa cleaning'])
      + '</div></div></section>'
      '<section class="section section--mint" aria-labelledby="hwe-title"><div class="container split split--top">'
      '<div class="reveal"><h2 id="hwe-title" class="section-title section-title--sm">Hot water extraction</h2>'
      '<p>The hot water extraction (HWE) cleaning method is suitable for cleaning most carpets, sofas, upholstery and other textiles, as long as they are not water sensitive.</p>'
      '<p>To get the best performance from a carpet extraction machine, it needs to be able to pull air flow through the carpet backing. However, not all carpet types allow for this.</p>'
      '<p>Office carpet tiles, for example, are constructed with watertight backings, which stop any airflow from being pulled through the backing and up the carpet fibres. This lack of airflow dramatically reduces the performance of a hot water extraction machine, so a low moisture system may be better suited and will give superior results.</p></div>'
      '<div class="reveal"><h2 class="section-title section-title--sm">Low moisture cleaning</h2>'
      '<p>The Texatherm<sup>&reg;</sup> low moisture cleaning process is a great alternative to HWE. It uses a combination of chemicals that react with an absorbent heated pad to create a capillary wicking action that draws dirt and stains out of the carpet fibres and onto the pad.</p>'
      '<p>This method does not need airflow through the carpet backing to work effectively, so it gives safer, superior cleaning results on commercial carpet tiles that dry very quickly. The process is also much quieter and dramatically reduces cleaning time when compared with HWE cleaning.</p></div>'
      '</div></section>'
      '<section class="section" aria-labelledby="benefits-title"><div class="container split">'
      '<div class="reveal"><h2 id="benefits-title" class="section-title">Benefits of low moisture cleaning</h2>'
      + ticks([
          'A superior clean on synthetic commercial carpet tiles',
          'Cleaning time reduced by up to 60% when compared to conventional cleaning methods',
          'A more environmentally friendly way to clean carpets: water consumption is cut by up to 80%, and 80% less foul water returns to drains',
          'Low noise means less disruption in the workplace',
          'A low moisture clean, with all the benefits normally associated with a dry cleaning system',
          '30 minute drying time',
        ]) + '</div>'
      '<div class="dry-stat reveal"><span class="dry-stat__num">30</span><span class="dry-stat__unit">minutes</span>'
      '<p>Using the most advanced and environmentally friendly Texatherm<sup>&reg;</sup> cleaning machine and process means textiles will dry out in just 30 minutes, <strong>guaranteed.</strong></p></div>'
      '</div></section>'
      + work_section('work-title', 'Recent carpet cleaning', 'Photos from recent All Cleanz carpet cleaning jobs.',
        gallery([('carpet-rotary', 'Carpet cleaning machine at work in an empty room, with the cleaned carpet visibly lighter'),
                 ('carpet-doormat', 'Carpet by a front door, half cleaned, showing the dirty and clean sections side by side'),
                 ('carpet-lines', 'Freshly cleaned light carpet showing clean lines beside an uncleaned strip'),
                 ('carpet-machine', 'All Cleanz carpet cleaning machine being set up')]))),
    'related': ['office-cleaning', 'end-of-tenancy-cleaning', 'deep-cleaning', 'domestic-cleaning'],
  },
  {
    'slug': 'office-cleaning',
    'name': 'Office Cleaning',
    'short': 'Office Cleaning',
    'h1': ('Office', 'Cleaning'),
    'title': 'Office Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Flexible office and commercial cleaning contracts across Merseyside and the North West, from a daily clean to a few hours a week. Call 07721 938429.',
    'lead': 'Our range of services are tailored to the requirements of each business and setting. We offer a wealth of experience in a variety of settings and are experts in cleaning standard office and commercial buildings.',
    'img': ('services/office', 720, 540, ['-400 400w', ' 720w'], 'Gloved hand wiping a desk and keyboard, office cleaning'),
    'wa': "Hi All Cleanz, I'd like a quote for office cleaning please.",
    'body': lambda: (
      '<section class="section" aria-labelledby="contracts-title"><div class="container split">'
      '<div class="reveal"><h2 id="contracts-title" class="section-title">Flexible, professional cleaning contracts</h2>'
      '<p>Our staff are trusted, hard-working and highly trained cleaners. We reinforce their training and performance by making frequent site supervision and quality checks, ensuring you have complete confidence in the professional cleaning services that we provide.</p></div>'
      '<div class="note reveal"><h3>We offer</h3>'
      + ticks(['A daily office clean', 'A few hours per week', 'Periodical cleans to carpets and upholstery in office environments'])
      + '<a class="note__link" href="carpet-upholstery-cleaning">About our carpet &amp; upholstery cleaning ' + ICON % 'arrow' + '</a></div>'
      '</div></section>'),
    'related': ['carpet-upholstery-cleaning', 'deep-cleaning', 'end-of-tenancy-cleaning', 'oven-cleaning'],
  },
  {
    'slug': 'oven-cleaning',
    'name': 'Oven Cleaning',
    'short': 'Oven Cleaning',
    'h1': ('Oven', 'Cleaning'),
    'title': 'Oven Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Professional domestic and commercial oven cleaning across Merseyside and the North West. Safe to use straight after cleaning. Call 07721 938429.',
    'lead': 'Take your cooking to the next level with a professionally cleaned oven. Our highly experienced commercial and domestic oven cleaners will save you time and elbow grease, so why not leave the scrubbing to us? We will disassemble the oven and deep clean the parts.',
    'img': ('services/oven-clean', 720, 540, ['-400 400w', ' 720w'], 'Oven with a clear glass door and clean interior after oven cleaning'),
    'wa': "Hi All Cleanz, I'd like a quote for an oven clean please.",
    'body': lambda: (
      '<section class="section results" aria-labelledby="results-title"><div class="container results__grid">'
      '<div class="results__copy reveal"><h2 id="results-title" class="section-title">See the difference</h2>'
      '<p class="lead">A real oven clean by All Cleanz. Drag the slider to compare the before and after.</p>'
      '<p>All our cleaning products and techniques ensure your oven is spotlessly clean with no damage and minimal chemical use. The oven is safe to use straight after cleaning.</p>'
      '<h3 class="ticks__title">A clean oven ensures</h3>'
      + ticks(['Fire safety', 'Better performance and long life, saving you money on repairs', 'Free from oil, debris and bacteria'])
      + '<p class="results__sign">Keep the heat out of the kitchen with an All Cleanz oven clean.</p></div>'
      '<div class="ba reveal" style="--pos: 50%">'
      '<img class="ba__img" src="assets/img/before-after/oven-after.webp" srcset="assets/img/before-after/oven-after-500.webp 500w, assets/img/before-after/oven-after-700.webp 700w, assets/img/before-after/oven-after.webp 900w" sizes="(max-width: 960px) 92vw, 520px" alt="Oven after cleaning by All Cleanz, with a clear glass door and clean shelves" width="900" height="1088" loading="lazy">'
      '<div class="ba__before"><img class="ba__img" src="assets/img/before-after/oven-before.webp" srcset="assets/img/before-after/oven-before-500.webp 500w, assets/img/before-after/oven-before-700.webp 700w, assets/img/before-after/oven-before.webp 900w" sizes="(max-width: 960px) 92vw, 520px" alt="The same oven before cleaning, with the door glass coated in baked-on grease" width="900" height="1088" loading="lazy"></div>'
      '<span class="ba__label ba__label--before" aria-hidden="true">Before</span><span class="ba__label ba__label--after" aria-hidden="true">After</span>'
      '<span class="ba__handle" aria-hidden="true"><span class="ba__knob"><svg class="ico"><use href="#i-arrows"/></svg></span></span>'
      '<input class="ba__range" type="range" min="0" max="100" value="50" step="1" aria-label="Before and after comparison. Move to reveal more of the before or after photo">'
      '</div></div></section>'),
    'related': ['deep-cleaning', 'end-of-tenancy-cleaning', 'domestic-cleaning', 'carpet-upholstery-cleaning'],
  },
]

def split(title_id, h2, left, right_title, right, mint=False):
    cls = 'section section--mint' if mint else 'section'
    return (f'<section class="{cls}" aria-labelledby="{title_id}"><div class="container split">'
            f'<div class="reveal"><h2 id="{title_id}" class="section-title">{h2}</h2>{left}</div>'
            f'<div class="note reveal"><h3>{right_title}</h3>{right}</div>'
            '</div></section>')

def P(*paras):
    return ''.join('<p>%s</p>' % x for x in paras)

PAGES += [
  {
    'slug': 'after-build-cleaning',
    'name': 'After Build Cleaning',
    'short': 'After Build Cleaning',
    'h1': ('After Build', 'Cleaning'),
    'title': 'After Build Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'After build and post renovation cleaning for builders and home owners across Merseyside and the North West. Call or WhatsApp All Cleanz on 07721 938429.',
    'lead': 'All Cleanz provides builders and home owners a thorough, in-depth commercial or domestic cleaning service after builders, construction workers or tradesmen leave.',
    'img': ('services/after-build', 720, 540, ['-400 400w', ' 720w'], 'Worker pressure washing a building after construction'),
    'wa': "Hi All Cleanz, I'd like a quote for an after build clean please.",
    'body': lambda: split('about-title', 'Cleaning for the construction industry',
        P('We understand a building or development should look its absolute best when presented to your client. As builders and contractors leave a mess of dust, cement, stones, paints and granites all over the construction site, it is important and necessary to hire a highly professional trained team who specialise in cleaning for the construction industry.',
          'When it comes to builders cleans we understand every project is different. Therefore we will discuss your particular cleaning needs and create a cleaning schedule that suits you.'),
        'Builders cleans include', ticks(['Newly built buildings', 'Post renovation cleaning', 'Subsequent repairs cleaning'])),
    'related': ['end-of-tenancy-cleaning', 'deep-cleaning', 'window-cleaning', 'carpet-upholstery-cleaning'],
  },
  {
    'slug': 'pre-post-party-cleaning',
    'name': 'Pre &amp; Post Party Cleaning',
    'short': 'Pre &amp; Post Party Cleaning',
    'h1': ('Pre &amp; Post Party', 'Cleaning'),
    'title': 'Pre &amp; Post Party Cleaning Merseyside | All Cleanz',
    'desc': 'Pre and post party cleaning for homes and businesses across Merseyside and the North West, including weekends. Call or WhatsApp All Cleanz on 07721 938429.',
    'lead': 'We offer hosts a flawless service in pre and post party commercial or domestic cleaning, so you don&rsquo;t get a headache about the mess!',
    'img': ('services/party', 720, 540, ['-400 400w', ' 720w'], 'Vacuum cleaning confetti from a carpet after a party'),
    'wa': "Hi All Cleanz, I'd like a quote for a party clean please.",
    'body': lambda: split('about-title', 'Leave the clean up to us',
        P('After a long night partying the last thing you want to do is clean away the debris. Our professional party cleaners are perfectly qualified to provide first class cleaning every time.'),
        'Tailormade to suit you', P('This cleaning service is tailormade to suit your needs and includes weekend party cleaning services too.')),
    'related': ['deep-cleaning', 'carpet-upholstery-cleaning', 'domestic-cleaning', 'oven-cleaning'],
  },
  {
    'slug': 'fridge-cleaning',
    'name': 'Fridge Cleaning',
    'short': 'Fridge Cleaning',
    'h1': ('Fridge', 'Cleaning'),
    'title': 'Fridge Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Domestic and commercial fridge cleaning across Merseyside and the North West. Get rid of smells, spills and bacteria. Call All Cleanz on 07721 938429.',
    'lead': 'Your kitchen is not clean unless your fridge is clean. The fridge is often an overlooked area of commercial and domestic household sanitation.',
    'img': ('services/fridge-clean', 720, 540, ['-400 400w', ' 720w'], 'Clean fridge interior with clear shelves'),
    'wa': "Hi All Cleanz, I'd like a quote for a fridge clean please.",
    'body': lambda: split('about-title', 'Why clean your fridge?',
        P('We tend to keep our kitchen floors and surfaces immaculately clean, but the fridge can be neglected for months, even years.',
          'If a fridge is not cleaned regularly it can become a breeding ground for dangerous bacteria. These bacteria can survive at low temperatures, so not only will your fridge start to smell, but your food can become contaminated and unsafe to eat.'),
        'Get rid of', ticks(['Unpleasant smells', 'Lingering spills and stains', 'Dangerous bacteria and mould'])),
    'related': ['oven-cleaning', 'deep-cleaning', 'domestic-cleaning', 'end-of-tenancy-cleaning'],
  },
  {
    'slug': 'window-cleaning',
    'name': 'Window Cleaning',
    'short': 'Window Cleaning',
    'h1': ('Window', 'Cleaning'),
    'title': 'Window Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Interior and exterior window cleaning for homes, offices and shops across Merseyside and the North West. Call or WhatsApp All Cleanz on 07721 938429.',
    'lead': 'A commercial or domestic cleaning service of the highest quality, leaving you with windows that sparkle.',
    'img': ('services/window', 720, 540, ['-400 400w', ' 720w'], 'Gloved hand cleaning a window frame'),
    'wa': "Hi All Cleanz, I'd like a quote for window cleaning please.",
    'body': lambda: split('about-title', 'Inside and out',
        P('Most window cleaners do not perform interior window cleaning, but we can help with our expert window cleaning service.',
          'Our window cleaners are skilled at working in a commercial environment as well as in homes. We can provide exterior and interior window cleaning for homes, offices, shops and any other commercial spaces.'),
        'For shops and businesses', P('Let your customers on the outside see your displays on the inside with the help of our expert service.')),
    'related': ['office-cleaning', 'gutter-cleaning', 'jet-washing', 'after-build-cleaning'],
  },
  {
    'slug': 'car-valeting',
    'name': 'Car Valeting',
    'short': 'Car Valeting',
    'h1': ('Car', 'Valeting'),
    'title': 'Car Valeting Merseyside &amp; North West | All Cleanz',
    'desc': 'A professional car valeting home service across Merseyside and the North West, bringing your car back to showroom condition. Call 07721 938429.',
    'lead': 'A professional domestic car cleaning service that will bring your vehicle back to showroom condition.',
    'img': ('services/car', 720, 540, ['-400 400w', ' 720w'], 'Clean car interior and dashboard after valeting'),
    'wa': "Hi All Cleanz, I'd like a quote for car valeting please.",
    'body': lambda: (
      '<section class="section" aria-labelledby="about-title"><div class="container split split--top">'
      '<div class="reveal"><h2 id="about-title" class="section-title">What&rsquo;s included</h2><p class="lead">We&rsquo;ll pamper your car with some much needed care and attention by:</p>'
      + ticks([
          'Pressure washing to remove loose debris using snow foam',
          'Washing wheels with a non-corrosive cleaner',
          'Cleaning the vehicle using a 2-bucket wash system and soft wash mitts made of natural wool',
          'Drying the vehicle with waffle-weave textured microfibre towels and leather',
          'Dressing tyres with a high quality dressing to achieve a natural dark sheen',
          'Carefully cleaning interior and exterior glass and mirrors',
          'Dusting all plastic surfaces using hi-tech microfibre and high quality brushes',
          'Vacuuming interior carpets, boot space and upholstery',
        ]) + '</div>'
      '<div class="note reveal"><h3>A home service</h3><p>No need to waste time waiting in long queues, as our back to brand new cleaning service is provided as a home service.</p></div>'
      '</div></section>'),
    'related': ['jet-washing', 'carpet-upholstery-cleaning', 'window-cleaning', 'domestic-cleaning'],
  },
  {
    'slug': 'jet-washing',
    'name': 'Jet Washing',
    'short': 'Jet Washing',
    'h1': ('Jet', 'Washing'),
    'title': 'Jet Washing Merseyside &amp; North West | All Cleanz',
    'desc': 'Jet washing for driveways, patios, paving, decking and more across Merseyside and the North West. Call or WhatsApp All Cleanz on 07721 938429.',
    'lead': 'Removing stains, dirt and grime to transform the appearance of the outside of your home. We specialise in cleaning exterior surfaces professionally, whether for a commercial or residential property.',
    'img': ('services/jet-driveway', 1040, 780, ['-400 400w', '-720 720w', ' 1040w'], 'Red block paving driveway looking like new after jet washing by All Cleanz'),
    'wa': "Hi All Cleanz, I'd like a quote for jet washing please.",
    'body': lambda: split('about-title', 'Driveways, paths and patios',
        P('Jet washing is one of the most effective ways to remove built up dirt and grime from driveways, paths and patios, as the high pressure quickly removes dirt, moss and algae, as well as blasting out weeds rooted in the joints of the surface being cleaned.',
          'Clean surfaces last longer when washed and maintained over time.'),
        'Suitable for', ticks(['Driveways', 'Patios', 'Paving', 'Stone walls', 'Decking', 'Fencing', 'Some flat roofing systems']))
      + work_section('work-title', 'See the difference',
        'Real driveways and patios cleaned by All Cleanz. Drag the sliders to compare the before and after.',
        '<div class="ba-grid">'
        + ba_slider('drive-front', 'Herringbone block paving driveway covered in weeds and dirt before jet washing',
                    'The same driveway after jet washing, with the weeds gone and the paving bright red again')
        + ba_slider('drive-block', 'Grey block paving driveway with moss and green staining before jet washing',
                    'The same driveway after jet washing, clean and dark grey')
        + '</div>'
        + ba_pair('drive-garage', 640, 800, 'Long red block paving driveway with weeds growing between the blocks, before jet washing',
                  'The same driveway after jet washing, clean and bright red')
        + gallery([('patio-sandstone', 'Sandstone patio freshly jet washed beside a house'),
                   ('patio-slabs', 'Grey patio slabs being jet washed outside a patio door')])),
    'related': ['gutter-cleaning', 'window-cleaning', 'car-valeting', 'bbq-cleaning'],
  },
  {
    'slug': 'gutter-cleaning',
    'name': 'Gutter Cleaning',
    'short': 'Gutter Cleaning',
    'h1': ('Gutter', 'Cleaning'),
    'title': 'Gutter Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Residential and commercial gutter cleaning, drainpipe unblocking and soffit and fascia cleaning across Merseyside and the North West. Call 07721 938429.',
    'lead': 'When rainwater cannot run freely through your gutters it can lead to an overflow. This is the leading cause of water damage to properties in the UK. All Cleanz specialise in residential and commercial gutter cleaning.',
    'img': ('services/gutter-vacuum', 1040, 780, ['-400 400w', '-720 720w', ' 1040w'], 'All Cleanz high reach gutter vacuum pole cleaning the gutter of a brick house'),
    'wa': "Hi All Cleanz, I'd like a quote for gutter cleaning please.",
    'body': lambda: split('about-title', 'So you don&rsquo;t have to deal with',
        ticks(['Structural damage', 'Leaking roof and basement', 'Dampness and mould growth', 'Pest infestation']),
        'Services include', ticks(['Residential and commercial gutter cleaning', 'Unblocking drainpipes', 'Minor gutter repairs', 'Soffit and fascia cleaning', 'Conservatory roof cleaning']))
      + work_section('work-title', 'See the difference', 'Soffit, fascia and downpipe cleaning by All Cleanz.',
        ba_pair('gutter-fascia', 640, 640, 'White fascia and downpipe streaked with black dirt and algae before cleaning',
                'The same fascia and downpipe after cleaning, bright white again')),
    'related': ['jet-washing', 'window-cleaning', 'after-build-cleaning', 'office-cleaning'],
  },
  {
    'slug': 'bbq-cleaning',
    'name': 'BBQ Cleaning',
    'short': 'BBQ Cleaning',
    'h1': ('BBQ', 'Cleaning'),
    'title': 'BBQ Cleaning Merseyside &amp; North West | All Cleanz',
    'desc': 'Gas and charcoal BBQ cleaning across Merseyside and the North West, using non toxic products. Ready to use in 2 hours. Call All Cleanz on 07721 938429.',
    'lead': 'Be ready to enjoy BBQ season with an All Cleanz domestic BBQ clean.',
    'img': ('services/bbq', 720, 540, ['-400 400w', ' 720w'], 'Clean kettle barbecue, BBQ cleaning'),
    'wa': "Hi All Cleanz, I'd like a quote for a BBQ clean please.",
    'cta_name': 'BBQ cleaning',
    'body': lambda: split('about-title', 'Leave the grill to us',
        P('One of the least favourite cleaning jobs in any household is cleaning the barbie&rsquo;s racks and grills of burnt on carbon.',
          'Trained in cleaning all types of gas and charcoal BBQs, our professional cleaning specialists are happy to take that job out of your hands, to ensure your BBQ food tastes great.'),
        'Ready to use in 2 hours',
        P('We use 100% non toxic, non caustic cleaning products to remove all grease, fat and carbon. We&rsquo;ll also get into those hard to reach places, leaving your BBQ hygienically deep cleaned, like new and ready to use in 2 hours.',
          'Professional maintenance will help extend the life of your BBQ.')),
    'related': ['oven-cleaning', 'jet-washing', 'pre-post-party-cleaning', 'fridge-cleaning'],
  },
]

BY_SLUG = {p['slug']: p for p in PAGES}

def srcset(img):
    base = 'assets/img/' + img[0]
    return ', '.join('%s%s.webp %s' % (base, s.split(' ')[0], s.split(' ')[1]) for s in img[3])

def strip_tags(s):
    return re.sub(r'<[^>]+>', '', s).replace('&reg;', '®').replace('&amp;', '&').replace('&rsquo;', '’').replace('&lsquo;', '‘')

WHY = index[index.index('<!-- WHY US -->'):index.index('<!-- CLIENTS -->')]

for p in PAGES:
    url = SITE + p['slug']
    name_plain = strip_tags(p['name'])
    ld = {
        '@context': 'https://schema.org',
        '@graph': [
            {
                '@type': 'Service',
                '@id': url + '#service',
                'name': name_plain,
                'serviceType': name_plain,
                'url': url,
                'description': strip_tags(p['lead']),
                'image': SITE + 'assets/img/' + p['img'][0] + '.webp',
                'provider': {
                    '@type': 'LocalBusiness',
                    '@id': SITE + '#business',
                    'name': 'All Cleanz',
                    'url': SITE,
                    'telephone': '+447721938429',
                },
                'areaServed': [
                    {'@type': 'AdministrativeArea', 'name': 'Merseyside'},
                    {'@type': 'AdministrativeArea', 'name': 'North West England'},
                ],
            },
            {
                '@type': 'WebPage',
                '@id': url + '#webpage',
                'url': url,
                'name': strip_tags(p['title']),
                'description': strip_tags(p['desc']),
                'inLanguage': 'en-GB',
                'isPartOf': {'@id': SITE + '#website'},
                'about': {'@id': url + '#service'},
                'mainEntity': {'@id': url + '#service'},
                'primaryImageOfPage': {'@type': 'ImageObject', 'url': SITE + 'assets/img/' + p['img'][0] + '.webp'},
                'breadcrumb': {'@id': url + '#breadcrumb'},
            },
            {
                '@type': 'BreadcrumbList',
                '@id': url + '#breadcrumb',
                'itemListElement': [
                    {'@type': 'ListItem', 'position': 1, 'name': 'Home', 'item': SITE},
                    {'@type': 'ListItem', 'position': 2, 'name': 'Services', 'item': SITE + 'services'},
                    {'@type': 'ListItem', 'position': 3, 'name': name_plain, 'item': url},
                ],
            },
        ],
    }
    title = p['title']
    desc = p['desc']
    img = p['img']
    head = f'''<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
  <meta charset="utf-8">
  <!-- Preview passcode screen (remove at launch, along with assets/js/gate.js) -->
  <script>var gateOn=true;try{{if(gateOn&&localStorage.getItem('allcleanz-preview')!=='1')document.documentElement.classList.add('gate-locked')}}catch(e){{if(gateOn)document.documentElement.classList.add('gate-locked')}}</script>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="index, follow, max-image-preview:large">
  <meta name="theme-color" content="#43B288">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_GB">
  <meta property="og:site_name" content="All Cleanz">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
{OG_NOTE}  <meta property="og:image" content="{OG_IMG}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="All Cleanz, your professional domestic and commercial cleaning service based in Merseyside">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{OG_IMG}">
  <meta name="twitter:image:alt" content="All Cleanz, your professional domestic and commercial cleaning service based in Merseyside">

  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">

  <link rel="preload" href="assets/fonts/poppins-900-italic-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/css/styles.css?v={VER}">

  <script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
  </script>
</head>
'''
    top = chrome_top.replace('<li><a href="%s">' % p['slug'], '<li><a href="%s" aria-current="page">' % p['slug'], 1)

    hero = f'''<main id="main">
    <section class="hero hero--page" aria-labelledby="page-title">
      <div class="hero__bg" aria-hidden="true">
        <div class="bubbles"><span style="left:3%;width:16px;height:16px;animation-duration:12s;animation-delay:1s"></span><span style="left:8%;width:10px;height:10px;animation-duration:9s;animation-delay:4s"></span><span style="left:53%;width:20px;height:20px;animation-duration:14s;animation-delay:0s"></span><span style="left:93%;width:14px;height:14px;animation-duration:10s;animation-delay:2.5s"></span><span style="left:97%;width:18px;height:18px;animation-duration:12s;animation-delay:6s"></span></div>
        <span class="blob blob--1"></span>
        <span class="blob blob--2"></span>
        <svg class="spark spark--1"><use href="#i-sparkle"/></svg>
        <svg class="spark spark--3"><use href="#i-sparkle"/></svg>
        <svg class="spark spark--4"><use href="#i-sparkle"/></svg>
      </div>

      <div class="container hero__grid">
        <div class="hero__copy">
          <nav class="crumbs" aria-label="Breadcrumb">
            <ol>
              <li><a href="./">Home</a></li>
              <li><a href="services">Services</a></li>
              <li><span aria-current="page">{p['short']}</span></li>
            </ol>
          </nav>
          <h1 id="page-title" class="hero__title">
            <span class="hero__title-lg hero__title-lg--page">{p['h1'][0]} <em>{p['h1'][1]}</em></span>
            <span class="hero__title-sm">across Merseyside &amp; the North West</span>
          </h1>
          <p class="hero__lead">{p['lead']}</p>

          <div class="hero__ctas">
            <a href="tel:+447721938429" class="btn btn--white btn--lg">
              {ICON % 'phone'} Call 07721 938429
            </a>
            <a href="{wa(p['wa'])}" target="_blank" rel="noopener" class="btn btn--whatsapp btn--lg">
              {ICON % 'whatsapp'} WhatsApp Us
            </a>
          </div>
          <div class="hero__meta">
            <a href="https://share.google/Gg61WBgD1EcMRRVPn" target="_blank" rel="noopener" class="rating rating--hero"><span class="stars" aria-hidden="true"><span class="stars__base"><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg></span><span class="stars__fill" style="width: 98%"><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg></span></span><span><strong>4.9</strong> rating on Google</span></a>
            <a href="./#quote-form" class="hero__textlink">Request a quote online {ICON % 'arrow'}</a>
          </div>
        </div>

        <div class="page-photo">
          <img src="assets/img/{img[0]}.webp" srcset="{srcset(img)}" sizes="(max-width: 960px) 92vw, 520px" alt="{img[4]}" width="{img[1]}" height="{img[2]}" fetchpriority="high">
        </div>
      </div>

      <svg class="hero__wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 40c240 50 480 50 720 20S1200 0 1440 30v60H0Z"/></svg>
    </section>

    {p['body']()}

    '''

    cards = ''
    for slug in p['related']:
        r = BY_SLUG[slug]
        ri = r['img']
        cards += (f'<li class="service-card reveal"><a href="{slug}"><img src="assets/img/{ri[0]}-400.webp" '
                  f'alt="{ri[4]}" width="400" height="300" loading="lazy">'
                  f'<span class="service-card__title">{r["name"]}</span><span class="service-card__go" aria-hidden="true">{ICON % "arrow"}</span></a></li>')

    tail = f'''{WHY}
    <section class="section page-cta" aria-labelledby="cta-title">
      <div class="container">
        <div class="contact__card page-cta__card reveal">
          <img class="contact__bg" src="assets/img/mark-white.webp" alt="" width="333" height="246" loading="lazy">
          <div class="contact__copy">
            <h2 id="cta-title" class="section-title section-title--light">Get a quote for {p.get('cta_name', p['name'].lower())}</h2>
            <p>Call, WhatsApp or send us your details and we&rsquo;ll be happy to help.</p>
          </div>
          <div class="page-cta__btns">
            <a href="tel:+447721938429" class="btn btn--white btn--lg">{ICON % 'phone'} Call 07721 938429</a>
            <a href="{wa(p['wa'])}" target="_blank" rel="noopener" class="btn btn--whatsapp btn--lg">{ICON % 'whatsapp'} WhatsApp Us</a>
            <a href="./#quote-form" class="btn btn--ghost-light btn--lg">Request a quote online {ICON % 'arrow'}</a>
          </div>
        </div>
      </div>
    </section>

    <section class="section more-services" aria-labelledby="more-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="more-title" class="section-title">More cleaning services</h2>
        </div>
        <ul class="service-grid">{cards}</ul>
        <p class="services__more reveal"><a href="services">See all of our cleaning services</a></p>
      </div>
    </section>
  '''
    html = head + top + hero + tail + chrome_bottom
    html = html.replace('</ul>\n', '</ul>\n')
    open('%s/%s.html' % (ROOT, p['slug']), 'w').write(html)
    print('wrote', p['slug'])

# ---------- 3. Services, About and Join the Team pages ----------
CLIENTS = index[index.index('<!-- CLIENTS -->'):index.index('<!-- TESTIMONIALS -->')]
TESTIMONIALS = index[index.index('<!-- TESTIMONIALS -->'):index.index('<!-- RECENT WORK')]
GRID = index[index.index('<ul class="service-grid">'):]
GRID = GRID[:GRID.index('</ul>') + 5]
SERVICES_MORE = index[index.index('<p class="services__more reveal">'):]
SERVICES_MORE = SERVICES_MORE[:SERVICES_MORE.index('</p>') + 4]

def page_head(title, desc, url, ld, robots='index, follow, max-image-preview:large'):
    return f'''<!DOCTYPE html>
<html lang="en-GB" class="no-js">
<head>
  <meta charset="utf-8">
  <!-- Preview passcode screen (remove at launch, along with assets/js/gate.js) -->
  <script>var gateOn=true;try{{if(gateOn&&localStorage.getItem('allcleanz-preview')!=='1')document.documentElement.classList.add('gate-locked')}}catch(e){{if(gateOn)document.documentElement.classList.add('gate-locked')}}</script>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{desc}">
  <link rel="canonical" href="{url}">
  <meta name="robots" content="{robots}">
  <meta name="theme-color" content="#43B288">

  <meta property="og:type" content="website">
  <meta property="og:locale" content="en_GB">
  <meta property="og:site_name" content="All Cleanz">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{desc}">
  <meta property="og:url" content="{url}">
{OG_NOTE}  <meta property="og:image" content="{OG_IMG}">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="All Cleanz, your professional domestic and commercial cleaning service based in Merseyside">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{title}">
  <meta name="twitter:description" content="{desc}">
  <meta name="twitter:image" content="{OG_IMG}">
  <meta name="twitter:image:alt" content="All Cleanz, your professional domestic and commercial cleaning service based in Merseyside">

  <link rel="icon" type="image/png" sizes="32x32" href="assets/img/favicon-32.png">
  <link rel="apple-touch-icon" href="assets/img/apple-touch-icon.png">
  <link rel="manifest" href="site.webmanifest">

  <link rel="preload" href="assets/fonts/poppins-900-italic-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="assets/fonts/inter-latin.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="assets/css/styles.css?v={VER}">

  <script type="application/ld+json">
{json.dumps(ld, indent=2, ensure_ascii=False)}
  </script>
</head>
'''

def page_hero(crumb, h1, sub, lead, img, wa_text, meta_link, parent=None):
    parent_li = '<li><a href="%s">%s</a></li>\n              ' % (parent[1], parent[0]) if parent else ''
    src, w, h, sets, alt = img
    base = 'assets/img/' + src
    srcs = ', '.join('%s%s.webp %s' % (base, x.split(' ')[0], x.split(' ')[1]) for x in sets)
    return f'''<main id="main">
    <section class="hero hero--page" aria-labelledby="page-title">
      <div class="hero__bg" aria-hidden="true">
        <div class="bubbles"><span style="left:3%;width:16px;height:16px;animation-duration:12s;animation-delay:1s"></span><span style="left:8%;width:10px;height:10px;animation-duration:9s;animation-delay:4s"></span><span style="left:53%;width:20px;height:20px;animation-duration:14s;animation-delay:0s"></span><span style="left:93%;width:14px;height:14px;animation-duration:10s;animation-delay:2.5s"></span><span style="left:97%;width:18px;height:18px;animation-duration:12s;animation-delay:6s"></span></div>
        <span class="blob blob--1"></span>
        <span class="blob blob--2"></span>
        <svg class="spark spark--1"><use href="#i-sparkle"/></svg>
        <svg class="spark spark--3"><use href="#i-sparkle"/></svg>
        <svg class="spark spark--4"><use href="#i-sparkle"/></svg>
      </div>

      <div class="container hero__grid">
        <div class="hero__copy">
          <nav class="crumbs" aria-label="Breadcrumb">
            <ol>
              <li><a href="./">Home</a></li>
              {parent_li}<li><span aria-current="page">{crumb}</span></li>
            </ol>
          </nav>
          <h1 id="page-title" class="hero__title">
            <span class="hero__title-lg hero__title-lg--page">{h1[0]} <em>{h1[1]}</em></span>
            <span class="hero__title-sm">{sub}</span>
          </h1>
          <p class="hero__lead">{lead}</p>

          <div class="hero__ctas">
            <a href="tel:+447721938429" class="btn btn--white btn--lg">
              {ICON % 'phone'} Call 07721 938429
            </a>
            <a href="{wa(wa_text)}" target="_blank" rel="noopener" class="btn btn--whatsapp btn--lg">
              {ICON % 'whatsapp'} WhatsApp Us
            </a>
          </div>
          <div class="hero__meta">
            <a href="https://share.google/Gg61WBgD1EcMRRVPn" target="_blank" rel="noopener" class="rating rating--hero"><span class="stars" aria-hidden="true"><span class="stars__base"><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg></span><span class="stars__fill" style="width: 98%"><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg><svg><use href="#i-star"/></svg></span></span><span><strong>4.9</strong> rating on Google</span></a>
            {meta_link}
          </div>
        </div>

        <div class="page-photo">
          <img src="{base}.webp" srcset="{srcs}" sizes="(max-width: 960px) 92vw, 520px" alt="{alt}" width="{w}" height="{h}" fetchpriority="high">
        </div>
      </div>

      <svg class="hero__wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 40c240 50 480 50 720 20S1200 0 1440 30v60H0Z"/></svg>
    </section>

    '''

def cta_band(title, wa_text):
    return f'''
    <section class="section page-cta" aria-labelledby="cta-title">
      <div class="container">
        <div class="contact__card page-cta__card reveal">
          <img class="contact__bg" src="assets/img/mark-white.webp" alt="" width="333" height="246" loading="lazy">
          <div class="contact__copy">
            <h2 id="cta-title" class="section-title section-title--light">{title}</h2>
            <p>Call, WhatsApp or send us your details and we&rsquo;ll be happy to help.</p>
          </div>
          <div class="page-cta__btns">
            <a href="tel:+447721938429" class="btn btn--white btn--lg">{ICON % 'phone'} Call 07721 938429</a>
            <a href="{wa(wa_text)}" target="_blank" rel="noopener" class="btn btn--whatsapp btn--lg">{ICON % 'whatsapp'} WhatsApp Us</a>
            <a href="./#quote-form" class="btn btn--ghost-light btn--lg">Request a quote online {ICON % 'arrow'}</a>
          </div>
        </div>
      </div>
    </section>
  '''

def crumbs_ld(name, url, parent=None):
    items = [('Home', SITE)] + ([(parent[0], SITE + parent[1])] if parent else []) + [(name, url)]
    return {
        '@type': 'BreadcrumbList',
        '@id': url + '#breadcrumb',
        'itemListElement': [{'@type': 'ListItem', 'position': i + 1, 'name': n, 'item': u} for i, (n, u) in enumerate(items)],
    }

def write_page(slug, title, desc, ld_type, ld_name, crumb, hero, body, extra=None, parent=None, nodes=(), robots='index, follow, max-image-preview:large'):
    url = SITE + slug
    page = {'@type': ld_type, '@id': url + '#webpage', 'url': url, 'name': ld_name,
            'description': strip_tags(desc), 'inLanguage': 'en-GB',
            'about': {'@id': SITE + '#business'}, 'isPartOf': {'@id': SITE + '#website'},
            'breadcrumb': {'@id': url + '#breadcrumb'}}
    if extra:
        page.update(extra)
    ld = {'@context': 'https://schema.org', '@graph': [page, crumbs_ld(crumb, url, parent)] + list(nodes)}
    top = chrome_top.replace('<li><a href="%s">' % slug, '<li><a href="%s" aria-current="page">' % slug, 1)
    top = top.replace('<a href="%s" class="nav__parent">' % slug, '<a href="%s" class="nav__parent" aria-current="page">' % slug, 1)
    html = page_head(title, desc, url, ld, robots) + top + hero + body + chrome_bottom
    open('%s/%s.html' % (ROOT, slug), 'w').write(html)
    print('wrote', slug)

# Same order as the homepage grid
ORDER = re.findall(r'<li class="service-card[^"]*"><a href="([a-z-]+)"', GRID)
assert len(ORDER) == 14, ORDER

# Services
write_page('services',
    'Cleaning Services Merseyside &amp; North West | All Cleanz',
    'Domestic and commercial cleaning services across Merseyside and the North West, from end of tenancy and deep cleans to carpets, ovens and jet washing.',
    'CollectionPage', 'Cleaning services', 'Services',
    page_hero('Services', ('Our Cleaning', 'Services'), 'across Merseyside &amp; the North West',
        'All Cleanz have the expertise to deal with any cleaning challenge and are committed, professional and efficient, making sure you&rsquo;re satisfied every step of the way. You can count on All Cleanz to not only meet, but exceed all your cleaning expectations.',
        ('services/deep-clean', 1200, 900, ['-400 400w', '-720 720w', ' 1200w'], 'Clean, organised kitchen shelf and worktop after a deep clean'),
        "Hi All Cleanz, I'd like a quote please. I'm looking for: ",
        f'<a href="./#quote-form" class="hero__textlink">Request a quote online {ICON % "arrow"}</a>'),
    f'''<section class="section services" aria-labelledby="list-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="list-title" class="section-title">What we can do for you</h2>
          <p>Learn about the cleaning services we provide below, and let us know if you would like more information about a specific offering.</p>
        </div>
        {GRID}
        {SERVICES_MORE}
      </div>
    </section>

    {WHY}''' + cta_band('Not sure what you need?', "Hi All Cleanz, I'd like a quote please. I'm looking for: "),
    {'mainEntity': {'@type': 'ItemList', 'itemListElement': [
        {'@type': 'ListItem', 'position': i + 1, 'name': strip_tags(x['name']), 'url': SITE + x['slug']}
        for i, x in enumerate(sorted(PAGES, key=lambda x: ORDER.index(x['slug'])))]}})

# About
write_page('about',
    'About All Cleanz | Merseyside &amp; North West Cleaning Company',
    'All Cleanz is a trusted, professional domestic and commercial cleaning company based in Prescot, Merseyside, working across the North West. Call 07721 938429.',
    'AboutPage', 'About All Cleanz', 'About',
    page_hero('About', ('About', 'All Cleanz'), 'Cleaning company based in Prescot, Merseyside',
        'Welcome to All Cleanz, your trusted, reliable, professional domestic and commercial cleaning company based in Prescot, Merseyside and working across the North West.',
        ('about-cleaner', 1200, 959, ['-600 600w', '-800 800w', ' 1200w'], 'All Cleanz cleaner at work in a bathroom with a skylight'),
        "Hi All Cleanz, I'd like a quote please. I'm looking for: ",
        f'<a href="services" class="hero__textlink">Explore our services {ICON % "arrow"}</a>'),
    split('story-title', 'Professional quality cleaning with a personal touch',
        P('Based in Prescot, Merseyside, we offer a wide range of cleaning services for homes, offices and commercial properties throughout the region. Our expert cleaners are trained to be the best in their field and are happy to take on any cleaning job, from a routine domestic clean to a thorough top to bottom end of tenancy clean.',
          'Whether you require a regular cleaning service (daily, weekly or monthly) or just a one off clean, you can count on us. We have the experience and skills necessary to tackle just about every type of cleaning job that comes our way. With All Cleanz, clients know exactly what to expect: professionalism, efficiency and exceptional results.',
          'With high standards and reasonable prices, All Cleanz offer great value for money.'),
        'Experience the difference with All Cleanz',
        ticks(['Domestic and commercial cleaning across Merseyside and the North West',
               'Regular daily, weekly or monthly cleans, or a one off',
               'Texatherm<sup>&reg;</sup> carpet and upholstery cleaning: dry in 30 minutes, guaranteed',
               'Quality control including on-site inspections and customer surveys',
               'Rated 4.9 on Google'])) + f'''

    {CLIENTS}
    {TESTIMONIALS}''' + cta_band('Get a quote from All Cleanz', "Hi All Cleanz, I'd like a quote please. I'm looking for: "),
    {'mainEntity': {'@id': SITE + '#business'}})

# Join the Team
JOIN_FORM = f'''<section class="section section--mint" aria-labelledby="apply-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="apply-title" class="section-title">Work with us</h2>
          <p>Fill in your details below and choose the role you&rsquo;re applying for.</p>
        </div>
        <form class="contact-form join-form reveal" id="join-form" name="join-the-team" method="POST" data-netlify="true" netlify-honeypot="bot-field" enctype="multipart/form-data" novalidate>
          <input type="hidden" name="form-name" value="join-the-team">
          <p hidden><label>Leave this empty <input name="bot-field"></label></p>
          <div class="join-form__fields">
            <div class="field-row">
              <div class="field">
                <label for="j-first">First name</label>
                <input id="j-first" name="first_name" type="text" autocomplete="given-name" required>
              </div>
              <div class="field">
                <label for="j-last">Last name</label>
                <input id="j-last" name="last_name" type="text" autocomplete="family-name" required>
              </div>
            </div>
            <div class="field-row">
              <div class="field">
                <label for="j-email">Email</label>
                <input id="j-email" name="email" type="email" autocomplete="email" required>
              </div>
              <div class="field">
                <label for="j-phone">Phone</label>
                <input id="j-phone" name="phone" type="tel" autocomplete="tel" required>
              </div>
            </div>
            <fieldset class="join-form__group">
              <legend>I&rsquo;m applying for</legend>
              <div class="choices">
                <label class="choice"><input type="radio" name="position" value="Domestic Cleaner" required><span>Domestic Cleaner</span></label>
                <label class="choice"><input type="radio" name="position" value="Cleaning Supervisor"><span>Cleaning Supervisor</span></label>
                <label class="choice choice--wide"><input type="radio" name="position" value="Car Valeter"><span>Car Valeter</span></label>
              </div>
            </fieldset>
            <div class="field-row">
              <div class="field">
                <label for="j-date">When can you start?</label>
                <input id="j-date" name="start_date" type="date" required>
              </div>
              <div class="field">
                <label for="j-cv">Your CV <span class="field__optional">(optional)</span></label>
                <input id="j-cv" name="cv" type="file" accept=".pdf,.doc,.docx,.jpg,.jpeg,.png">
              </div>
            </div>
            <p class="form-note">We&rsquo;ll only use your details to consider your application. See our <a href="privacy-policy">privacy policy</a>.</p>
            <p class="quote__error" role="alert" hidden>Please fill in the highlighted details and choose a role.</p>
            <button class="btn btn--primary btn--lg contact-form__submit" type="submit">Send application {ICON % 'arrow'}</button>
          </div>
          <div class="join-form__done" tabindex="-1" hidden>
            <h3 class="quote__done-title">Thanks, <span data-join-name></span>!</h3>
            <p>To make sure your application reaches us, send it by email with your CV attached, or message us on WhatsApp.</p>
            <dl class="quote__summary"></dl>
            <div class="page-cta__btns">
              <a class="btn btn--primary" data-join-email href="mailto:enquiries@allcleanznorthwest.co.uk">{ICON % 'mail'} Email my application</a>
              <a class="btn btn--whatsapp" data-join-wa href="https://wa.me/447721938429" target="_blank" rel="noopener">{ICON % 'whatsapp'} Send on WhatsApp</a>
            </div>
          </div>
        </form>
      </div>
    </section>
'''
write_page('join-the-team',
    'Cleaning Jobs Merseyside | Join the Team | All Cleanz',
    'Apply to join the All Cleanz team as a domestic cleaner, cleaning supervisor or car valeter, working flexible hours throughout the week across Merseyside.',
    'WebPage', 'Join the All Cleanz team', 'Join the Team',
    page_hero('Join the Team', ('Join the', 'Team'), 'Work with All Cleanz',
        'Our fantastic All Cleanz cleaning team currently deal with all domestic and commercial cleaning jobs, working flexible hours throughout the week.',
        ('hero-cleaner', 1152, 960, ['-500 500w', '-800 800w', ' 1152w'], 'All Cleanz cleaner in uniform wiping down shower tiles'),
        "Hi All Cleanz, I'd like to apply to join the team.",
        f'<a href="#join-form" class="hero__textlink">Apply now {ICON % "arrow"}</a>'),
    JOIN_FORM)

# ---------- 4. Privacy policy ----------
PRIVACY = '''
    <section class="section legal" aria-label="Privacy policy">
      <div class="container prose">
        <p class="lead">This policy explains what personal information All Cleanz collects when you use our website or get in touch, how we use it, and the rights you have over it. We only collect what we need to answer your enquiry, carry out our cleaning services and run our business.</p>

        <h2>Who we are</h2>
        <p>All Cleanz (&ldquo;we&rdquo;, &ldquo;us&rdquo;, &ldquo;our&rdquo;) is a domestic and commercial cleaning company based in Prescot, Merseyside, working across the North West of England. We are responsible for the personal information described in this policy.</p>
        <p>If you have any questions about this policy or your information, contact us:</p>
        <ul>
          <li>Email: <a href="mailto:enquiries@allcleanznorthwest.co.uk">enquiries@allcleanznorthwest.co.uk</a></li>
          <li>Phone or WhatsApp: <a href="tel:+447721938429">07721 938429</a></li>
        </ul>

        <h2>The information we collect</h2>
        <h3>When you ask for a quote or contact us</h3>
        <p>If you use our quote form, call us, email us or message us on WhatsApp, we collect the details you give us. This usually includes your name, email address, phone number, town or postcode, the type and size of your property, the service you&rsquo;re interested in and any message you send.</p>
        <h3>When you book a clean</h3>
        <p>To carry out and invoice the work, we also keep details such as your address, how we can access the property, the services booked and any notes you give us about your home or premises.</p>
        <h3>When you apply to join the team</h3>
        <p>If you apply for a job with us, we collect your name, email address, phone number, the role you&rsquo;re applying for, when you can start, and your CV along with anything else you choose to include in it.</p>
        <h3>When you visit our website</h3>
        <p>The company that hosts our website automatically records basic technical information when pages are requested, such as your IP address, browser type and the pages visited. This is used to keep the website running securely. We do not use this information to identify you.</p>

        <h2>How we use your information</h2>
        <p>Under UK data protection law we must have a lawful reason for using your personal information. We use it:</p>
        <ul>
          <li><strong>To reply to your enquiry and give you a quote.</strong> This is a step you have asked us to take before entering into a contract with us.</li>
          <li><strong>To carry out the cleaning services you book</strong>, arrange visits and send invoices. This is necessary to perform our contract with you.</li>
          <li><strong>To keep business and tax records.</strong> This is necessary to meet our legal obligations.</li>
          <li><strong>To consider your job application</strong> and contact you about it. This is a step you have asked us to take before entering into a contract with us.</li>
          <li><strong>To keep our website secure</strong> and working properly. This is in our legitimate interests.</li>
        </ul>
        <p>We will not send you marketing messages unless you have asked us to, and we never sell your personal information.</p>

        <h2>Who we share it with</h2>
        <p>We only share your information with the people and services that help us run the business, and only as much as they need:</p>
        <ul>
          <li>the company that hosts our website and handles our online forms</li>
          <li>our email, phone and messaging providers, including WhatsApp if you choose to message us there</li>
          <li>our accountant, and HMRC where the law requires it</li>
        </ul>
        <p>Some of these providers may store information outside the UK, for example in the United States. Where that happens, they protect it with safeguards recognised under UK data protection law.</p>

        <h2>How long we keep it</h2>
        <ul>
          <li><strong>Enquiries and quotes</strong> that don&rsquo;t lead to a booking: up to 12 months.</li>
          <li><strong>Customer records and invoices:</strong> 6 years from the end of the tax year they relate to, as required for tax purposes.</li>
          <li><strong>Job applications</strong> that are not successful: up to 6 months. If you join the team, your application becomes part of your staff record.</li>
        </ul>
        <p>After these periods we securely delete or destroy the information.</p>

        <h2>Cookies</h2>
        <p>Our website does not use cookies for advertising or tracking. If we add website analytics in the future, we will update this policy and ask for your consent where the law requires it.</p>
        <p>Our website links to other sites, such as Facebook, Instagram, WhatsApp and Google. Those sites have their own privacy policies, and we are not responsible for how they use your information.</p>

        <h2>Your rights</h2>
        <p>You have the right to:</p>
        <ul>
          <li>ask for a copy of the personal information we hold about you</li>
          <li>ask us to correct information that is wrong or incomplete</li>
          <li>ask us to delete your information</li>
          <li>ask us to limit how we use your information, or object to us using it</li>
          <li>ask for your information in a format you can take to another provider</li>
        </ul>
        <p>Some of these rights only apply in certain situations. To use any of them, email or call us using the details above. We will respond within one month, and there is usually no charge.</p>

        <h2>How to complain</h2>
        <p>If you&rsquo;re unhappy with how we have handled your information, please contact us first so we can put it right. You also have the right to complain to the Information Commissioner&rsquo;s Office (ICO), the UK&rsquo;s data protection regulator, at <a href="https://ico.org.uk/make-a-complaint/" target="_blank" rel="noopener">ico.org.uk</a> or on 0303 123 1113.</p>

        <h2>Changes to this policy</h2>
        <p>We may update this policy from time to time. The latest version will always be on this page, with the date it was last updated.</p>
      </div>
    </section>
'''

legal_hero = f'''<main id="main">
    <section class="hero hero--page hero--legal" aria-labelledby="page-title">
      <div class="hero__bg" aria-hidden="true">
        <div class="bubbles"><span style="left:3%;width:16px;height:16px;animation-duration:12s;animation-delay:1s"></span><span style="left:53%;width:20px;height:20px;animation-duration:14s;animation-delay:0s"></span><span style="left:95%;width:14px;height:14px;animation-duration:10s;animation-delay:2.5s"></span></div>
        <span class="blob blob--1"></span>
        <svg class="spark spark--4"><use href="#i-sparkle"/></svg>
      </div>
      <div class="container">
        <nav class="crumbs" aria-label="Breadcrumb">
          <ol>
            <li><a href="./">Home</a></li>
            <li><span aria-current="page">Privacy Policy</span></li>
          </ol>
        </nav>
        <h1 id="page-title" class="hero__title">
          <span class="hero__title-lg hero__title-lg--page">Privacy <em>Policy</em></span>
          <span class="hero__title-sm">Last updated 13 November 2026</span>
        </h1>
      </div>
      <svg class="hero__wave" viewBox="0 0 1440 90" preserveAspectRatio="none" aria-hidden="true"><path d="M0 40c240 50 480 50 720 20S1200 0 1440 30v60H0Z"/></svg>
    </section>
'''
write_page('privacy-policy',
    'Privacy Policy | All Cleanz',
    'How All Cleanz collects, uses and protects your personal information when you use our website, ask for a quote or apply to join the team.',
    'WebPage', 'Privacy Policy', 'Privacy Policy',
    legal_hero, PRIVACY)

# ---------- 5. Location pages ----------
# Prescot has no page of its own: the homepage targets it, so a second page would compete with it.
# Distances are straight-line from Prescot town centre. Neighbourhood lists are geography,
# covered by the business's stated service area (Merseyside and the North West).
AREAS = ('Areas we cover', 'areas-we-cover')

def faq(items):
    out = '<div class="faq">'
    for q_, a_ in items:
        out += f'<details class="faq__item reveal"><summary>{q_}</summary><div class="faq__a"><p>{a_}</p></div></details>'
    return out + '</div>'

def faq_ld(url, items):
    return {'@type': 'FAQPage', '@id': url + '#faq', 'mainEntity': [
        {'@type': 'Question', 'name': strip_tags(q_), 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a_)}}
        for q_, a_ in items]}

QUOTE_A = ('Call or WhatsApp us on <a href="tel:+447721938429">07721 938429</a>, email '
           '<a href="mailto:enquiries@allcleanznorthwest.co.uk">enquiries@allcleanznorthwest.co.uk</a>, '
           'or fill in our <a href="./#quote-form">online quote form</a>.')
CARPET_A = ('Using the Texatherm<sup>&reg;</sup> cleaning machine and process, carpets and upholstery dry in just 30 minutes, guaranteed. '
            'See our <a href="carpet-upholstery-cleaning">carpet and upholstery cleaning</a> page.')
REGULAR_A = ('Yes. We provide a bespoke service to suit every need and budget, from regular daily, weekly or monthly cleans to a one off. '
             'See our <a href="domestic-cleaning">domestic cleaning</a> page for what&rsquo;s included.')

LOCATIONS = [
  {
    'slug': 'cleaners-huyton', 'town': 'Huyton', 'miles': 2.0, 'dist': 'about 2 miles',
    'img': ('work/drive-front-wide', 1040, 780, ['-400 400w', '-720 720w', ' 1040w'], 'Clean red herringbone block paving driveway in front of a house after jet washing'),
    'lead': 'All Cleanz is a domestic and commercial cleaning company based just down the road in Prescot, about 2 miles from Huyton. From regular home cleans to end of tenancy, carpet and office cleaning, we look after homes and businesses across Huyton.',
    'story': ('We already work in Huyton: our clients include King George V Sports Complex on Longview Lane.',
              'Whether you need a regular daily, weekly or monthly clean or just a one off, you can count on us. With All Cleanz, clients know exactly what to expect: professionalism, efficiency and exceptional results.'),
    'nearby': ['Huyton village', 'Roby', 'Page Moss', 'Swanside', 'Bowring Park', 'Longview'],
    'faq': [
      ('Do you cover Huyton?', 'Yes. All Cleanz is based in Prescot, about 2 miles from Huyton, and we clean homes and businesses across Huyton and the rest of Merseyside and the North West.'),
      ('Do you clean sports clubs and community venues?', 'Yes. Our clients include King George V Sports Complex in Huyton and Eccleston Park Lawn Tennis Club. See our <a href="office-cleaning">office and commercial cleaning</a> page.'),
      ('How quickly will my carpets dry?', CARPET_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in Huyton, based 2 miles away in Prescot. End of tenancy, deep cleans, carpets, offices and more. Call 07721 938429.',
  },
  {
    'slug': 'cleaners-st-helens', 'town': 'St Helens', 'miles': 3.1, 'dist': 'about 3 miles',
    'img': ('services/end-of-tenancy-room', 1200, 900, ['-400 400w', '-720 720w', ' 1200w'], 'Bright, empty room with a fireplace and clean wooden floor after an end of tenancy clean'),
    'lead': 'Looking for reliable cleaners in St Helens? All Cleanz is based in neighbouring Prescot, about 3 miles from St Helens town centre, and provides professional domestic and commercial cleaning across St Helens.',
    'story': ('From a routine domestic clean to a thorough top to bottom end of tenancy clean, our expert cleaners are happy to take on any cleaning job. We clean private homes, rental properties, offices and commercial premises.',
              'With high standards and reasonable prices, All Cleanz offer great value for money, and our quality control includes on-site inspections and customer surveys.'),
    'nearby': ['St Helens town centre', 'Eccleston', 'Thatto Heath', 'Sutton', 'Parr', 'Rainhill', 'Haydock'],
    'faq': [
      ('Do you cover St Helens?', 'Yes. We are based in Prescot, about 3 miles from St Helens town centre, and clean homes and businesses across St Helens and the rest of Merseyside and the North West.'),
      ('Do you do end of tenancy cleans in St Helens?', 'Yes. We use a comprehensive end of tenancy cleaning checklist approved by agencies, so your landlord receives a sparkly clean property and you get your deposit back. See our <a href="end-of-tenancy-cleaning">end of tenancy cleaning</a> page.'),
      ('Can I book a regular clean?', REGULAR_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in St Helens, based 3 miles away in Prescot. End of tenancy, deep cleans, carpets, offices and more. Call 07721 938429.',
  },
  {
    'slug': 'cleaners-liverpool', 'town': 'Liverpool', 'miles': 8.0, 'dist': 'about 8 miles',
    'img': ('services/office', 720, 540, ['-400 400w', ' 720w'], 'Gloved hand wiping a desk and keyboard during an office clean'),
    'lead': 'All Cleanz provides professional domestic and commercial cleaning across Liverpool, from our base in Prescot, about 8 miles from the city centre. Homes, rental properties, offices and commercial premises: we have the experience and skills to tackle just about every type of cleaning job.',
    'story': ('Our range of services is tailored to the requirements of each home, business and setting. We offer flexible office cleaning contracts, thorough end of tenancy and deep cleans, and regular daily, weekly or monthly home cleaning.',
              'Our staff are trusted, hard-working and highly trained cleaners, and we reinforce their training with frequent site supervision and quality checks.'),
    'nearby': ['Knotty Ash', 'West Derby', 'Childwall', 'Gateacre', 'Woolton', 'Wavertree', 'Liverpool city centre'],
    'faq': [
      ('Do you cover Liverpool?', 'Yes. We are based in Prescot, about 8 miles from Liverpool city centre, and clean homes and businesses across Liverpool and the rest of Merseyside and the North West.'),
      ('Do you clean offices in Liverpool?', 'Yes. We offer flexible, professional cleaning contracts: a daily office clean, a few hours per week, or periodical cleans to carpets and upholstery. See our <a href="office-cleaning">office cleaning</a> page.'),
      ('Can I book a regular clean?', REGULAR_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners covering Liverpool from our base in Prescot. Offices, end of tenancy, deep cleans, carpets and more. Call 07721 938429.',
  },
]

LOCATIONS += [
  {
    'slug': 'cleaners-whiston', 'town': 'Whiston', 'miles': 1.0, 'dist': 'about 1 mile',
    'img': ('services/deep-clean', 1200, 900, ['-400 400w', '-720 720w', ' 1200w'], 'Clean, organised kitchen shelf and worktop after a deep clean'),
    'lead': 'Whiston is right next door to our base in Prescot, about 1 mile away, so All Cleanz is never far from your door. We provide professional domestic and commercial cleaning for homes and businesses across Whiston.',
    'story': ('We know your time is precious, so let us take care of your cleaning, from a regular daily, weekly or monthly clean to a top to bottom deep clean that gets into all the nooks and crannies around your home.',
              'At All Cleanz we offer professional quality cleaning with a personal touch. With high standards and reasonable prices, we offer great value for money.'),
    'nearby': ['Whiston village', 'Halsnead', 'Cronton', 'Tarbock'],
    'faq': [
      ('Do you cover Whiston?', 'Yes. Whiston is about 1 mile from our base in Prescot, and we clean homes and businesses across Whiston and the rest of Merseyside and the North West.'),
      ('Do you offer deep cleans in Whiston?', 'Yes. Our deep clean is a top to bottom thorough clean, done with your belongings in place, reaching those neglected areas. It&rsquo;s ideal before selling, after moving in or before a new baby arrives. See our <a href="deep-cleaning">deep cleaning</a> page.'),
      ('Can I book a regular clean?', REGULAR_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in Whiston, just 1 mile from our Prescot base. Regular cleans, deep cleans, carpets, ovens and more. Call 07721 938429.',
  },
  {
    'slug': 'cleaners-rainhill', 'town': 'Rainhill', 'miles': 1.7, 'dist': 'under 2 miles',
    'img': ('work/patio-sandstone', 720, 540, ['-400 400w', ' 720w'], 'Sandstone patio freshly jet washed beside a house'),
    'lead': 'Rainhill sits just east of Prescot, under 2 miles from our base. All Cleanz provides domestic and commercial cleaning across Rainhill, inside and out, from regular home cleans to jet washing driveways and patios.',
    'story': ('Inside, we offer everything from a routine domestic clean to a thorough end of tenancy clean, plus Texatherm<sup>&reg;</sup> carpet and upholstery cleaning with a 30 minute drying time, guaranteed.',
              'Outside, we specialise in cleaning exterior surfaces professionally. Jet washing quickly removes dirt, moss and algae from driveways, paths and patios, and we also clean gutters, soffits and fascias.'),
    'nearby': ['Rainhill village', 'Rainhill Stoops', 'Eccleston Park', 'Bold', 'Sutton Manor'],
    'faq': [
      ('Do you cover Rainhill?', 'Yes. Rainhill is under 2 miles from our base in Prescot, and we clean homes and businesses across Rainhill and the rest of Merseyside and the North West.'),
      ('Do you clean driveways and patios in Rainhill?', 'Yes. Jet washing is suitable for driveways, patios, paving, stone walls, decking, fencing and some flat roofing systems. See our <a href="jet-washing">jet washing</a> page for before and after photos.'),
      ('How quickly will my carpets dry?', CARPET_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in Rainhill, under 2 miles from our Prescot base. Home cleans, carpets, jet washing and more. Call 07721 938429.',
  },
  {
    'slug': 'cleaners-kirkby', 'town': 'Kirkby', 'miles': 5.2, 'dist': 'about 5 miles',
    'img': ('services/oven-clean', 720, 540, ['-400 400w', ' 720w'], 'Oven with a clear glass door and clean interior after oven cleaning'),
    'lead': 'Kirkby is in Knowsley, like our home town of Prescot, about 5 miles from our base. All Cleanz provides professional domestic and commercial cleaning for homes, offices and commercial properties across Kirkby.',
    'story': ('Our expert cleaners are trained to be the best in their field and are happy to take on any cleaning job, from a routine domestic clean to a thorough top to bottom end of tenancy clean.',
              'We also take on the jobs nobody enjoys: oven cleaning, fridge cleaning and BBQ cleaning. For an oven clean we disassemble the oven and deep clean the parts, and it&rsquo;s safe to use straight after cleaning.'),
    'nearby': ['Kirkby town centre', 'Northwood', 'Tower Hill', 'Westvale', 'Southdene', 'Knowsley Village'],
    'faq': [
      ('Do you cover Kirkby?', 'Yes. Kirkby is about 5 miles from our base in Prescot, and we clean homes and businesses across Kirkby and the rest of Merseyside and the North West.'),
      ('Can you clean my oven?', 'Yes. Our domestic and commercial oven cleaners disassemble the oven and deep clean the parts, using techniques that leave it spotlessly clean with no damage and minimal chemical use. It&rsquo;s safe to use straight after cleaning. See our <a href="oven-cleaning">oven cleaning</a> page.'),
      ('Can I book a regular clean?', REGULAR_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in Kirkby, about 5 miles from our Prescot base. Regular cleans, end of tenancy, ovens, carpets and more. Call 07721 938429.',
  },
  {
    'slug': 'cleaners-widnes', 'town': 'Widnes', 'miles': 5.4, 'dist': 'about 5 miles',
    'img': ('services/gutter-vacuum', 1040, 780, ['-400 400w', '-720 720w', ' 1040w'], 'High reach gutter vacuum pole cleaning the gutter of a brick house'),
    'lead': 'Widnes is just over the border in Cheshire, about 5 miles from our base in Prescot and well within the North West area we cover. All Cleanz provides domestic and commercial cleaning for homes and businesses across Widnes.',
    'story': ('From regular home cleaning to end of tenancy, deep cleans and Texatherm<sup>&reg;</sup> carpet cleaning, we offer a bespoke service to suit every need and budget.',
              'We also look after the outside of your property. When rainwater can&rsquo;t run freely through your gutters it can lead to an overflow, so we offer residential and commercial gutter cleaning, drainpipe unblocking and soffit and fascia cleaning.'),
    'nearby': ['Widnes town centre', 'Hough Green', 'Ditton', 'Farnworth', 'Upton Rocks', 'Appleton'],
    'faq': [
      ('Do you cover Widnes?', 'Yes. Widnes is about 5 miles from our base in Prescot, and we clean homes and businesses across Widnes and the rest of the North West.'),
      ('Do you clean gutters in Widnes?', 'Yes. Our services include residential and commercial gutter cleaning, unblocking drainpipes, minor gutter repairs, soffit and fascia cleaning and conservatory roof cleaning. See our <a href="gutter-cleaning">gutter cleaning</a> page.'),
      ('How quickly will my carpets dry?', CARPET_A),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners in Widnes, about 5 miles from our Prescot base. Home cleans, carpets, gutters and more. Call or WhatsApp 07721 938429.',
  },
  {
    'slug': 'cleaners-warrington', 'town': 'Warrington', 'miles': 8.8, 'dist': 'about 9 miles',
    'img': ('work/carpet-rotary', 720, 540, ['-400 400w', ' 720w'], 'Carpet cleaning machine at work in an empty room, with the cleaned carpet visibly lighter'),
    'lead': 'All Cleanz covers Warrington from our base in Prescot, about 9 miles away. We provide professional domestic and commercial cleaning for homes, offices and commercial properties across Warrington.',
    'story': ('For carpet, upholstery and hard floor cleaning we use the patented Texatherm<sup>&reg;</sup> process, which combines market leading technology with state of the art equipment. Textiles dry in just 30 minutes, guaranteed.',
              'For businesses, we offer flexible cleaning contracts: a daily office clean, a few hours per week, or periodical cleans to carpets and upholstery, with frequent site supervision and quality checks.'),
    'nearby': ['Warrington town centre', 'Great Sankey', 'Penketh', 'Westbrook', 'Burtonwood', 'Orford'],
    'faq': [
      ('Do you cover Warrington?', 'Yes. Warrington is about 9 miles from our base in Prescot, and we clean homes and businesses across Warrington and the rest of the North West.'),
      ('Do you offer carpet cleaning in Warrington?', CARPET_A),
      ('Do you clean offices in Warrington?', 'Yes. We offer flexible, professional cleaning contracts: a daily office clean, a few hours per week, or periodical cleans to carpets and upholstery. See our <a href="office-cleaning">office cleaning</a> page.'),
      ('How do I get a quote?', QUOTE_A),
    ],
    'desc': 'Domestic and commercial cleaners covering Warrington from our Prescot base. Texatherm carpet cleaning, offices, home cleans and more. Call 07721 938429.',
  },
]
LOCATIONS.sort(key=lambda l: l['miles'])

def other_areas(current):
    links = ['<a href="./">Prescot</a>'] + [f'<a href="{l["slug"]}">{l["town"]}</a>' for l in LOCATIONS if l['slug'] != current]
    return ', '.join(links[:-1]) + ' and ' + links[-1]

for L in LOCATIONS:
    town, url = L['town'], SITE + L['slug']
    wa_text = "Hi All Cleanz, I'd like a quote for a clean in %s please. I'm looking for: " % town
    body = (split('local-title', f'Your local cleaning company in {town}', P(*L['story']),
                  f'Areas we cover around {town}', ticks(L['nearby']) + '<p class="note__more">Not listed? We work right across Merseyside and the North West, so just ask.</p>')
            + f'''
    <section class="section services" aria-labelledby="list-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="list-title" class="section-title">Cleaning services in {town}</h2>
          <p>Every one of our services is available in {town}. Choose a service to find out more.</p>
        </div>
        {GRID}
      </div>
    </section>
    {TESTIMONIALS}
    <section class="section section--mint" aria-labelledby="faq-title">
      <div class="container">
        <div class="section-head reveal"><h2 id="faq-title" class="section-title">Cleaners in {town}: your questions</h2></div>
        {faq(L['faq'])}
      </div>
    </section>
    {cta_band('Get a quote for a clean in ' + town, wa_text)}
    <section class="section areas-more" aria-label="Other areas">
      <div class="container"><p class="services__more reveal">We also cover {other_areas(L['slug'])}. <a href="areas-we-cover">See all the areas we cover</a>.</p></div>
    </section>
''')
    service = {'@type': 'Service', '@id': url + '#service', 'name': f'Cleaning services in {town}',
               'serviceType': 'Domestic and commercial cleaning', 'url': url,
               'provider': {'@type': 'LocalBusiness', '@id': SITE + '#business', 'name': 'All Cleanz', 'url': SITE, 'telephone': '+447721938429'},
               'areaServed': {'@type': 'City', 'name': town}}
    write_page(L['slug'],
        f'Cleaners in {town} | Domestic &amp; Commercial | All Cleanz',
        L['desc'], 'WebPage', f'Cleaners in {town}', town,
        page_hero(town, ('Cleaners in', town), 'Domestic &amp; commercial cleaning', L['lead'], L['img'], wa_text,
                  f'<a href="./#quote-form" class="hero__textlink">Request a quote online {ICON % "arrow"}</a>', parent=(AREAS[0], AREAS[1])),
        body, extra={'mainEntity': {'@id': url + '#service'}}, parent=(AREAS[0], AREAS[1]),
        nodes=[service, faq_ld(url, L['faq'])])

# Areas we cover
area_cards = ('<ul class="rooms rooms--areas">'
    '<li class="room reveal"><h3><a href="./">Prescot</a></h3><p>Our home base. Domestic and commercial cleaning across Prescot, Eccleston Park, Knowsley Village and Cronton.</p></li>'
    + ''.join(f'<li class="room reveal"><h3><a href="{l["slug"]}">{l["town"]}</a></h3><p>{l["dist"][0].upper() + l["dist"][1:]} from our base. Covering {", ".join(l["nearby"][:-1])} and {l["nearby"][-1]}.</p></li>' for l in LOCATIONS)
    + '</ul>')
write_page('areas-we-cover',
    'Areas We Cover | Cleaners Across Merseyside | All Cleanz',
    'All Cleanz is based in Prescot and provides domestic and commercial cleaning across Merseyside and the North West, including Huyton, St Helens and Liverpool.',
    'CollectionPage', 'Areas we cover', 'Areas we cover',
    page_hero('Areas we cover', ('Areas We', 'Cover'), 'Merseyside &amp; the North West',
        'All Cleanz is based in Prescot and provides professional domestic and commercial cleaning for homes, offices and commercial properties throughout Merseyside and the North West.',
        ('hero-cleaner', 1152, 960, ['-500 500w', '-800 800w', ' 1152w'], 'All Cleanz cleaner in uniform wiping down shower tiles'),
        "Hi All Cleanz, I'd like a quote please. I'm looking for: ",
        f'<a href="services" class="hero__textlink">Explore our services {ICON % "arrow"}</a>'),
    f'''<section class="section section--mint" aria-labelledby="areas-title">
      <div class="container">
        <div class="section-head reveal">
          <h2 id="areas-title" class="section-title">Where we clean</h2>
          <p>Don&rsquo;t see your area? We work right across Merseyside and the North West, so call or WhatsApp us on <a href="tel:+447721938429">07721 938429</a> to check.</p>
        </div>
        {area_cards}
      </div>
    </section>
    {WHY}''' + cta_band('Get a quote from All Cleanz', "Hi All Cleanz, I'd like a quote please. I'm looking for: "),
    extra={'mainEntity': {'@type': 'ItemList', 'itemListElement': [
        {'@type': 'ListItem', 'position': 1, 'name': 'Prescot', 'url': SITE}] + [
        {'@type': 'ListItem', 'position': i + 2, 'name': l['town'], 'url': SITE + l['slug']} for i, l in enumerate(LOCATIONS)]}})

# ---------- 6. Keep everything that lists the towns in step with LOCATIONS ----------
# Turning a town off = delete its entry above and re-run this script. Its page, homepage link,
# sitemap entry and llms.txt line all go; add a 301 to /areas-we-cover in netlify.toml if it was live.
import glob, os
live = {l['slug'] for l in LOCATIONS}
for f in glob.glob(ROOT + '/cleaners-*.html'):
    if os.path.basename(f)[:-5] not in live:
        os.remove(f)
        print('removed', os.path.basename(f))

def town_list(links):
    return ', '.join(links[:-1]) + ' and ' + links[-1]

path = ROOT + '/index.html'
html = open(path).read()
para = ('<p>Based in Prescot, we clean homes and businesses across Merseyside and the North West, including '
        + town_list([f'<a href="{l["slug"]}">{l["town"]}</a>' for l in LOCATIONS])
        + '. <a href="areas-we-cover">See all the areas we cover</a>.</p>')
html, n = re.subn(r'<p>Based in Prescot, we clean homes and businesses across Merseyside and the North West, including .*?</p>', para, html, count=1)
assert n == 1, 'homepage areas paragraph not found'
open(path, 'w').write(html)

path = ROOT + '/sitemap.xml'
xml = open(path).read()
xml = re.sub(r'  <url>\n    <loc>https://www\.allcleanz\.co\.uk/cleaners-[a-z-]+</loc>.*?</url>\n', '', xml, flags=re.S)
entries = ''.join(
    f'  <url>\n    <loc>{SITE}{l["slug"]}</loc>\n    <lastmod>2026-11-17</lastmod>\n    <changefreq>monthly</changefreq>\n'
    f'    <priority>0.7</priority>\n    <image:image>\n      <image:loc>{SITE}assets/img/{l["img"][0]}.webp</image:loc>\n    </image:image>\n  </url>\n'
    for l in LOCATIONS)
anchor = f'  <url>\n    <loc>{SITE}about</loc>'
assert anchor in xml
open(path, 'w').write(xml.replace(anchor, entries + anchor))

path = ROOT + '/llms.txt'
txt = '\n'.join(line for line in open(path).read().split('\n') if '/cleaners-' not in line)
lines = ''.join(f'- [Cleaners in {l["town"]}]({SITE}{l["slug"]}): Domestic and commercial cleaning in {l["town"]}, {l["dist"]} from our Prescot base\n' for l in LOCATIONS)
anchor = f'- [About]({SITE}about)'
assert anchor in txt
open(path, 'w').write(txt.replace(anchor, lines + anchor))
print('towns:', ', '.join(l['town'] for l in LOCATIONS))

# ---------- 7. Our Work gallery ----------
OVEN = 'assets/img/before-after/'
work_body = (
    work_section('drive-title', 'Driveways &amp; patios',
        'Jet washing removes dirt, moss, algae and weeds from block paving and patios. Drag the sliders to compare. <a href="jet-washing">About our jet washing</a>.',
        '<div class="ba-grid">'
        + ba_slider('drive-front', 'Herringbone block paving driveway covered in weeds and dirt before jet washing',
                    'The same driveway after jet washing, with the weeds gone and the paving bright red again')
        + ba_slider('drive-block', 'Grey block paving driveway with moss and green staining before jet washing',
                    'The same driveway after jet washing, clean and dark grey')
        + '</div>'
        + ba_pair('drive-garage', 640, 800, 'Long red block paving driveway with weeds growing between the blocks, before jet washing',
                  'The same driveway after jet washing, clean and bright red')
        + gallery([('patio-sandstone', 'Sandstone patio freshly jet washed beside a house'),
                   ('patio-slabs', 'Grey patio slabs being jet washed outside a patio door')]), mint=True)
    + work_section('oven-title', 'Ovens',
        'We disassemble the oven and deep clean the parts. <a href="oven-cleaning">About our oven cleaning</a>.',
        '<div class="ba-grid ba-grid--one">'
        + ba_slider('oven', 'The oven before cleaning, with the door glass coated in baked-on grease',
                    'Oven after cleaning by All Cleanz, with a clear glass door and clean shelves', base=OVEN)
        + '</div>', mint=False)
    + work_section('gutter-title', 'Gutters, soffits &amp; fascias',
        'Gutter cleaning with a high reach gutter vacuum, plus soffit, fascia and downpipe cleaning. <a href="gutter-cleaning">About our gutter cleaning</a>.',
        ba_pair('gutter-fascia', 640, 640, 'White fascia and downpipe streaked with black dirt and algae before cleaning',
                'The same fascia and downpipe after cleaning, bright white again')
        + '<ul class="work-gallery work-gallery--one"><li class="reveal"><img src="assets/img/services/gutter-vacuum-720.webp" '
          'srcset="assets/img/services/gutter-vacuum-400.webp 400w, assets/img/services/gutter-vacuum-720.webp 720w, assets/img/services/gutter-vacuum.webp 1040w" '
          'sizes="(max-width: 760px) 92vw, 760px" alt="All Cleanz high reach gutter vacuum pole cleaning the gutter of a brick house" '
          'width="720" height="540" loading="lazy"></li></ul>', mint=True)
    + work_section('carpet-title', 'Carpets',
        'Texatherm<sup>&reg;</sup> carpet cleaning, with textiles dry in 30 minutes, guaranteed. <a href="carpet-upholstery-cleaning">About our carpet cleaning</a>.',
        gallery([('carpet-rotary', 'Carpet cleaning machine at work in an empty room, with the cleaned carpet visibly lighter'),
                 ('carpet-doormat', 'Carpet by a front door, half cleaned, showing the dirty and clean sections side by side'),
                 ('carpet-lines', 'Freshly cleaned light carpet showing clean lines beside an uncleaned strip'),
                 ('carpet-machine', 'All Cleanz carpet cleaning machine being set up')]), mint=False)
    + work_section('stairs-title', 'Stairs',
        'An outdoor staircase with grit stair treads, before and after.',
        ba_pair('stairs', 640, 800, 'Outdoor staircase with blue railings and stained grit stair treads before cleaning',
                'The same staircase after cleaning, with clean, even stair treads'), mint=True)
    + f'''
    <section class="section areas-more" aria-label="More on social media">
      <div class="container"><p class="services__more reveal">See more of our latest jobs on <a href="https://www.facebook.com/AllcleanzNW" target="_blank" rel="noopener">Facebook</a> and <a href="https://www.instagram.com/allcleanz/" target="_blank" rel="noopener">Instagram</a>.</p></div>
    </section>
'''
    + cta_band('Want results like these?', "Hi All Cleanz, I'd like a quote please. I'm looking for: "))
write_page('our-work',
    'Our Work | Before &amp; After Photos | All Cleanz',
    'Before and after photos from real All Cleanz jobs across Merseyside and the North West: driveways, patios, ovens, gutters, carpets and more.',
    'CollectionPage', 'Our work', 'Our Work',
    page_hero('Our Work', ('Our', 'Work'), 'Real before &amp; after photos',
        'Every photo on this page is from a real All Cleanz job. From driveways and patios to ovens, gutters and carpets, here&rsquo;s the difference a professional clean makes.',
        ('work/drive-front-wide', 1040, 780, ['-400 400w', '-720 720w', ' 1040w'], 'Clean red herringbone block paving driveway in front of a house after jet washing'),
        "Hi All Cleanz, I'd like a quote please. I'm looking for: ",
        f'<a href="#drive-title" class="hero__textlink">See the photos {ICON % "arrow"}</a>'),
    work_body)

# ---------- 8. Leave a review (utility page, kept out of search) ----------
REVIEW_URL = 'https://search.google.com/local/writereview?placeid=ChIJE3yGEImFwWURhPb_ciz941g'
review_body = f'''
    <section class="section legal" aria-labelledby="review-title">
      <div class="container">
        <div class="review-card reveal">
          <h2 id="review-title" class="section-title">Thank you for choosing All Cleanz</h2>
          <p class="lead">Happy with your clean? A quick Google review really helps other people find us, and it only takes a minute.</p>
          <div class="page-cta__btns review-card__btns">
            <a href="{REVIEW_URL}" target="_blank" rel="noopener" class="btn btn--primary btn--lg">Leave a Google review {ICON % 'arrow'}</a>
            <a href="https://share.google/Gg61WBgD1EcMRRVPn" target="_blank" rel="noopener" class="btn btn--outline btn--lg">Read our reviews</a>
          </div>
          <figure class="review-card__qr">
            <img src="assets/img/review-qr.svg" alt="QR code that opens the All Cleanz Google review form" width="280" height="280">
            <figcaption>Or scan with your phone camera</figcaption>
          </figure>
          <p class="review-card__note">Not happy with something? Please tell us first on <a href="tel:+447721938429">07721 938429</a> so we can put it right.</p>
        </div>
      </div>
    </section>
'''
review_hero = legal_hero.replace('Privacy <em>Policy</em>', 'Leave Us a <em>Review</em>').replace(
    '<span class="hero__title-sm">Last updated 13 November 2026</span>', '<span class="hero__title-sm">Rated 4.9 out of 5 on Google</span>').replace(
    '<li><span aria-current="page">Privacy Policy</span></li>', '<li><span aria-current="page">Leave a Review</span></li>')
write_page('review',
    'Leave Us a Review | All Cleanz',
    'Happy with your All Cleanz clean? Leave us a quick Google review. It really helps other people across Merseyside and the North West find us.',
    'WebPage', 'Leave us a review', 'Leave a Review', review_hero, review_body, robots='noindex, follow')

# ---------- 9. FAQs ----------
# Every answer comes from the business's own published wording (old website, Google Business Profile).
# Not answered until the client confirms: prices, opening hours, insurance, DBS checks, payment methods.
FAQ_GROUPS = [
  ('About All Cleanz', [
    ('Where are you based and what areas do you cover?',
     'All Cleanz is based in Prescot, Merseyside, and provides domestic and commercial cleaning throughout Merseyside and the North West, '
     'including ' + ', '.join(f'<a href="{l["slug"]}">{l["town"]}</a>' for l in LOCATIONS[:-1]) + f' and <a href="{LOCATIONS[-1]["slug"]}">{LOCATIONS[-1]["town"]}</a>. '
     'See <a href="areas-we-cover">all the areas we cover</a>.'),
    ('Do you clean homes or businesses?',
     'Both. We offer a wide range of cleaning services for homes, offices and commercial properties, from a routine domestic clean to office cleaning contracts and builders cleans.'),
    ('What cleaning services do you offer?',
     'We offer ' + ', '.join(f'<a href="{x["slug"]}">{strip_tags(x["name"]).lower()}</a>' for x in sorted(PAGES, key=lambda x: ORDER.index(x['slug']))[:-1])
     + f' and <a href="bbq-cleaning">BBQ cleaning</a>. See <a href="services">all our services</a>.'),
    ('Can I book a regular clean or just a one off?',
     'Either. We provide a bespoke service to suit every need and budget, from regular daily, weekly or monthly cleans to a one off clean.'),
    ('How do you make sure the cleaning is done properly?',
     'To ensure the highest levels of customer satisfaction we use quality control programmes, including on-site inspections and customer surveys. '
     'For commercial contracts we also carry out frequent site supervision and quality checks.'),
    ('What do your customers say about you?',
     'We&rsquo;re rated 4.9 out of 5 on Google. You can <a href="https://share.google/Gg61WBgD1EcMRRVPn" target="_blank" rel="noopener">read our Google reviews</a> or see some of them on our <a href="about">About page</a>.'),
    ('How do I get a quote?', QUOTE_A),
  ]),
  ('Home cleaning', [
    ('What&rsquo;s included in an end of tenancy clean?',
     'We use a comprehensive end of tenancy checklist approved by agencies. The clean takes place once all your belongings have been removed and covers every room, '
     'including the kitchen, bathroom, bedrooms, living room, hallway and stairs. See the <a href="end-of-tenancy-cleaning">full end of tenancy checklist</a>.'),
    ('Do I need to move my belongings for a deep clean?',
     'No. Deep cleans are done with all your belongings in place, while still reaching those neglected areas. A deep clean is ideal before selling your property, after moving in, or before a new baby arrives. '
     'See <a href="deep-cleaning">deep cleaning</a>.'),
    ('What does a regular domestic clean include?',
     'A daily, weekly or monthly clean tailored to your needs, room by room: from dusting and wiping surfaces, vacuuming and mopping, to cleaning the bathroom, '
     'scrubbing the hob and removing rubbish. See exactly <a href="domestic-cleaning">what&rsquo;s included in each room</a>.'),
    ('Can you clean before or after a party?',
     'Yes. Our pre and post party cleaning is tailormade to suit your needs and includes weekend party cleaning too. See <a href="pre-post-party-cleaning">party cleaning</a>.'),
  ]),
  ('Carpets &amp; upholstery', [
    ('How long do carpets take to dry?',
     'Using the advanced, environmentally friendly Texatherm<sup>&reg;</sup> cleaning machine and process, carpets and upholstery dry in just 30 minutes, guaranteed.'),
    ('What is Texatherm<sup>&reg;</sup>?',
     'Texatherm<sup>&reg;</sup> is a patented cleaning process for carpets, upholstery and hard floors. Our Texatherm<sup>&reg;</sup> trained technicians can switch between several cleaning methods '
     'from just one machine, including hot water extraction and low moisture cleaning, depending on what each carpet needs. '
     'See <a href="carpet-upholstery-cleaning">carpet and upholstery cleaning</a>.'),
    ('Can you clean office carpet tiles?',
     'Yes. Office carpet tiles have watertight backings, so we use the Texatherm<sup>&reg;</sup> low moisture process, which gives superior results on commercial carpet tiles, '
     'cuts cleaning time by up to 60% and causes less disruption because it&rsquo;s quieter.'),
  ]),
  ('Ovens, fridges &amp; BBQs', [
    ('Can I use my oven straight after it&rsquo;s cleaned?',
     'Yes. Our cleaning products and techniques leave your oven spotlessly clean with no damage and minimal chemical use, and it&rsquo;s safe to use straight after cleaning. '
     'We disassemble the oven and deep clean the parts. See <a href="oven-cleaning">oven cleaning</a>.'),
    ('What do you use to clean BBQs?',
     'We use 100% non toxic, non caustic cleaning products to remove all grease, fat and carbon. We clean all types of gas and charcoal BBQs, and your BBQ is ready to use in 2 hours. '
     'See <a href="bbq-cleaning">BBQ cleaning</a>.'),
    ('Why should I have my fridge cleaned?',
     'If a fridge isn&rsquo;t cleaned regularly it can become a breeding ground for bacteria that survive at low temperatures, causing smells and making food unsafe to eat. '
     'See <a href="fridge-cleaning">fridge cleaning</a>.'),
  ]),
  ('Outside &amp; other services', [
    ('What can you jet wash?',
     'Driveways, patios, paving, stone walls, decking, fencing and some flat roofing systems. See <a href="jet-washing">jet washing</a>, with before and after photos.'),
    ('What does gutter cleaning include?',
     'Residential and commercial gutter cleaning, unblocking drainpipes, minor gutter repairs, soffit and fascia cleaning and conservatory roof cleaning. See <a href="gutter-cleaning">gutter cleaning</a>.'),
    ('Do you clean the inside of windows?',
     'Yes. Most window cleaners don&rsquo;t clean interior windows, but we provide both interior and exterior window cleaning for homes, offices, shops and other commercial spaces. '
     'See <a href="window-cleaning">window cleaning</a>.'),
    ('Do I need to bring my car to you for valeting?',
     'No. Our car valeting is provided as a home service, so there&rsquo;s no need to wait in long queues. See <a href="car-valeting">car valeting</a>.'),
    ('Do you clean after building work?',
     'Yes. We provide after build cleaning for builders and home owners, including newly built buildings, post renovation cleaning and cleaning after repairs. '
     'We&rsquo;ll discuss your needs and create a cleaning schedule that suits you. See <a href="after-build-cleaning">after build cleaning</a>.'),
  ]),
  ('Working for All Cleanz', [
    ('Are you hiring?',
     'Our cleaning team works flexible hours throughout the week on domestic and commercial jobs. You can apply as a domestic cleaner, cleaning supervisor or car valeter on our '
     '<a href="join-the-team">Join the Team</a> page.'),
  ]),
]
ALL_FAQS = [qa for _, items in FAQ_GROUPS for qa in items]
faq_url = SITE + 'faq'
faq_body = ''.join(
    f'''
    <section class="section{' section--mint' if i % 2 == 0 else ''}" aria-labelledby="faq-{i}">
      <div class="container">
        <div class="section-head reveal"><h2 id="faq-{i}" class="section-title section-title--sm">{group}</h2></div>
        {faq(items)}
      </div>
    </section>''' for i, (group, items) in enumerate(FAQ_GROUPS)) + cta_band('Got a question we haven&rsquo;t answered?', "Hi All Cleanz, I have a question: ")
faq_hero = legal_hero.replace('Privacy <em>Policy</em>', 'Frequently Asked <em>Questions</em>').replace(
    '<span class="hero__title-sm">Last updated 13 November 2026</span>', '<span class="hero__title-sm">Cleaning questions, answered</span>').replace(
    '<li><span aria-current="page">Privacy Policy</span></li>', '<li><span aria-current="page">FAQs</span></li>')
write_page('faq',
    'Cleaning FAQs | All Cleanz | Prescot, Merseyside',
    'Answers to common questions about All Cleanz: areas covered, end of tenancy and deep cleans, carpet drying times, oven and BBQ cleaning, jet washing and more.',
    'FAQPage', 'Frequently asked questions', 'FAQs', faq_hero, faq_body,
    extra={'mainEntity': [
        {'@type': 'Question', 'name': strip_tags(q_), 'acceptedAnswer': {'@type': 'Answer', 'text': strip_tags(a_)}}
        for q_, a_ in ALL_FAQS]})

# Homepage: a short FAQ section, generated from the same answers
HOME_FAQ_QS = ['Where are you based and what areas do you cover?', 'Can I book a regular clean or just a one off?',
               'How long do carpets take to dry?', 'Do I need to move my belongings for a deep clean?', 'How do I get a quote?']
home_faq = [next(qa for qa in ALL_FAQS if qa[0] == q_) for q_ in HOME_FAQ_QS]
assert len(home_faq) == len(HOME_FAQ_QS)
block = f'''<!-- FAQ (generated by tools/build_pages.py) -->
    <section class="section section--mint" aria-labelledby="home-faq-title">
      <div class="container">
        <div class="section-head reveal"><h2 id="home-faq-title" class="section-title">Frequently asked questions</h2></div>
        {faq(home_faq)}
        <p class="services__more reveal"><a href="faq">See all our FAQs</a></p>
      </div>
    </section>

    '''
path = ROOT + '/index.html'
html = open(path).read()
if '<!-- FAQ (generated' in html:
    html = re.sub(r'<!-- FAQ \(generated.*?(?=<!-- AREAS -->)', block, html, count=1, flags=re.S)
else:
    html = html.replace('<!-- AREAS -->', block + '<!-- AREAS -->', 1)
open(path, 'w').write(html)
