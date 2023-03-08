from flask import Flask, jsonify, request, render_template, send_file, redirect
import os
import glob
import pandas as pd
import json
import zipfile
import ast


app = Flask(__name__)
app = Flask(__name__, template_folder='')

@app.route("/")
def upload_file():
   return render_template('upload.html')

@app.route("/uploader", methods = ['POST'])
def uploader():
    # delete existing csv files except export.csv
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    for csv_file in csv_files:
        os.remove(csv_file)

    file = request.files['file']
    filename = file.filename
    file.save(filename)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall('.')
    title = request.form['title']
    drill_data_str = request.form['drill_data']
    drill_data = [x.strip() for x in drill_data_str.split(',')]
    path = os.getcwd()
    csv_files = glob.glob(os.path.join(path, "*.csv"))
    data_frame = []
    for f in csv_files:
            if(f.find("export.csv") != -1) :
                continue
            df = pd.read_csv(f)
            df['Info'] = df['Info'].apply(lambda x: x.replace(title, ''))
            df['Info'] = df['Info'].apply(ast.literal_eval)
            # df['Info'] = df['Info'].apply(json.loads)
            column_names = set()
            for row in df['Info']:
                column_names |= set(row.keys())
            for col_name in column_names:
                df[col_name] = df['Info'].apply(lambda x: x.get(col_name, None))
            for drill in drill_data:
                df[drill] = df[drill].apply(json.dumps)
                df[drill] = df[drill].apply(json.loads)
                column_names = set()
                for row in df[drill]:
                    if row:
                        column_names |= set(row.keys())
                for col_name in column_names:
                    col_name2 = drill + "_" + col_name
                    df[col_name2] = df[drill].apply(lambda x: x.get(col_name, None) if isinstance(x, dict) and x is not None else None)
            data_frame.append(df)
    result = pd.concat(data_frame)
    result.to_csv("export.csv",index=False)
    os.remove(filename)
    return redirect('/download')

@app.route("/download")
def download_file():
    # download export.csv
    return send_file("export.csv", as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)