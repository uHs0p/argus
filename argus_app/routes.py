from flask import Blueprint, request, jsonify, render_template, send_file
from .utils.scanner import APIScanner
from .utils.report_generator import generate_report
from models import db, ScanResult
from .controllers import *
import json
import os

app_blueprint = Blueprint(
    'app',
    __name__,
    template_folder='templates',
    static_folder='static',
    static_url_path='/app/static'
)

@app_blueprint.route('/')
def index():
    return render_template('argus/index.html')

@app_blueprint.route('/scanner',methods=['GET','POST'])
def scanner():
    if request.method == 'POST':
        data = request.form
        url = data.get('url')
        scanner = APIScanner()
        open_endpoints = scanner.scan_api(url)
        another_open_endpoints = scanner.fuzz_directory(url)
        owasp_zap_results = [
            "mkc 1 baar",
            "mkc 2 baar",
            "mkc 3 baar",
        ]
        # owasp_top_10 = {
        #     "name": "Darshan Soni",
        #     "age": 21,
        #     "skills": ["Python", "Cybersecurity", "PowerShell"],
        #     "details": {
        #         "email": "sonidarshan200@gmail.com",
        #         "location": "Pune, Maharashtra"
        #     }
        # }
        
        return render_template(
            'argus/scanner.html',
            endpoints=open_endpoints, 
            owasp_zap_results = owasp_zap_results,
            owasp_top_10 = another_open_endpoints
        )
    else:
        return render_template('argus/scanner.html')

@app_blueprint.route('/report')
def report():
    # Query all scans for the user (e.g., user_id = 1 for demonstration purposes)
    user_id = 1  # Replace with actual logic to get the current logged-in user
    scans = ScanResult.query.filter_by(user_id=user_id).all()
    return render_template('argus/report.html', scans=scans)

@app_blueprint.route('/login')
def login():
    return render_template('argus/login.html')

@app_blueprint.route('/test')
def test():
    return render_template('argus/test.html')

@app_blueprint.route('/generate-report/<int:url_id>', methods=['GET'])
def generate_report_route(url_id):
    # Fetch data from the database
    scan = ScanResult.query.get(url_id)
    if not scan:
        return {"error": "Scan not found"}, 404

    # Prepare data
    report_data = {
        "original_url": scan.original_endpoint,
        "open_endpoints": json.loads(scan.endpoints),
        "vulnerabilities_found": json.loads(scan.result),
        "timestamp": scan.timestamp,
    }

    output_dir = "argus_app/static/reports"
    report_name = f"Scan_{scan.id}_{scan.timestamp.strftime('%Y%m%d%H%M%S')}.pdf"
    output_path = os.path.join(output_dir, report_name)

    # Create the directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    generate_report(report_data, output_path)

    # Serve the file
    return send_file(output_path, as_attachment=True)