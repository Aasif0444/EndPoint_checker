from flask import Flask,redirect,render_template,request,jsonify
from bs4 import BeautifulSoup
import requests
import lxml
import time


app = Flask(__name__)


@app.route('/')
def home_page():
    return "flask app running fine"
@app.route('/check',methods = ['POST'])
def check():
    data = request.get_json()


    sitemap_url = data.get('sitemap_url')

    if not sitemap_url:
        return jsonify({'error': 'Missing sitemap_url'}), 400

    try:
        response = requests.get(sitemap_url)
        content_type = response.headers.get('Content-Type')

        if 'xml' not in content_type:
            print("Not proper xml file found ❌")
            exit()
        
    except:
        print('❌ XML not found or site unreachable')
        return jsonify({'error': 'Sitemap not found or site is unreachable'}), 400

    soup = BeautifulSoup(response.content,'xml')

    loc_tags = soup.find_all('loc')
    total_endpoints = 0
    running_endpoints = 0
    damaged_endpoints = 0 
    damaged_endpoints_list = []

    for tag in loc_tags:
        url = tag.text
        response = requests.get(url,timeout=5)
        
        try:
            if response.status_code in  (200,301,302):
                print(f"{url} ✅")
                running_endpoints += 1
                
            else:
                print(f"{url} ❌")
                damaged_endpoints_list.append(url)
                damaged_endpoints += 1 
        except requests.exceptions.RequestException:
            damaged_endpoints_list.append(url)
            damaged_endpoints += 1
        
        time.sleep(0.3)
        total_endpoints += 1


    print(f"total endpoints = {total_endpoints}")
    print(f"running_endpoints = {running_endpoints}")
    print(f"damaged_endpoints = {damaged_endpoints}")

    return jsonify({
        'total_endpoints':total_endpoints,
        'running_endpoints':running_endpoints,
        'damaged_endpoints':damaged_endpoints
    })


if __name__ == '__main__':
    app.run(debug=True)