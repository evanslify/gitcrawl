import os
import genson
import json
import codecs

js_folder = 'json'
js_abspath = os.path.abspath(js_folder)
# folder name of the json folder

def getnames(dir=js_abspath, ext='.json'):
    for filename in os.listdir(js_folder):
        if filename.endswith(ext):
            callgen(filename)


def callgen(json_filename):

    s = genson.Schema()
    json_path = './json/' + json_filename
    file = codecs.open(json_path, 'r', 'utf-8')
    jr = json.loads(file.read())
    s.add_object(jr)
    new_abs = './schema/schema_' + json_filename

    newfile = codecs.open(new_abs, 'w+', 'utf-8')
    newfile.write(s.to_json())
    newfile.close()

getnames()