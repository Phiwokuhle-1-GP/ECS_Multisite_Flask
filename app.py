import os
import re
from functools import wraps
from secrets import token_urlsafe
from flask import (
    Flask, render_template, request, abort, redirect, url_for,
    session, flash, jsonify, Response
)
from werkzeug.security import check_password_hash
import json
from sites import TEMPLATES, TEMPLATE_MAP, ALIASES
from db import get_db, close_db, init_db, DB_PATH, DEFAULT_PLATFORM_SETTINGS

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-only-change-me')
app.teardown_appcontext(close_db)

# For local testing only. On Render set ADMIN_USERNAME + ADMIN_PASSWORD.
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'change-me-now')
ADMIN_PASSWORD_HASH = os.environ.get('ADMIN_PASSWORD_HASH')

with app.app_context():
    init_db()


def normalize_design_id(design_id):
    design_id = (design_id or '').upper()
    return ALIASES.get(design_id, design_id)


def normalize_host(host):
    host = (host or '').split(':')[0].lower().strip()
    if host.startswith('www.'):
        host = host[4:]
    return host


def row_to_site(row):
    if not row:
        return None
    s = dict(row)
    s['db_id'] = s.get('id')
    design_id = normalize_design_id(s['design_id'])
    template = TEMPLATE_MAP.get(design_id, TEMPLATES[0])
    s['design_id'] = design_id
    s['template'] = template
    s['id_code'] = design_id
    s['id'] = design_id  # backwards compatibility with V2 templates
    s['name'] = s['business_name']
    s['desc'] = s['hero_text'] or template['desc']
    s['hero'] = s['hero_title']
    s['cta'] = s['cta_text']
    s['style'] = template['style']
    s['palette'] = template['palette']
    s['layout'] = template['layout']
    s['category'] = template['category']
    s['gradient'] = f"linear-gradient(135deg,{s['primary_color'] or template['primary']},{s['secondary_color'] or template['secondary']})"
    s['services'] = [x for x in [s.get('service_1'), s.get('service_2'), s.get('service_3')] if x]
    return s


def find_site_by_slug(slug):
    row = get_db().execute('SELECT * FROM sites WHERE slug=?', (slug.lower(),)).fetchone()
    return row_to_site(row)


def find_site_by_domain(domain):
    row = get_db().execute(
        "SELECT * FROM sites WHERE lower(domain)=? AND status='active'", (normalize_host(domain),)
    ).fetchone()
    return row_to_site(row)


def get_site(slug=None):
    if slug:
        return find_site_by_slug(slug)
    return find_site_by_domain(request.host)


def is_render_host():
    return normalize_host(request.host).endswith('.onrender.com')


def page_url(site, page='home'):
    current_host = normalize_host(request.host)
    domain = normalize_host(site.get('domain'))
    if domain and current_host == domain:
        return '/' if page == 'home' else f'/{page}'
    if page == 'home':
        return url_for('preview_home', slug=site['slug'])
    return url_for(f'preview_{page}', slug=site['slug'])


@app.context_processor
def inject_helpers():
    return {'page_url': page_url}


def get_platform_settings():
    rows = get_db().execute('SELECT key,value FROM platform_settings').fetchall()
    settings = dict(DEFAULT_PLATFORM_SETTINGS)
    settings.update({r['key']: (r['value'] or '') for r in rows})
    settings['industries_list'] = [x.strip() for x in settings.get('industries','').split(',') if x.strip()]
    return settings


def platform_settings_payload(form):
    payload = {}
    for key, default in DEFAULT_PLATFORM_SETTINGS.items():
        payload[key] = (form.get(key) if form.get(key) is not None else default).strip()
    payload['whatsapp'] = re.sub(r'\D', '', payload.get('whatsapp',''))
    return payload


def verify_admin_password(password):
    if ADMIN_PASSWORD_HASH:
        return check_password_hash(ADMIN_PASSWORD_HASH, password)
    return password == ADMIN_PASSWORD


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect(url_for('admin_login', next=request.path))
        return view(*args, **kwargs)
    return wrapped


def csrf_token():
    if 'csrf_token' not in session:
        session['csrf_token'] = token_urlsafe(24)
    return session['csrf_token']


@app.context_processor
def inject_csrf():
    return {'csrf_token': csrf_token}


