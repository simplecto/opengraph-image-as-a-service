import requests
from webpreview import web_preview
from datetime import datetime, date
import dateparser
import pytz


def get_og_image_as_rss_enclosure_attrs(url):

    headers = {"User-Agent":"Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36"}
    title, description, image = web_preview(url, parser='lxml', headers=headers)

    if not image:
        return None

    r = requests.get(image)

    return {
        "url": image,
        "type": r.headers.get('content-type'),
        "length": len(r.content)
    }


def get_item_age_days(item):
    pub_date = item.find('pubDate').text
    date_published = dateparser.parse(pub_date)
    right_now = datetime.now(date_published.tzinfo)
    return (right_now - date_published).days
