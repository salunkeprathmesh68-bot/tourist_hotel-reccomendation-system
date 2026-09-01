"""
Smart Kolhapur Guide - Application Launcher
Runs the modular Flask application with backend routes and frontend templates.
"""
from backend.app import app

if __name__ == '__main__':
    print("============================================================")
    print(" [START] SMART KOLHAPUR GUIDE - Web Application Starting")
    print(" [INFO]  District: Kolhapur, Maharashtra, India")
    print(" [INFO]  Backend: Python Flask & Modular Blueprints")
    print(" [INFO]  Frontend: Jinja2 HTML5, CSS3 & JavaScript")
    print(" [INFO]  Running on: http://127.0.0.1:5000")
    print("============================================================")
    app.run(debug=True, host='127.0.0.1', port=5000)
