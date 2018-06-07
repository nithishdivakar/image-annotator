from flask import Flask, render_template, abort
from flask import request
from flask import jsonify
from flask import send_from_directory
from flask import send_file

import glob
import uuid
import os

app = Flask(__name__)


COLORS = [
    '#008B8B',
    '#FF0000',
    '#EE82EE',
    '#DAA520',
    '#000080',
    '#800000',
    '#008000',
    '#FF7F50',
    '#00FFFF',
    '#008080',
    '#808000',
    '#FF8C00',
    '#FFFF00',
    '#800080',
    '#00FF00',
    '#FF69B4',
    '#32CD32',
    '#4682B4',
    '#0000FF',
    '#FF00FF',
]


IMAGES = {}
CLASS_NAMES = []


def check_mkdirs(path):
  if not os.path.isdir(path):
    os.makedirs(path)


def init():
  for img_path in glob.glob("unlabelled/*.png") + \
          glob.glob("unlabelled/*.jpg"):
    IMAGES[str(uuid.uuid4())] = img_path

  with open('class_names.txt', 'r') as fobj:
    for l in fobj:
      CLASS_NAMES.append(l.strip())

  check_mkdirs("labelled")
  for class_name in CLASS_NAMES:
    check_mkdirs(os.path.join("labelled", class_name))


@app.route('/')
def index():
  image_ids = list(IMAGES.keys())
  return render_template('home.html', class_names=CLASS_NAMES,
                         images=image_ids[:20], colors=COLORS)


@app.route('/label', methods=['POST'])
def label_image():
  image_id = request.form['image_id']
  label = request.form['label']
  image_path = IMAGES[image_id]
  assert label in CLASS_NAMES

  os.system("mv {} labelled/{}".format(image_path, label))
  del IMAGES[image_id]

  return jsonify({"status": "True"})


@app.route('/get_image/<image_id>', methods=['GET', 'POST'])
def image_serve(image_id):
  if request.method == 'GET':
    ext = IMAGES[image_id].split(".")[-1]
    return send_file(
        IMAGES[image_id], attachment_filename=image_id + "." + ext)

@app.route('/get_stats', methods=['GET'])
def stats():
  ANNOT = {}
  for class_name in CLASS_NAMES:
    L = glob.glob(os.path.join("labelled", class_name)+"/*.png")
    ANNOT[class_name] = len(L)
  return jsonify(ANNOT)


if __name__ == '__main__':
  import argparse
  init()
  app.run(host='0.0.0.0', port=5000, debug=True)