def require_csrf():
    if request.form.get('_csrf') != session.get('csrf_token'):
        abort(400, 'Invalid CSRF token')


def clean_slug(value):
    value = re.sub(r'[^a-z0-9-]+', '-', (value or '').strip().lower())
    return re.sub(r'-+', '-', value).strip('-')


def clean_domain(value):
    value = normalize_host((value or '').replace('https://', '').replace('http://', '').split('/')[0])
    return value or None


def site_form_payload(form):
    design_id = normalize_design_id(form.get('design_id'))
    template = TEMPLATE_MAP.get(design_id, TEMPLATES[0])
    return {
        'slug': clean_slug(form.get('slug')),
        'design_id': design_id,
        'business_name': (form.get('business_name') or '').strip(),
        'domain': clean_domain(form.get('domain')),
        'status': 'active' if form.get('status') == 'active' else 'archived',
        'eyebrow': (form.get('eyebrow') or '').strip(),
        'hero_title': (form.get('hero_title') or '').strip(),
        'hero_text': (form.get('hero_text') or '').strip(),
        'cta_text': (form.get('cta_text') or '').strip(),
        'primary_color': (form.get('primary_color') or template['primary']).strip(),
        'secondary_color': (form.get('secondary_color') or template['secondary']).strip(),
        'logo_url': (form.get('logo_url') or '').strip(),
        'hero_image_url': (form.get('hero_image_url') or '').strip(),
        'phone': (form.get('phone') or '').strip(),
        'whatsapp': re.sub(r'\D', '', form.get('whatsapp') or ''),
        'email': (form.get('email') or '').strip(),
        'location': (form.get('location') or '').strip(),
        'seo_title': (form.get('seo_title') or '').strip(),
        'seo_description': (form.get('seo_description') or '').strip(),
        'primary_keyword': (form.get('primary_keyword') or '').strip(),
        'image_alt': (form.get('image_alt') or '').strip(),
        'og_title': (form.get('og_title') or '').strip(),
        'og_description': (form.get('og_description') or '').strip(),
        'og_image_url': (form.get('og_image_url') or '').strip(),
        'robots_index': 1 if form.get('robots_index') == '1' else 0,
        'business_type': (form.get('business_type') or 'LocalBusiness').strip(),
        'street_address': (form.get('street_address') or '').strip(),
        'city': (form.get('city') or '').strip(),
        'region': (form.get('region') or '').strip(),
        'postal_code': (form.get('postal_code') or '').strip(),
        'country': (form.get('country') or 'ZA').strip().upper(),
        'service_area': (form.get('service_area') or '').strip(),
        'opening_hours': (form.get('opening_hours') or '').strip(),
        'service_1': (form.get('service_1') or '').strip(),
        'service_2': (form.get('service_2') or '').strip(),
        'service_3': (form.get('service_3') or '').strip(),
    }


def canonical_url(site, page='home'):
    domain = normalize_host(site.get('domain'))
    if not domain or domain.endswith('.example.co.za'):
        return request.url_root.rstrip('/') + ('' if page == 'home' else '/' + page)
    return f"https://{domain}" + ('' if page == 'home' else '/' + page)


def local_business_schema(site):
    domain = normalize_host(site.get('domain'))
    url = f"https://{domain}" if domain and not domain.endswith('.example.co.za') else request.url_root.rstrip('/')
    address = {"@type": "PostalAddress"}
    if site.get('street_address'): address['streetAddress'] = site['street_address']
    if site.get('city'): address['addressLocality'] = site['city']
    if site.get('region'): address['addressRegion'] = site['region']
    if site.get('postal_code'): address['postalCode'] = site['postal_code']
    if site.get('country'): address['addressCountry'] = site['country']
    data = {
        "@context": "https://schema.org",
        "@type": site.get('business_type') or "LocalBusiness",
        "name": site.get('business_name'),
        "url": url,
        "description": site.get('seo_description') or site.get('hero_text'),
    }
    if site.get('phone'): data['telephone'] = site['phone']
    if site.get('email'): data['email'] = site['email']
    if site.get('logo_url'): data['logo'] = site['logo_url']
    if site.get('hero_image_url'): data['image'] = site['hero_image_url']
    if len(address) > 1: data['address'] = address
    if site.get('service_area'): data['areaServed'] = site['service_area']
    if site.get('opening_hours'): data['openingHours'] = [x.strip() for x in site['opening_hours'].split(',') if x.strip()]
    return json.dumps(data, ensure_ascii=False)


