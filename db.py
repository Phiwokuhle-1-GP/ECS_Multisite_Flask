import os
import sqlite3
from pathlib import Path
from flask import g
from sites import TEMPLATES, CATEGORY_CONTENT

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.environ.get('DATA_DIR', BASE_DIR / 'instance'))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / 'ecs_multisite_v3.db'

SCHEMA = '''
CREATE TABLE IF NOT EXISTS sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    slug TEXT UNIQUE NOT NULL,
    design_id TEXT NOT NULL,
    business_name TEXT NOT NULL,
    domain TEXT UNIQUE,
    status TEXT NOT NULL DEFAULT 'active',
    eyebrow TEXT,
    hero_title TEXT,
    hero_text TEXT,
    cta_text TEXT,
    primary_color TEXT,
    secondary_color TEXT,
    logo_url TEXT,
    hero_image_url TEXT,
    phone TEXT,
    whatsapp TEXT,
    email TEXT,
    location TEXT,
    seo_title TEXT,
    seo_description TEXT,
    primary_keyword TEXT,
    image_alt TEXT,
    og_title TEXT,
    og_description TEXT,
    og_image_url TEXT,
    robots_index INTEGER NOT NULL DEFAULT 1,
    business_type TEXT DEFAULT 'LocalBusiness',
    street_address TEXT,
    city TEXT,
    region TEXT,
    postal_code TEXT,
    country TEXT DEFAULT 'ZA',
    service_area TEXT,
    opening_hours TEXT,
    service_1 TEXT,
    service_2 TEXT,
    service_3 TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS enquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    site_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    message TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(site_id) REFERENCES sites(id) ON DELETE CASCADE
);
CREATE INDEX IF NOT EXISTS idx_sites_domain ON sites(domain);
CREATE INDEX IF NOT EXISTS idx_enquiries_site ON enquiries(site_id);

CREATE TABLE IF NOT EXISTS platform_settings (
    key TEXT PRIMARY KEY,
    value TEXT
);
'''

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute('PRAGMA foreign_keys=ON')
    return con

def get_db():
    if 'db' not in g:
        g.db = connect()
    return g.db

def close_db(_=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()

DEFAULT_PLATFORM_SETTINGS = {
    'brand_name': 'Executive Communication Services',
    'brand_short': 'ECS',
    'tagline': 'WEBSITES · DIGITAL SOLUTIONS · DATA & ANALYTICS',
    'hero_kicker': 'PROFESSIONAL WEBSITES FOR GROWING BUSINESSES',
    'hero_title': 'Get a Professional Website for',
    'price': 'R2,999',
    'price_note': 'Once-off payment — includes domain and 12 months hosting.',
    'hero_text': 'Modern, mobile-friendly websites built for small businesses that want to look professional and grow online.',
    'cta_text': 'GET MY WEBSITE — R2,999',
    'cta_url': '',
    'whatsapp': '',
    'phone': '',
    'email': 'info@executivecommunicationservices.co.za',
    'location': 'Johannesburg, South Africa',
    'website': 'executivecommunicationservices.co.za',
    'annual_fee': 'R799/year',
    'annual_text': 'Hosting · domain renewal · SSL · maintenance · monitoring',
    'primary_color': '#062b57',
    'secondary_color': '#1598f5',
    'accent_color': '#1598f5',
    'hero_image_url': '',
    'benefit_1_title': 'Professional 3-page website',
    'benefit_1_text': 'Home, Services and Contact',
    'benefit_2_title': 'Domain name included',
    'benefit_2_text': '.co.za domain',
    'benefit_3_title': '12 months hosting included',
    'benefit_3_text': 'Fast, secure and reliable',
    'benefit_4_title': 'Basic SEO included',
    'benefit_4_text': 'Get found on Google',
    'benefit_5_title': 'Mobile responsive',
    'benefit_5_text': 'Looks great on all devices',
    'benefit_6_title': 'Perfect for small businesses',
    'benefit_6_text': 'Get your business online today',
    'industries': 'Plumbers,Electricians,Tutors,Consultants,Beauty Salons,Barbers,Caterers,Transport,Cleaning,Contractors,Training Providers',
    'seo_title': 'Professional Small Business Websites | ECS',
    'seo_description': 'Professional 3-page websites for small businesses. Domain and 12 months hosting included. Johannesburg, South Africa.'
}

def seed_platform_settings(con):
    for key, value in DEFAULT_PLATFORM_SETTINGS.items():
        con.execute('INSERT OR IGNORE INTO platform_settings(key,value) VALUES (?,?)', (key, value))

SEO_COLUMNS = {
    'primary_keyword': "TEXT",
    'image_alt': "TEXT",
    'og_title': "TEXT",
    'og_description': "TEXT",
    'og_image_url': "TEXT",
    'robots_index': "INTEGER NOT NULL DEFAULT 1",
    'business_type': "TEXT DEFAULT 'LocalBusiness'",
    'street_address': "TEXT",
    'city': "TEXT",
    'region': "TEXT",
    'postal_code': "TEXT",
    'country': "TEXT DEFAULT 'ZA'",
    'service_area': "TEXT",
    'opening_hours': "TEXT",
}

def migrate_schema(con):
    existing = {r[1] for r in con.execute('PRAGMA table_info(sites)').fetchall()}
    for name, ddl in SEO_COLUMNS.items():
        if name not in existing:
            con.execute(f'ALTER TABLE sites ADD COLUMN {name} {ddl}')

def init_db():
    con = connect()
    con.executescript(SCHEMA)
    migrate_schema(con)
    count = con.execute('SELECT COUNT(*) FROM sites').fetchone()[0]
    if count == 0:
        seed_sites(con)
    seed_platform_settings(con)
    con.commit()
    con.close()

def seed_sites(con):
    for idx, t in enumerate(TEMPLATES, 1):
        content = CATEGORY_CONTENT[t['category']]
        slug = t['id'].lower()
        domain = f"{t['id'].lower().replace('-', '')}.example.co.za"
        con.execute('''
            INSERT INTO sites (
                slug, design_id, business_name, domain, status, eyebrow,
                hero_title, hero_text, cta_text, primary_color, secondary_color,
                phone, whatsapp, email, location, seo_title, seo_description,
                service_1, service_2, service_3
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        ''', (
            slug, t['id'], f"{t['name']} Demo", domain, 'active', content['eyebrow'],
            content['hero'], t['desc'], content['cta'], t['primary'], t['secondary'],
            f"071 555 {1000+idx:04d}", f"2771555{1000+idx:04d}", f"hello@{domain}",
            'Johannesburg, South Africa', f"{t['name']} | ECS Website Demo", t['desc'],
            *content['services']
        ))
