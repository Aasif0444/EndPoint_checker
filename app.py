from flask import Flask,redirect,render_template,request,jsonify
from bs4 import BeautifulSoup
import requests
import lxml
import time
import os

app = Flask(__name__)

@app.route('/')
def home():
    return "this is working api"

@app.route('/check', methods=['POST'])
def check():
    data = request.get_json()
    sitemap_url = data.get('sitemap_url')
    only_count = data.get('only_count',False)
    limit = data.get('limit')

    if not sitemap_url:
        return jsonify({'error': 'Missing sitemap_url'}), 400

    try:
        response = requests.get(sitemap_url)
        content_type = response.headers.get('Content-Type', '')
        if 'xml' not in content_type:
            print("❌ Not a valid XML file.")
            return jsonify({'error': 'Not a valid XML file'}), 400
    except Exception as e:
        print("❌ Sitemap not found or site unreachable.")
        return jsonify({'error': 'Sitemap not found or site is unreachable'}), 400

    soup = BeautifulSoup(response.content, 'xml')
    loc_tags = soup.find_all('loc')
    total_endpoints = len(loc_tags)

    if only_count:
        return jsonify({'total_endpoints':total_endpoints})
    
    url_to_check = loc_tags[:int(limit)] if limit else loc_tags

    running_endpoints = 0
    damaged_endpoints = 0
    damaged_endpoints_list = []

    for tag in url_to_check:
        url = tag.text

        try:
            response = requests.get(url, timeout=5)
            if response.status_code in (200, 301, 302):
                print(f"✅ {url}")
                running_endpoints += 1
            else:
                print(f"❌ {url}")
                damaged_endpoints_list.append(url)
                damaged_endpoints += 1
        except requests.exceptions.RequestException:
            print(f"❌ {url}")
            damaged_endpoints_list.append(url)
            damaged_endpoints += 1

        time.sleep(0.2)

    

    return jsonify({
        'total_endpoints': total_endpoints,
        'running_endpoints': running_endpoints,
        'damaged_endpoints': damaged_endpoints,
        'damaged_endpoints_list': damaged_endpoints_list,
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0',port=port)