def seo_health(site):
    checks = []
    title = (site.get('seo_title') or '').strip()
    desc = (site.get('seo_description') or '').strip()
    real_domain = bool(site.get('domain') and not site['domain'].endswith('.example.co.za'))
    checks.append(('SEO title', bool(title), 'Add a unique page title.'))
    checks.append(('Title length', 30 <= len(title) <= 65, f'{len(title)} characters; aim for 30–65.'))
    checks.append(('Meta description', bool(desc), 'Add a unique meta description.'))
    checks.append(('Description length', 90 <= len(desc) <= 165, f'{len(desc)} characters; aim for 90–165.'))
    checks.append(('Primary keyword', bool(site.get('primary_keyword')), 'Set the main service/location phrase.'))
    checks.append(('Unique H1', bool(site.get('hero_title')), 'Add a clear hero heading.'))
    checks.append(('Real domain', real_domain, 'Connect the client custom domain.'))
    checks.append(('Location', bool(site.get('location') or site.get('city')), 'Add the business location/service area.'))
    checks.append(('Contact details', bool(site.get('phone') or site.get('email')), 'Add phone or email.'))
    checks.append(('Image alt text', bool(site.get('image_alt')) if site.get('hero_image_url') else True, 'Add descriptive hero image alt text.'))
    checks.append(('Open Graph', bool(site.get('og_title') or title) and bool(site.get('og_description') or desc), 'Add social sharing title/description.'))
    checks.append(('Indexing enabled', bool(site.get('robots_index')), 'Enable indexing when the site is ready.'))
    passed = sum(1 for _, ok, _ in checks if ok)
    return {'score': round(passed / len(checks) * 100), 'passed': passed, 'total': len(checks), 'checks': checks}


@app.context_processor
def inject_seo_helpers():
    return {'canonical_url': canonical_url, 'local_business_schema': local_business_schema, 'seo_health': seo_health}


@app.after_request
def protect_internal_surfaces_from_indexing(response):
    internal_path = (
        request.path.startswith('/admin')
        or request.path.startswith('/preview/')
        or request.path.startswith('/demo/')
        or request.path in ('/catalogue', '/platform')
    )
    if is_render_host() or internal_path:
        response.headers['X-Robots-Tag'] = 'noindex, nofollow, noarchive'
    if internal_path:
        response.headers['Cache-Control'] = 'no-store'
    return response


# ---------- public website ----------
@app.route('/')
def root():
    site = get_site()
    if site:
        return render_template('site_home.html', site=site)
    if session.get('admin_logged_in'):
        return redirect(url_for('admin_dashboard'))
    return redirect(url_for('admin_login'))


@app.route('/platform')
@admin_required
def platform_launcher():
    rows = get_db().execute("SELECT * FROM sites WHERE status='active' ORDER BY id").fetchall()
    return render_template('launcher.html', sites=[row_to_site(r) for r in rows])


@app.route('/catalogue')
@admin_required
def catalogue():
    categories = sorted({d['category'] for d in TEMPLATES})
    styles = sorted({d['style'] for d in TEMPLATES})
    return render_template('catalogue.html', designs=TEMPLATES, categories=categories, styles=styles)


@app.route('/services')
def domain_services():
    site = get_site()
    if not site:
        abort(404)
    return render_template('site_services.html', site=site)


@app.route('/contact', methods=['GET', 'POST'])
def domain_contact():
    site = get_site()
    if not site:
        abort(404)
    if request.method == 'POST':
        return save_enquiry(site)
    return render_template('site_contact.html', site=site)


@app.route('/preview/<slug>')
@admin_required
def preview_home(slug):
    site = get_site(slug)
    if not site:
        abort(404)
    return render_template('site_home.html', site=site, preview=True)


@app.route('/preview/<slug>/services')
@admin_required
def preview_services(slug):
    site = get_site(slug)
    if not site:
        abort(404)
    return render_template('site_services.html', site=site, preview=True)


@app.route('/preview/<slug>/contact', methods=['GET', 'POST'])
@admin_required
def preview_contact(slug):
    site = get_site(slug)
    if not site:
        abort(404)
    if request.method == 'POST':
        return save_enquiry(site)
    return render_template('site_contact.html', site=site, preview=True)


