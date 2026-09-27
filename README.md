# ECS Multisite Flask V2 — 20 real catalogue mockups

This version connects the **actual 20 design records from `website_mockup_catalogue_v1`** to one Flask multisite engine.

## What changed

- Original catalogue metadata and gradients preserved.
- 20 live sites, not placeholder industries.
- Every site has Home, Services and Contact pages.
- Original catalogue remains available at `/catalogue`.
- Clicking a catalogue design opens its live site.
- Domain routing is ready for one Render service with multiple custom domains.
- `SML-01` to `SML-04` aliases are supported, but the uploaded source file uses `SMB-01` to `SMB-04` as its actual IDs.

## Run locally (Windows PowerShell)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python app.py
```

Open:

- `http://127.0.0.1:5000` — 20-site launcher
- `http://127.0.0.1:5000/catalogue` — original catalogue, now connected
- `http://127.0.0.1:5000/demo/COR-01` — Executive Navy
- `http://127.0.0.1:5000/demo/ECM-01` — Single Product
- `http://127.0.0.1:5000/demo/TRN-02` — City Shuttle
- `http://127.0.0.1:5000/health` — returns site count

Every demo has:

```text
/demo/COR-01
/demo/COR-01/services
/demo/COR-01/contact
```

## Render/domain model

Each site currently has a test domain such as:

```text
cor01.example.co.za
cor02.example.co.za
...
trn04.example.co.za
```

Change `domain` values in `sites.py` to real client domains and add those domains to the same Render web service. The incoming host selects the correct site.

On a real client domain:

```text
https://client-domain.co.za/
https://client-domain.co.za/services
https://client-domain.co.za/contact
```

## Images

The uploaded catalogue source ZIP does **not contain image files**; its previews are gradient/browser-style mockups. V2 therefore preserves that real source rather than inventing image assets. Client images can be added next through shared object storage or static assets.
