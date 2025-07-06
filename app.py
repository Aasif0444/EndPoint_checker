from flask import Flask,redirect,render_template,request,jsonify,Response
from bs4 import BeautifulSoup
import requests
import lxml
import time
import os

app = Flask(__name__)


@app.route('/')
def home_page():
    return "flask app running fine"

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    sitemap_url = data.get('sitemap_url')

    def generate_logs():
        if not sitemap_url:
            yield "❌ Missing sitemap_url\n"
            return

        yield f"🔍 Fetching sitemap: {sitemap_url}\n"

        try:
            response = requests.get(sitemap_url)
            content_type = response.headers.get('Content-Type')

            if 'xml' not in content_type:
                yield "❌ Not proper XML file found\n"
                return
        except:
            yield '❌ XML not found or site unreachable\n'
            return

        soup = BeautifulSoup(response.content, 'xml')
        loc_tags = soup.find_all('loc')

        total_endpoints = 0
        running_endpoints = 0
        damaged_endpoints = 0
        damaged_endpoints_list = []

        for tag in loc_tags:
            url = tag.text
            total_endpoints += 1
            yield f"🔗 Checking {total_endpoints} of {len(loc_tags)} → {url}\n"

            try:
                response = requests.get(url, timeout=5)
                if response.status_code in (200, 301, 302):
                    running_endpoints += 1
                    yield f"✅ {url}\n"
                else:
                    damaged_endpoints += 1
                    damaged_endpoints_list.append(url)
                    yield f"❌ {url} [{response.status_code}]\n"
            except requests.exceptions.RequestException:
                damaged_endpoints += 1
                damaged_endpoints_list.append(url)
                yield f"❌ Failed to connect: {url}\n"

            time.sleep(0.3)

        yield f"\n📊 total_endpoints = {total_endpoints}\n"
        yield f"✅ running_endpoints = {running_endpoints}\n"
        yield f"❌ damaged_endpoints = {damaged_endpoints}\n"
        yield "✅ Completed.\n"

    return Response(generate_logs(), mimetype='text/plain')





if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
