"""
Flask Web Application for Market Intelligence Swarm
"""
from flask import Flask, jsonify, render_template
from flask_cors import CORS
from swarm_orchestrator import SwarmOrchestrator
import config

app = Flask(__name__)
CORS(app)

# Initialize swarm orchestrator
swarm = SwarmOrchestrator()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/api/intelligence')
def get_intelligence():
    """Get market intelligence"""
    force_refresh = False  # Can be made configurable via query param
    intelligence = swarm.get_intelligence(force_refresh=force_refresh)
    return jsonify(intelligence)

@app.route('/api/intelligence/refresh')
def refresh_intelligence():
    """Force refresh intelligence"""
    intelligence = swarm.get_intelligence(force_refresh=True)
    return jsonify(intelligence)

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Market Intelligence Swarm',
        'version': '1.0.0'
    })

if __name__ == '__main__':
    # Initial intelligence gathering
    print("Initializing Market Intelligence Swarm...")
    swarm.get_intelligence(force_refresh=True)
    
    # Start Flask server
    app.run(
        host=config.SERVER_CONFIG['host'],
        port=config.SERVER_CONFIG['port'],
        debug=config.SERVER_CONFIG['debug']
    )