# V2 links remain valid.
@app.route('/demo/<design_id>')
@admin_required
def old_demo_redirect(design_id):
    design_id = normalize_design_id(design_id)
    row = get_db().execute('SELECT slug FROM sites WHERE design_id=? ORDER BY id LIMIT 1', (design_id,)).fetchone()
    if not row:
        abort(404)
    return redirect(url_for('preview_home', slug=row['slug']))

@app.route('/demo/<design_id>/<page>')
@admin_required
def old_demo_page_redirect(design_id, page):
    if page not in ('services', 'contact'):
        abort(404)
    design_id = normalize_design_id(design_id)
    row = get_db().execute('SELECT slug FROM sites WHERE design_id=? ORDER BY id LIMIT 1', (design_id,)).fetchone()
    if not row:
        abort(404)
    return redirect(url_for(f'preview_{page}', slug=row['slug']))


def save_enquiry(site):
    name = (request.form.get('name') or '').strip()
    message = (request.form.get('message') or '').strip()
    if not name or not message:
        flash('Please enter your name and message.', 'error')
        return render_template('site_contact.html', site=site)
    db = get_db()
    db.execute(
        'INSERT INTO enquiries(site_id,name,phone,email,message) VALUES (?,?,?,?,?)',
        (site['db_id'], name,
         (request.form.get('phone') or '').strip(), (request.form.get('email') or '').strip(), message)
    )
    db.commit()
    flash('Thank you. Your enquiry has been received.', 'success')
    return redirect(page_url(site, 'contact'))


@app.route('/sitemap.xml')
def sitemap_xml():
    site = get_site()
    if site:
        base = f"https://{normalize_host(site['domain'])}" if site.get('domain') and not site['domain'].endswith('.example.co.za') else request.url_root.rstrip('/')
        urls = [base + '/', base + '/services', base + '/contact']
    else:
        urls = []
    body = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u in urls:
        body.append(f'<url><loc>{u}</loc></url>')
    body.append('</urlset>')
    return Response('\n'.join(body), mimetype='application/xml')


@app.route('/robots.txt')
def robots_txt():
    site = get_site()
    base = request.url_root.rstrip('/')
    if not site:
        text = 'User-agent: *\nDisallow: /\n'
    elif not site.get('robots_index'):
        text = 'User-agent: *\nDisallow: /\n'
    else:
        text = f'User-agent: *\nAllow: /\nSitemap: {base}/sitemap.xml\n'
    return Response(text, mimetype='text/plain')


# ---------- admin ----------
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        if request.form.get('username') == ADMIN_USERNAME and verify_admin_password(request.form.get('password') or ''):
            session.clear()
            session['admin_logged_in'] = True
            session['admin_username'] = ADMIN_USERNAME
            session['csrf_token'] = token_urlsafe(24)
            next_url = request.args.get('next') or url_for('admin_dashboard')
            if not next_url.startswith('/') or next_url.startswith('//'):
                next_url = url_for('admin_dashboard')
            return redirect(next_url)
        flash('Invalid username or password.', 'error')
    return render_template('admin/login.html')


@app.route('/admin/logout', methods=['POST'])
@admin_required
def admin_logout():
    require_csrf()
    session.clear()
    return redirect(url_for('admin_login'))


@app.route('/admin')
@admin_required
def admin_dashboard():
    db = get_db()
    rows = db.execute('SELECT * FROM sites ORDER BY updated_at DESC, id DESC').fetchall()
    sites = [row_to_site(r) for r in rows]
    for s, r in zip(sites, rows):
        s['db_id'] = r['id']
    stats = {
        'sites': len(sites),
        'active': sum(s['status'] == 'active' for s in sites),
        'domains': sum(bool(s['domain'] and not s['domain'].endswith('.example.co.za')) for s in sites),
        'enquiries': db.execute('SELECT COUNT(*) FROM enquiries').fetchone()[0],
        'new_enquiries': db.execute("SELECT COUNT(*) FROM enquiries WHERE status='new'").fetchone()[0],
    }
    return render_template('admin/dashboard.html', sites=sites, stats=stats)


