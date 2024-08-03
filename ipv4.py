from flask import Flask, request, jsonify, send_file
import random
import requests
from collections import Counter
import re
import io

app = Flask(__name__)

def generate_random_ip():
    return f"192.168.{random.randint(0, 255)}.{random.randint(0, 255)}"

def is_valid_ip(ip):
    return bool(re.match(r'^192\.168\.\d{1,3}\.\d{1,3}$', ip))

def generate_ip_addresses(count):
    return [generate_random_ip() for _ in range(count)]

def most_common_ip(ip_list):
    if not ip_list:
        return None
    ip_counter = Counter(ip_list)
    return ip_counter.most_common(1)[0][0]

def generate_ip_data(count):
    ips = generate_ip_addresses(count)
    most_common = most_common_ip(ips)
    ip_data = [f"{ip} {'valid' if is_valid_ip(ip) else 'invalid'}" for ip in ips]
    return most_common, ip_data

@app.route('/')
def index():
    return '''
    <h1>IP Generator</h1>
    <form action="/generate" method="post">
        <label for="count">Number of IPs to generate (1-1000000):</label><br>
        <input type="number" id="count" name="count" min="1" max="1000000" required><br><br>
        <input type="submit" value="Generate">
    </form>
    <form action="/webhook" method="post">
        <label for="count">Number of IPs to generate (1-1000000):</label><br>
        <input type="number" id="count" name="count" min="1" max="1000000" required><br><br>
        <label for="webhook_url">Webhook URL:</label><br>
        <input type="text" id="webhook_url" name="webhook_url" required><br><br>
        <input type="submit" value="Send to Webhook">
    </form>
    '''

@app.route('/generate', methods=['POST'])
def generate():
    count = int(request.form.get('count', 1000))
    most_common, ip_data = generate_ip_data(count)
    
    output = io.StringIO()
    output.write(f"Most Common IP: {most_common}\n\n")
    output.write("\n".join(ip_data))
    output.seek(0)
    
    return send_file(io.BytesIO(output.getvalue().encode()), attachment_filename="ip.txt", as_attachment=True)

@app.route('/webhook', methods=['POST'])
def webhook():
    count = int(request.form.get('count', 1000))
    webhook_url = request.form.get('webhook_url')
    most_common, ip_data = generate_ip_data(count)
    
    output = io.StringIO()
    output.write(f"Most Common IP: {most_common}\n\n")
    output.write("\n".join(ip_data))
    output.seek(0)
    
    file_content = io.BytesIO(output.getvalue().encode())
    requests.post(
        webhook_url,
        files={"file": ("ip.txt", file_content)},
        data={"content": "Here are your generated IP addresses:"}
    )
    
    return jsonify({"message": "IPs sent to the webhook."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
