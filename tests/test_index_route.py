"""TestClient tests for GET / and the /static mount — the dashboard
itself.

The dashboard is the product's front door: the root route must serve
the HTML shell (not a JSON 404), the bundled assets must be reachable
under /static, and a missing asset must be a plain 404 rather than a
traceback or a redirect.
"""
from fastapi.testclient import TestClient

from localforge.server import app

client = TestClient(app, raise_server_exceptions=False)


def test_root_serves_dashboard_html():
    r = client.get("/")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "LocalForge" in r.text


def test_static_index_html_is_served():
    r = client.get("/static/index.html")
    assert r.status_code == 200
    assert "text/html" in r.headers["content-type"]
    assert "LocalForge" in r.text


def test_missing_static_asset_is_404():
    r = client.get("/static/does-not-exist.js")
    assert r.status_code == 404