@app.route('/admin/sites/new', methods=['GET', 'POST'])
@admin_required
def admin_site_new():
    if request.method == 'POST':
        require_csrf()
        payload = site_form_payload(request.form)
        if not payload['slug'] or not payload['business_name']:
            flash('Business name and slug are required.', 'error')
            return render_template('admin/site_form.html', site=payload, templates=TEMPLATES, mode='new', seo=None)
        cols = ','.join(payload.keys())
        marks = ','.join('?' for _ in payload)
        try:
            db = get_db()
            db.execute(f'INSERT INTO sites ({cols}) VALUES ({marks})', tuple(payload.values()))
            db.commit()
            flash('Website created.', 'success')
            return redirect(url_for('admin_dashboard'))
        except Exception as exc:
            flash(f'Could not create website: {exc}', 'error')
    selected_design = normalize_design_id(request.args.get('design_id'))
    site = {'design_id': selected_design} if selected_design in TEMPLATE_MAP else None
    return render_template('admin/site_form.html', site=site, templates=TEMPLATES, mode='new', seo=None)


@app.route('/admin/sites/<int:site_id>/edit', methods=['GET', 'POST'])
@admin_required
def admin_site_edit(site_id):
    db = get_db()
    row = db.execute('SELECT * FROM sites WHERE id=?', (site_id,)).fetchone()
    if not row:
        abort(404)
    if request.method == 'POST':
        require_csrf()
        payload = site_form_payload(request.form)
        assignments = ','.join(f'{k}=?' for k in payload)
        try:
            db.execute(f'UPDATE sites SET {assignments}, updated_at=CURRENT_TIMESTAMP WHERE id=?', (*payload.values(), site_id))
            db.commit()
            flash('Website updated.', 'success')
            return redirect(url_for('admin_site_edit', site_id=site_id))
        except Exception as exc:
            flash(f'Could not update website: {exc}', 'error')
    site = dict(row)
    return render_template('admin/site_form.html', site=site, templates=TEMPLATES, mode='edit', site_id=site_id, seo=seo_health(site))


@app.route('/admin/sites/<int:site_id>/archive', methods=['POST'])
@admin_required
def admin_site_archive(site_id):
    require_csrf()
    db = get_db()
    current = db.execute('SELECT status FROM sites WHERE id=?', (site_id,)).fetchone()
    if not current:
        abort(404)
    new_status = 'archived' if current['status'] == 'active' else 'active'
    db.execute('UPDATE sites SET status=?, updated_at=CURRENT_TIMESTAMP WHERE id=?', (new_status, site_id))
    db.commit()
    flash(f'Website marked {new_status}.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/homepage', methods=['GET', 'POST'])
@admin_required
def admin_homepage():
    if request.method == 'POST':
        require_csrf()
        payload = platform_settings_payload(request.form)
        db = get_db()
        for key, value in payload.items():
            db.execute('INSERT INTO platform_settings(key,value) VALUES (?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value', (key, value))
        db.commit()
        flash('ECS homepage updated.', 'success')
        return redirect(url_for('admin_homepage'))
    return render_template('admin/homepage.html', settings=get_platform_settings())


@app.route('/admin/enquiries')
@admin_required
def admin_enquiries():
    rows = get_db().execute('''
        SELECT e.*, s.business_name, s.slug FROM enquiries e
        JOIN sites s ON s.id=e.site_id
        ORDER BY e.created_at DESC
    ''').fetchall()
    return render_template('admin/enquiries.html', enquiries=rows)


@app.route('/admin/enquiries/<int:enquiry_id>/read', methods=['POST'])
@admin_required
def admin_enquiry_read(enquiry_id):
    require_csrf()
    db = get_db()
    db.execute("UPDATE enquiries SET status='read' WHERE id=?", (enquiry_id,))
    db.commit()
    return redirect(url_for('admin_enquiries'))


@app.route('/health')
def health():
    db = get_db()
    return jsonify({
        'status': 'ok',
        'version': '3.3',
        'sites': db.execute('SELECT COUNT(*) FROM sites').fetchone()[0],
        'active_sites': db.execute("SELECT COUNT(*) FROM sites WHERE status='active'").fetchone()[0],
        'templates': len(TEMPLATES),
        'database': str(DB_PATH),
        'admin_enabled': True,
    })


if __name__ == '__main__':
    app.run(debug=True)
