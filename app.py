from flask import Flask, request, jsonify
import threading
import time
import sys
import os
from gen import create_acc, REGION_URLS, get_region

app = Flask(__name__)

# Global variables to track generation status
generation_status = {}
accounts_results = {}

@app.route('/gen', methods=['GET'])
def generate_accounts():
    try:
        # Get parameters
        name = request.args.get('name', 'FALCON')
        count = int(request.args.get('count', 1))
        region = request.args.get('region')
        
        # Validate parameters
        if not region:
            return jsonify({
                'success': False,
                'error': 'Region parameter is required'
            }), 400
        
        if region not in REGION_URLS:
            return jsonify({
                'success': False,
                'error': f'Invalid region. Available regions: {list(REGION_URLS.keys())}'
            }), 400
        
        if count < 1 or count > 100:
            return jsonify({
                'success': False,
                'error': 'Count must be between 1 and 100'
            }), 400
        
        # Initialize generation status
        generation_id = f"{name}_{region}_{int(time.time())}"
        generation_status[generation_id] = {
            'status': 'started',
            'completed': 0,
            'total': count,
            'accounts': [],
            'errors': []
        }
        
        # Start account generation in background thread
        thread = threading.Thread(target=generate_accounts_thread, args=(generation_id, name, count, region))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'generation_id': generation_id,
            'message': f'Started generating {count} accounts for region {region}',
            'status_url': f'/status/{generation_id}'
        })
        
    except ValueError:
        return jsonify({
            'success': False,
            'error': 'Count must be a valid integer'
        }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

def generate_accounts_thread(generation_id, name, count, region):
    """Background thread to generate accounts"""
    try:
        for i in range(count):
            try:
                # Generate account
                result = create_acc(region)
                
                if result:
                    account_data = {
                        'name': result.get('name', name),
                        'uid': result.get('uid'),
                        'password': result.get('password'),
                        'region': region,
                        'game_uid': result.get('game_uid'),
                        'jwt_token': result.get('jwt_token'),
                        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    generation_status[generation_id]['accounts'].append(account_data)
                else:
                    generation_status[generation_id]['errors'].append(f'Failed to create account {i+1}')
                
                generation_status[generation_id]['completed'] = i + 1
                
                # Small delay to prevent rate limiting
                time.sleep(0.5)
                
            except Exception as e:
                generation_status[generation_id]['errors'].append(f'Error creating account {i+1}: {str(e)}')
                generation_status[generation_id]['completed'] = i + 1
        
        # Mark as completed
        generation_status[generation_id]['status'] = 'completed'
        
        # Store final results
        accounts_results[generation_id] = generation_status[generation_id].copy()
        
    except Exception as e:
        generation_status[generation_id]['status'] = 'failed'
        generation_status[generation_id]['error'] = str(e)

@app.route('/status/<generation_id>', methods=['GET'])
def get_status(generation_id):
    if generation_id not in generation_status:
        return jsonify({
            'success': False,
            'error': 'Generation ID not found'
        }), 404
    
    status = generation_status[generation_id]
    
    return jsonify({
        'success': True,
        'generation_id': generation_id,
        'status': status['status'],
        'completed': status['completed'],
        'total': status['total'],
        'accounts_count': len(status['accounts']),
        'errors_count': len(status['errors']),
        'accounts': status['accounts'] if status['status'] == 'completed' else [],
        'errors': status['errors']
    })

@app.route('/results/<generation_id>', methods=['GET'])
def get_results(generation_id):
    if generation_id not in accounts_results:
        return jsonify({
            'success': False,
            'error': 'Results not found for this generation ID'
        }), 404
    
    return jsonify({
        'success': True,
        'generation_id': generation_id,
        'results': accounts_results[generation_id]
    })

@app.route('/regions', methods=['GET'])
def get_regions():
    return jsonify({
        'success': True,
        'regions': list(REGION_URLS.keys()),
        'region_urls': REGION_URLS
    })

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'success': True,
        'status': 'healthy',
        'active_generations': len([s for s in generation_status.values() if s['status'] == 'started'])
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'success': True,
        'message': 'Free Fire Account Generator API',
        'endpoints': {
            'generate': '/gen?name=FALCON&count=1&region=IND',
            'status': '/status/{generation_id}',
            'results': '/results/{generation_id}',
            'regions': '/regions',
            'health': '/health'
        },
        'example_usage': {
            'generate_accounts': 'GET /gen?name=FALCON&count=5&region=IND',
            'check_status': 'GET /status/FALCON_IND_1642123456',
            'get_results': 'GET /results/FALCON_IND_1642123456'
        }
    })

if __name__ == '__main__':
    print("Starting Free Fire Account Generator API...")
    print("API will be available at: http://localhost:5000")
    print("Documentation: http://localhost:5000")
    print("Health Check: http://localhost:5000/health")
    print("Available Regions: http://localhost:5000/regions")
    print("\nExample Usage:")
    print("   Generate: http://localhost:5000/gen?name=FALCON&count=5&region=IND")
    print("   Status:   http://localhost:5000/status/{generation_id}")
    print("   Results:  http://localhost:5000/results/{generation_id}")
    
    app.run(host='0.0.0.0', port=5000, debug=True, threaded=True)
