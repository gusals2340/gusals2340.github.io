from flask import Flask, request, jsonify, send_from_directory
from werkzeug.utils import secure_filename
import pandas as pd
import os
import json

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONFIG_FOLDER = 'config'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CONFIG_FOLDER'] = CONFIG_FOLDER

# 업로드 폴더 생성
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html') # index.html을 제공 (테스트용)

@app.route('/<path:path>')
def serve_static(path):
    # 정적 파일 제공 (JS, CSS 등)
    return send_from_directory('.', path)

@app.route('/config/<path:filename>')
def serve_config_file(filename):
    # config 폴더의 파일 제공
    return send_from_directory(app.config['CONFIG_FOLDER'], filename)

@app.route('/upload_excel', methods=['POST'])
def upload_excel():
    if 'file' not in request.files:
        return jsonify({"error": "파일이 없습니다."}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "파일 이름이 없습니다."}), 400
    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        output_csv_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'csv_output')
        if not os.path.exists(output_csv_dir):
            os.makedirs(output_csv_dir)

        try:
            xls = pd.ExcelFile(filepath)
            sheet_names = xls.sheet_names
            converted_csv_files = []

            for sheet_name in sheet_names:
                df = pd.read_excel(filepath, sheet_name=sheet_name)
                base_excel_name = os.path.splitext(os.path.basename(filepath))[0]
                csv_file_name = "{}_{}.csv".format(base_excel_name, sheet_name)
                csv_file_path = os.path.join(output_csv_dir, csv_file_name)
                df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
                converted_csv_files.append(csv_file_name)
            
            return jsonify({"message": "엑셀 파일이 성공적으로 CSV로 변환되었습니다.", "csv_files": converted_csv_files}), 200

        except Exception as e:
            return jsonify({"error": "엑셀 파일을 CSV로 변환하는 중 오류가 발생했습니다: {}".format(e)}), 500
    return jsonify({"error": "파일 업로드 실패"}), 500

@app.route('/get_style_json', methods=['GET'])
def get_style_json():
    try:
        with open(os.path.join(app.config['CONFIG_FOLDER'], 'style_20241224_hkmc.json'), 'r', encoding='utf-8') as f:
            style_data = json.load(f)
        return jsonify(style_data), 200
    except FileNotFoundError:
        return jsonify({"error": "style_20241224_hkmc.json 파일을 찾을 수 없습니다."}), 404
    except Exception as e:
        return jsonify({"error": "스타일 JSON 파일을 읽는 중 오류가 발생했습니다: {}".format(e)}), 500

if __name__ == '__main__':
    # 필요한 라이브러리 설치 안내
    try:
        import pandas as pd
        from flask import Flask # Flask가 설치되어 있는지 확인
    except ImportError:
        print("필요한 라이브러리가 설치되어 있지 않습니다.")
        print("pip install Flask pandas openpyxl")
        exit()
    
    # Flask 서버 실행
    # 개발 환경에서는 debug=True로 설정하여 변경 사항 자동 반영 및 디버깅 정보 확인
    # 실제 배포 시에는 debug=False로 설정하고, Gunicorn과 같은 WSGI 서버 사용 권장
    app.run(debug=True, port=5000)
