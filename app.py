import re
import pandas as pd
import sqlite3

from flask import Flask, jsonify
from flask import request
from flasgger import Swagger, LazyString, LazyJSONEncoder
from flasgger import swag_from
 
app = Flask(__name__)

app.json_encoder = LazyJSONEncoder
swagger_template = dict (
info = {
    'title' : LazyString(lambda: 'API Documentation for Data Processing and Modelling '),
    'version' : LazyString(lambda: '1.0.0'),
    'description' : LazyString(lambda: 'Dokumentasi API untuk Data Processing dan Modeling'),
    },
    host = LazyString(lambda: request.host)
)
swagger_config = {
    "headers" : [],
    "specs": [
        {
            "endpoint": 'docs',
            "route": '/docs.json',
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/docs"
}
swagger = Swagger(app, template=swagger_template,
                config=swagger_config)

@swag_from("docs/text_processing.yml", methods=['POST'])
@app.route('/text-processing', methods=['POST'])
def text_processing():
    
    text = request.form.get('text')
    
    json_response = {
        'status_code': 200,
        'description': "Teks yang Sudah diproses",
        'data': re.sub(r'[^a-zA-Z0-9]', ' ', text)
    }

    dbtext = sqlite3.connect('docs/textprocessingdb.db')
    #dbtext.execute('''CREATE TABLE sebelumsesudahtext(sebelum varchar(255), sesudah varchar(255));''')
    dbtext.execute('INSERT INTO sebelumsesudahtext VALUES (?,?)', (text, json_response['data']))
    
    dbtext.commit()
    dbtext.close()

    response_data = jsonify(json_response)
    return response_data

@swag_from("docs/upload_file.yml", methods=['POST'])
@app.route('/upload', methods=['POST'])
def upload_file():

    upload = request.files['upload']
    upload_csv = pd.read_csv(upload, encoding='latin-1')
    upload_csv = upload_csv['Tweet']
    upload_csv = upload_csv.drop_duplicates()
    upload_csv = upload_csv.dropna()

    upload_csv = upload_csv.values.tolist()
    x = 0
    file = {}
    for str in upload_csv:
        
        file[x] = {}
        file[x]['Tweet'] = str
        file[x]['Tweet_Clean'] = re.sub(r'[^a-zA-Z0-9]', ' ', str)
        
        dbfile = sqlite3.connect('docs/uploadfiledb.db')
        #dbfile.execute('''CREATE TABLE sebelumsesudahfile(sebelumfile varchar(255), sesudahfile varchar(255));''')
        dbfile.execute('INSERT INTO sebelumsesudahfile VALUES (?,?)', (str, file[x]['Tweet_Clean']))
        dbfile.commit()
        dbfile.close()

        x = x + 1
        
    return file

if __name__ =='__main__':
    app.debug = True
    app.run()