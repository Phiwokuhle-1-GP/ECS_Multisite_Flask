# Exact design metadata carried over from website_mockup_catalogue_v1.
# Each catalogue design is now a real 3-page site configuration.

DESIGNS = [
    dict(id='COR-01', name='Executive Navy', category='Corporate', style='Executive', palette='Navy / Gold', layout='Multi-page', desc='Premium consulting and professional-services layout.', gradient='linear-gradient(135deg,#071a34,#174a7e)'),
    dict(id='COR-02', name='Clean Advisory', category='Corporate', style='Minimal', palette='White / Blue', layout='Multi-page', desc='Bright advisory site with strong service hierarchy.', gradient='linear-gradient(135deg,#eef4fb,#2367a5)'),
    dict(id='COR-03', name='Boardroom', category='Corporate', style='Luxury', palette='Charcoal / Bronze', layout='Multi-page', desc='High-end executive and legal-services presentation.', gradient='linear-gradient(135deg,#151719,#9b7548)'),
    dict(id='COR-04', name='Strategy Grid', category='Corporate', style='Modern', palette='Slate / Cyan', layout='One-page', desc='Modern strategy company with modular case-study blocks.', gradient='linear-gradient(135deg,#26333e,#1aa6b7)'),
    dict(id='SMB-01', name='Local Pro', category='Small Business', style='Friendly', palette='Blue / White', layout='One-page', desc='Conversion-first local service business homepage.', gradient='linear-gradient(135deg,#1976d2,#e7f2ff)'),
    dict(id='SMB-02', name='Trade Strong', category='Small Business', style='Bold', palette='Black / Orange', layout='Multi-page', desc='Trades, construction and repair services with quote CTA.', gradient='linear-gradient(135deg,#191919,#ef7d22)'),
    dict(id='SMB-03', name='Neighbourhood', category='Small Business', style='Warm', palette='Green / Cream', layout='One-page', desc='Approachable local business style with reviews and map.', gradient='linear-gradient(135deg,#315c49,#f3ead7)'),
    dict(id='SMB-04', name='Service Flow', category='Small Business', style='Modern', palette='Indigo / Mint', layout='Multi-page', desc='Structured services, process, FAQ and lead generation.', gradient='linear-gradient(135deg,#353b73,#7bdcb5)'),
    dict(id='EDU-01', name='Course Launch', category='Education', style='Energetic', palette='Purple / Lime', layout='One-page', desc='Focused course landing page built for paid campaigns.', gradient='linear-gradient(135deg,#5d2e8c,#c5e86c)'),
    dict(id='EDU-02', name='Academy', category='Education', style='Professional', palette='Navy / Sky', layout='Multi-page', desc='Training academy with course catalogue and enquiries.', gradient='linear-gradient(135deg,#0d2745,#5eb6e8)'),
    dict(id='EDU-03', name='Young Creator', category='Education', style='Playful', palette='Blue / Yellow', layout='Multi-page', desc='Coding, editing and creative learning for young students.', gradient='linear-gradient(135deg,#1d6fd8,#ffd85a)'),
    dict(id='EDU-04', name='Tutor Focus', category='Education', style='Minimal', palette='Teal / White', layout='One-page', desc='Simple tutor profile with outcomes, subjects and booking.', gradient='linear-gradient(135deg,#168b8b,#eefafa)'),
    dict(id='ECM-01', name='Single Product', category='E-commerce', style='Conversion', palette='Blush / Plum', layout='One-page', desc='One-product offer with benefits, proof and fast checkout.', gradient='linear-gradient(135deg,#f5dce5,#6f3158)'),
    dict(id='ECM-02', name='Boutique', category='E-commerce', style='Luxury', palette='Cream / Black', layout='Multi-page', desc='Editorial boutique store with premium product storytelling.', gradient='linear-gradient(135deg,#f3ecdf,#24211f)'),
    dict(id='ECM-03', name='Fresh Store', category='E-commerce', style='Modern', palette='Aqua / Navy', layout='Multi-page', desc='Clean catalogue storefront with categories and promotions.', gradient='linear-gradient(135deg,#7bded8,#15324a)'),
    dict(id='ECM-04', name='Bundle Shop', category='E-commerce', style='Friendly', palette='Rose / Peach', layout='Multi-page', desc='Gift and bundle-led shopping with strong offer cards.', gradient='linear-gradient(135deg,#dc6f88,#ffc49b)'),
    dict(id='TRN-01', name='Executive Ride', category='Transport', style='Luxury', palette='Black / Gold', layout='Multi-page', desc='Premium chauffeur and airport transfer experience.', gradient='linear-gradient(135deg,#111,#b18b43)'),
    dict(id='TRN-02', name='City Shuttle', category='Transport', style='Modern', palette='Navy / Green', layout='One-page', desc='Fast quote-led shuttle service for local routes.', gradient='linear-gradient(135deg,#0e3154,#35b779)'),
    dict(id='TRN-03', name='Tour Explorer', category='Transport', style='Visual', palette='Ocean / Sand', layout='Multi-page', desc='Tour and transfer company with destination-led imagery.', gradient='linear-gradient(135deg,#247b91,#e7c99b)'),
    dict(id='TRN-04', name='Corporate Fleet', category='Transport', style='Professional', palette='Slate / Blue', layout='Multi-page', desc='Corporate transport with fleet, accounts and booking.', gradient='linear-gradient(135deg,#33424f,#3987c9)'),
]

