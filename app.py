from flask import Flask, request, jsonify
import os
import socket
import concurrent.futures
import urllib.request
import json

app = Flask(__name__)
LOG_DIR = '/var/log'
PRIMARY = False
THREAD_POOL_MAX_WORKERS = 10
SECONDARY_SERVERS = 'second.cfg'
# MAX_PER_PAGE = 100

def get_remote_log(filename, keyword, limit, offset):
    def send_req(hostname):
        # construct secondary URL
        url = f"http://{hostname}:5000/logs?filename={filename}"
        if keyword:
            url += f"&keyword={keyword}"

        if limit:
            url += f"&limit={limit}"

        if offset:
            url += f"&offset={offset}"

        with urllib.request.urlopen(url, timeout=5) as conn:
            return conn.read()
        
    # load secondary configs
    if not os.path.exists(SECONDARY_SERVERS):
        app.logger.warning(f"Config file for Secondary servers is not exist")
        return []

    with open(SECONDARY_SERVERS, 'r') as file:
        hosts = file.readlines()
    
    # use threadpool to retrieve logs from seconary servers
    res = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=THREAD_POOL_MAX_WORKERS) as excutor:
        futures = {excutor.submit(send_req, hostname.strip()): hostname.strip() for hostname in hosts}
        for future in concurrent.futures.as_completed(futures, timeout=10):
            try:
                data = future.result()
                res.append(json.loads(data)[0])
            except Exception as e:
                app.logger.warning(f"Failed to get log from secondary server ({futures[future]}. Exception: {str(e)})")
            else:
                app.logger.info(f"Retrieved logs from secondary server ({futures[future]}) with file {filename}")

    return res


@app.route('/logs', methods=['GET'])
def get_logs():    
    filename = request.args.get('filename')
    keyword = request.args.get('keyword')
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    app.logger.debug(f"filename={filename}, keyword={keyword}, limit={limit}, offset={offset}")

    if not filename:
        app.logger.error('No filename specified')
        return jsonify({'error': 'No filename specified'}), 400

    file_path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(file_path):
        app.logger.error('No filename specified')
        return jsonify({'error': 'No specified file'}), 404

    lines = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if keyword and keyword not in line:
                    continue

                lines.append(line.strip())
    except Exception as e:
        app.logger.error(str(e))
        return jsonify({'error': str(e)}), 500

    end = len(lines) - offset
    start = end - limit if end > limit else 0
    # trunc lines to limit length
    lines = lines[start: end]
    
    # reverse lines
    lines.reverse() 

    app.logger.debug(f"Response contain {len(lines)} lines.")
    
    res = [{
        'hostname': socket.gethostname(), 
        'IP': socket.gethostbyname(socket.gethostname()),
        'file': file_path,
        'offset': offset + limit,
        'log': lines
        }]
    
    if PRIMARY:
        res.extend(get_remote_log(filename, keyword, limit, offset))

    return jsonify(res)
