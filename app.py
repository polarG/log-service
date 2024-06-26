from flask import Flask, request, jsonify
import os
import socket

app = Flask(__name__)
LOG_DIR = './data' #/var/log'
MAX_PER_PAGE = 100

@app.route('/logs', methods=['GET'])
def get_logs():    
    filename = request.args.get('filename')
    keyword = request.args.get('keyword')
    limit = request.args.get('limit', default=10, type=int)
    offset = request.args.get('offset', default=0, type=int)

    app.logger.debug(f"filename={filename}, keyword={keyword}, limit={limit}, offset={offset}")

    if not filename:
        return jsonify({'error': 'No filename specified'}), 400

    file_path = os.path.join(LOG_DIR, filename)
    if not os.path.exists(file_path):
        return jsonify({'error': 'No specified file'}), 404

    lines = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                if keyword and keyword not in line:
                    continue

                lines.append(line.strip())
    except Exception as e:
        return jsonify({'error': str(e)}), 500

    if len(lines) - limit > 0:
        # trunc lines to limit length
        lines = lines[len(lines) - limit: ]
    
    lines.reverse() # reverse lines
    
    res = [{
        'hostname': socket.gethostname(), 
        'IP': socket.gethostbyname(socket.gethostname()),
        'file': file_path,
        'start': offset,
        'next page': limit + 1,
        'log': lines
        }]

    return jsonify(res)
