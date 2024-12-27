import sys
import os

from flask import Flask, send_from_directory

PROJECT_DIR = os.path.join(os.path.dirname(__file__), '../..')
sys.path.append(PROJECT_DIR)

app = Flask(__name__)
PORT = 8001

# 设置图片存储路径
IMAGE_FOLDER = os.path.join(PROJECT_DIR, 'data/benchmark/data_analysis/excel')

@app.route('/<filename>')
def image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
