"""
Simple health check server for Streamlit container health monitoring.
Runs alongside Streamlit to provide health check endpoint.
"""

from flask import Flask
import threading
import time

app = Flask(__name__)

@app.route('/health')
def health():
    """Health check endpoint for Docker health monitoring."""
    return {'status': 'healthy', 'service': 'streamlit-ui'}, 200

def run_health_server():
    """Run health check server on port 8502."""
    app.run(host='0.0.0.0', port=8502, debug=False)

if __name__ == '__main__':
    # Start health server in background thread
    health_thread = threading.Thread(target=run_health_server, daemon=True)
    health_thread.start()
    
    # Keep main thread alive
    while True:
        time.sleep(60)