CATEGORY_CONTENT = {
    'Corporate': {
        'eyebrow': 'PROFESSIONAL SERVICES',
        'hero': 'Clear thinking. Strong execution.',
        'services': ['Strategy & Advisory', 'Business Solutions', 'Client Support'],
        'cta': 'Book a consultation',
    },
    'Small Business': {
        'eyebrow': 'LOCAL BUSINESS',
        'hero': 'Reliable local service, made simple.',
        'services': ['Core Service', 'Repairs & Support', 'Quotes & Call-outs'],
        'cta': 'Get a free quote',
    },
    'Education': {
        'eyebrow': 'LEARN & GROW',
        'hero': 'Practical learning for real progress.',
        'services': ['Courses', 'Skills Training', 'Learner Support'],
        'cta': 'Enquire about courses',
    },
    'E-commerce': {
        'eyebrow': 'SHOP THE COLLECTION',
        'hero': 'Products worth discovering.',
        'services': ['Featured Products', 'Bundles & Offers', 'Fast Ordering'],
        'cta': 'Shop now',
    },
    'Transport': {
        'eyebrow': 'MOVE WITH CONFIDENCE',
        'hero': 'Dependable journeys, professionally delivered.',
        'services': ['Bookings', 'Transfers', 'Business Travel'],
        'cta': 'Request a booking',
    },
}

SITES = {}
for i, d in enumerate(DESIGNS, start=1):
    content = CATEGORY_CONTENT[d['category']]
    key = d['id'].lower()
    domain = f"{d['id'].lower().replace('-', '')}.example.co.za"
    SITES[d['id']] = {
        **d,
        'key': key,
        'domain': domain,
        'eyebrow': content['eyebrow'],
        'hero': content['hero'],
        'services': content['services'],
        'cta': content['cta'],
        'phone': f"071 555 {1000+i:04d}",
        'whatsapp': f"2771555{1000+i:04d}",
        'email': f"hello@{domain}",
        'location': 'Johannesburg, South Africa',
    }

# Alias the SML references from the visual catalogue discussion to the actual
# uploaded source IDs, which use SMB-01 ... SMB-04.
ALIASES = {f'SML-0{i}': f'SMB-0{i}' for i in range(1, 5)}

DOMAIN_MAP = {site['domain']: design_id for design_id, site in SITES.items()}
