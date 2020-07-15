from bs4 import BeautifulSoup
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.responses import StreamingResponse
import io
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from typing import Optional
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from pathlib import Path
from jinja2 import Template

import urllib
import requests
from requests_html import HTMLSession
import os

import database


app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

BASE_DOMAIN = os.getenv('BASE_DOMAIN', 'http://localhost:8000')



@app.get("/")
async def status():
    return {"status": "OK"}

@app.get("/feeds")
async def feeds(request: Request):
    return database.feeds

@app.get("/page/{template}")
async def template_page(request: Request,
                        template: str,
                        text: str,
                        byline: str):
    payload = {
        "request": request,
        "text": text,
        "byline": byline,
    }
    return templates.TemplateResponse(f"{template}.html", payload)

@app.get("/generate/firefox-remote/{template}")
async def firefox_remote_page(request: Request, template: str, text: Optional[str] = None):

    selenium_grid_url = "http://streaming1:4444/wd/hub"

    #capabilities = DesiredCapabilities.FIREFOX.copy()
    capabilities = DesiredCapabilities.CHROME.copy()

    driver = webdriver.Remote(desired_capabilities=capabilities,
                          command_executor=selenium_grid_url)
#    profile = webdriver.FirefoxProfile()
#    options = Options()
#    options.headless = True
#    driver = webdriver.Firefox(options=options, firefox_profile=profile)
    driver.set_window_size(1200, 630)
    driver.get(f"http://192.168.1.7:8000/page/{template}?text={text}")
    image = driver.get_screenshot_as_png()
    driver.quit()
    return StreamingResponse(io.BytesIO(image), 
                             media_type="image/png")


@app.get("/generate/{browser}/{template}")
async def get_ogimage(request: Request,
                      browser: str,
                      template: str,
                      text: str,
                      byline: str):

    template_str = Path(f"templates/{template}.html").read_text()
    t = Template(template_str)
    html = urllib.parse.quote(t.render(text=text, page_byline=byline))

    image = generate_screenshot(browser=browser, html=html)
    return StreamingResponse(io.BytesIO(image), 
                             media_type="image/png")


def generate_screenshot(browser: str, html: str):
    if browser == 'chrome':
        options = webdriver.ChromeOptions()
        options.add_argument('--no-sandbox')
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        driver = webdriver.Chrome(options=options)

    elif browser == 'firefox':
        profile = webdriver.FirefoxProfile()
        options = Options()
        options.headless = True
        driver = webdriver.Firefox(options=options, firefox_profile=profile)

    driver.set_window_size(1200, 630)
    driver.get(f"data:text/html;charset=utf-8,{html}")
    image = driver.get_screenshot_as_png()
    driver.quit()

    return image

# dont break this! it is used in production
@app.get('/rss/feed/{rss_name}')
async def proxy_rss_feed(request: Request, rss_name: str):

    if rss_name not in database.feeds:
        raise HTTPException(status_code=404, detail="Feed not found")

    r = requests.get(database.feeds[rss_name]['url'])
    byline = urllib.parse.quote(database.feeds[rss_name]['name'])

    soup = BeautifulSoup(r.content, "xml")
    items = soup.find_all('item')
    for i in items:
        link = i.find('link')

        url = urllib.parse.quote(link.text)

        link.string = f'{BASE_DOMAIN}/rss/link?url={url}&byline={byline}'

    return Response(content=soup, media_type="application/xml")

@app.get('/rss/link')
async def proxy_rss_link(request: Request, url: str, byline: str):

    session = HTMLSession()
    r = session.get(url)

    try: 
        title = r.html.find('title', first=True).text
    except AttributeError:
        title = ''

    try:
        description = r.html.find('meta[name=description]',first=True).attrs['content']
    except AttributeError:
        description = ''
    except KeyError:
        description = ''

    title_encoded = urllib.parse.quote(title)

    page_content = ''.join([h.html for h in r.html.find('body *')])
    payload = {
        "request": request,
        "page_title": title,
        "page_byline": byline,
        "page_description": description, 
        "page_content": page_content,
        "og_image": f'{BASE_DOMAIN}/generate/chrome/90daydx?text={title_encoded}&byline={byline}',
        "page_link": url
    }
    return templates.TemplateResponse(f"fake_page.html", payload)
