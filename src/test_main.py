import urllib
from fastapi.testclient import TestClient
from main import app
import requests


client = TestClient(app)


def test_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "OK"}

def test_feeds():
    response = client.get("/feeds")
    assert 'simplecto' in response.json()

def test_template_page():
    params = {
        "byline": "this is a byline",
        "text": "this is the text"
    }
    response = client.get("/page/90daydx", params=params)
    assert response.status_code == 200

def test_template_page_missing_byline():
    params = {
        "text": "this is the text"
    }
    response = client.get("/page/90daydx")
    assert response.status_code == 422

def test_template_page_missing_text():
    params = {
        "byline": "this is a byline",
    }
    response = client.get("/page/90daydx")
    assert response.status_code == 422

def test_proxy_rss_feed():
    response = client.get("/rss/feed/90daydx")
    assert response.status_code == 200

def test_proxy_rss_feed_not_found():
    response = client.get("/rss/feed/nothere")
    assert response.status_code == 404

def test_proxy_rss_link():
    params = {
        "url": 'https://www.90daydx.com',
        "byline": urllib.parse.quote('test suite')
    }
    response = client.get("/rss/link", params=params)
    assert response.status_code == 200

def test_proxy_rss_link_missing_url():
    params = {
        "byline": urllib.parse.quote('test suite')
    }
    response = client.get("/rss/link", params=params)
    assert response.status_code == 422

def test_proxy_rss_link_missing_byline():
    params = {
        "url": urllib.parse.quote('https://www.90daydx.com')
    }
    response = client.get(f"/rss/link", params=params)
    assert response.status_code == 422


def test_proxy_rss_link_missing_title():
    html = '<html><head></head><body></body></html>'
    r = requests.put('https://the99utilsliflrvju-keyvalstore.functions.fnc.fr-par.scw.cloud/test-no-title', data=html)
    params = {
        "byline": urllib.parse.quote('test suite'),
        "url": 'https://the99utilsliflrvju-keyvalstore.functions.fnc.fr-par.scw.cloud/test-no-title'
    }
    response = client.get(f"/rss/link", params=params)
    assert response.status_code == 200


def test_proxy_rss_link_missing_meta_Description():
    html = "<html><head></head><body></body></html>"
    r = requests.put('https://the99utilsliflrvju-keyvalstore.functions.fnc.fr-par.scw.cloud/test-no-title', data=html)
    params = {
        "byline": urllib.parse.quote('test suite'),
        "url": 'https://the99utilsliflrvju-keyvalstore.functions.fnc.fr-par.scw.cloud/test-no-title'
    }
    response = client.get(f"/rss/link", params=params)
    assert response.status_code == 200
