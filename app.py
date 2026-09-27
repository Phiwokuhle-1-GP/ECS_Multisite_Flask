from flask import Flask, render_template, request, abort, redirect, url_for
from sites import SITES, DESIGNS, DOMAIN_MAP, ALIASES

app = Flask(__name__)


def normalize_design_id(design_id):
    design_id = design_id.upper()
    return ALIASES.get(design_id, design_id)


def get_site(design_id=None):
    if design_id:
        return SITES.get(normalize_design_id(design_id))
    host = request.host.split(':')[0].lower()
    if host.startswith('www.'):
        host = host[4:]
    site_id = DOMAIN_MAP.get(host)
    return SITES.get(site_id) if site_id else None


def page_url(site, page='home'):
    # On a real custom domain, keep normal /, /services and /contact URLs.
    host = request.host.split(':')[0].lower()
    if host.startswith('www.'):
        host = host[4:]
    if host in DOMAIN_MAP:
        if page == 'home':
            return '/'
        return f'/{page}'
    # Local/Render demo launcher keeps site id in the URL.
    if page == 'home':
        return url_for('demo_home', design_id=site['id'])
    return url_for(f'demo_{page}', design_id=site['id'])


@app.context_processor
def inject_helpers():
    return {'page_url': page_url}


@app.route('/')
def root():
    site = get_site()
    if site:
        return render_template('site_home.html', site=site)
    return render_template('launcher.html', sites=SITES)


@app.route('/catalogue')
def catalogue():
    categories = sorted({d['category'] for d in DESIGNS})
    styles = sorted({d['style'] for d in DESIGNS})
    return render_template('catalogue.html', designs=DESIGNS, categories=categories, styles=styles)


@app.route('/preview/<design_id>')
def old_preview_redirect(design_id):
    site = get_site(design_id)
    if not site:
        abort(404)
    return redirect(url_for('demo_home', design_id=site['id']))


@app.route('/services')
def domain_services():
    site = get_site()
    if not site:
        abort(404)
    return render_template('site_services.html', site=site)


@app.route('/contact')
def domain_contact():
    site = get_site()
    if not site:
        abort(404)
    return render_template('site_contact.html', site=site)


@app.route('/demo/<design_id>')
def demo_home(design_id):
    site = get_site(design_id)
    if not site:
        abort(404)
    return render_template('site_home.html', site=site)


@app.route('/demo/<design_id>/services')
def demo_services(design_id):
    site = get_site(design_id)
    if not site:
        abort(404)
    return render_template('site_services.html', site=site)


@app.route('/demo/<design_id>/contact')
def demo_contact(design_id):
    site = get_site(design_id)
    if not site:
        abort(404)
    return render_template('site_contact.html', site=site)


@app.route('/health')
def health():
    return {
        'status': 'ok',
        'sites': len(SITES),
        'domains': len(DOMAIN_MAP),
        'catalogue_connected': True,
    }


if __name__ == '__main__':
    app.run(debug=True)
