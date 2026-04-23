from flask import Flask, request, jsonify
from standalone_gen import create_acc, REGION_URLS, get_region
import time
import json
import os

app = Flask(__name__)

# File-based storage for Vercel compatibility
STATUS_FILE = "generation_status.json"
RESULTS_FILE = "generation_results.json"

def read_json_file(filename):
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                return json.load(f)
    except:
        pass
    return {}

def write_json_file(filename, data):
    try:
        with open(filename, 'w') as f:
            json.dump(data, f)
    except:
        pass

@app.route('/gen', methods=['GET'])
def generate_accounts():
    try:
        name = request.args.get('name', 'FALCON')
        count = int(request.args.get('count', 1))
        region = request.args.get('region')
        
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
        
        if count < 1 or count > 10:  # Reduced for Vercel
            return jsonify({
                'success': False,
                'error': 'Count must be between 1 and 10 (Vercel limit)'
            }), 400
        
        # Generate accounts synchronously (no threading)
        accounts = []
        errors = []
        
        for i in range(count):
            try:
                result = create_acc(region)
                if result and isinstance(result, dict) and 'error' not in result:
                    account_data = {
                        'name': result.get('name', name),
                        'uid': result.get('uid'),
                        'password': result.get('password'),
                        'region': region,
                        'game_uid': result.get('game_uid'),
                        'jwt_token': result.get('jwt_token'),
                        'access_token': result.get('access_token'),
                        'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    accounts.append(account_data)
                else:
                    if isinstance(result, dict) and 'error' in result:
                        errors.append(f'Account {i+1} failed: {result.get("error", "Unknown error")}')
                        if 'debug' in result:
                            errors.append(f'Debug info: {result["debug"]}')
                    else:
                        errors.append(f'Failed to create account {i+1} - No response')
                
                # Small delay
                time.sleep(1)
                
            except Exception as e:
                errors.append(f'Error creating account {i+1}: {str(e)}')
        
        generation_id = f"{name}_{region}_{int(time.time())}"
        
        # Store results
        all_results = read_json_file(RESULTS_FILE)
        all_results[generation_id] = {
            'status': 'completed',
            'accounts': accounts,
            'errors': errors,
            'completed': len(accounts),
            'total': count
        }
        write_json_file(RESULTS_FILE, all_results)
        
        return jsonify({
            'success': True,
            'generation_id': generation_id,
            'message': f'Generated {len(accounts)} accounts for region {region}',
            'accounts': accounts,
            'errors': errors,
            'completed': len(accounts),
            'total': count
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

@app.route('/status/<generation_id>', methods=['GET'])
def get_status(generation_id):
    all_results = read_json_file(RESULTS_FILE)
    
    if generation_id not in all_results:
        return jsonify({
            'success': False,
            'error': 'Generation ID not found'
        }), 404
    
    result = all_results[generation_id]
    
    return jsonify({
        'success': True,
        'generation_id': generation_id,
        'status': result['status'],
        'completed': result['completed'],
        'total': result['total'],
        'accounts_count': len(result['accounts']),
        'errors_count': len(result['errors']),
        'accounts': result['accounts'],
        'errors': result['errors']
    })

@app.route('/results/<generation_id>', methods=['GET'])
def get_results(generation_id):
    all_results = read_json_file(RESULTS_FILE)
    
    if generation_id not in all_results:
        return jsonify({
            'success': False,
            'error': 'Results not found for this generation ID'
        }), 404
    
    return jsonify({
        'success': True,
        'generation_id': generation_id,
        'results': all_results[generation_id]
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
        'platform': 'vercel',
        'note': 'Synchronous processing - no background threads'
    })

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'success': True,
        'message': 'Free Fire Account Generator API (Vercel Fixed Version)',
        'platform': 'Vercel Serverless',
        'limitations': [
            'No background threading',
            'Maximum 10 accounts per request',
            'Synchronous processing only',
            'No protobuf dependency'
        ],
        'endpoints': {
            'generate': '/gen?name=FALCON&count=1&region=IND',
            'status': '/status/{generation_id}',
            'results': '/results/{generation_id}',
            'regions': '/regions',
            'health': '/health'
        },
        'example_usage': {
            'generate_accounts': 'GET /gen?name=FALCON&count=5&region=IND'
        }
    })

# Vercel serverless handler
app = app

# For Vercel deployment
def handler(environ, start_response):
    return app(environ, start_response)

# Also export as module variable
application = app
