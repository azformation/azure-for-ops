import os
import json
from datetime import datetime
from flask import Blueprint, jsonify, request
from collections import defaultdict

modules_bp = Blueprint('modules', __name__)

def get_data_file_path(filename):
    """Get the full path to a data file"""
    return os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', filename)

def load_json_file(filename):
    """Load data from a JSON file"""
    file_path = get_data_file_path(filename)
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []

def save_json_file(filename, data):
    """Save data to a JSON file"""
    file_path = get_data_file_path(filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

@modules_bp.route('/modules', methods=['GET'])
def get_modules():
    """Get all available modules"""
    try:
        modules = load_json_file('modules.json')
        return jsonify({
            'success': True,
            'data': modules
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_bp.route('/votes', methods=['POST'])
def submit_votes():
    """Submit votes for modules"""
    try:
        data = request.get_json()
        
        if not data or 'votes' not in data:
            return jsonify({
                'success': False,
                'error': 'Invalid data format. Expected {"votes": [...]}'
            }), 400
        
        votes = data['votes']
        
        # Validate votes format
        for vote in votes:
            if not isinstance(vote, dict) or 'moduleId' not in vote or 'priority' not in vote:
                return jsonify({
                    'success': False,
                    'error': 'Invalid vote format. Each vote must have moduleId and priority'
                }), 400
            
            if vote['priority'] not in [1, 2, 3]:
                return jsonify({
                    'success': False,
                    'error': 'Priority must be 1, 2, or 3'
                }), 400
        
        # Load existing votes
        existing_votes = load_json_file('votes.json')
        
        # Add timestamp to each vote
        timestamp = datetime.now().isoformat()
        for vote in votes:
            vote['timestamp'] = timestamp
        
        # Append new votes
        existing_votes.extend(votes)
        
        # Save updated votes
        save_json_file('votes.json', existing_votes)
        
        return jsonify({
            'success': True,
            'message': f'Successfully submitted {len(votes)} votes'
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_bp.route('/results', methods=['GET'])
def get_results():
    """Get aggregated voting results"""
    try:
        # Load modules and votes
        modules = load_json_file('modules.json')
        votes = load_json_file('votes.json')
        
        # Create module lookup
        module_lookup = {module['id']: module for module in modules}
        
        # Aggregate votes by module and priority
        results = defaultdict(lambda: {'priority_1': 0, 'priority_2': 0, 'priority_3': 0, 'total': 0})
        
        for vote in votes:
            module_id = vote['moduleId']
            priority = vote['priority']
            
            if module_id in module_lookup:
                results[module_id][f'priority_{priority}'] += 1
                results[module_id]['total'] += 1
        
        # Format results for frontend
        formatted_results = []
        for module_id, vote_counts in results.items():
            if module_id in module_lookup:
                module_info = module_lookup[module_id]
                formatted_results.append({
                    'moduleId': module_id,
                    'title': module_info['title'],
                    'duration': module_info['duration'],
                    'votes': vote_counts
                })
        
        # Sort by total votes (descending)
        formatted_results.sort(key=lambda x: x['votes']['total'], reverse=True)
        
        # Calculate summary statistics
        total_votes = len(votes)
        total_participants = len(set(vote.get('timestamp', '') for vote in votes))
        
        summary = {
            'totalVotes': total_votes,
            'totalParticipants': total_participants,
            'totalModules': len(modules),
            'modulesWithVotes': len(results)
        }
        
        return jsonify({
            'success': True,
            'data': {
                'results': formatted_results,
                'summary': summary
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_bp.route('/results/chart-data', methods=['GET'])
def get_chart_data():
    """Get data formatted for charts"""
    try:
        # Load modules and votes
        modules = load_json_file('modules.json')
        votes = load_json_file('votes.json')
        
        # Create module lookup
        module_lookup = {module['id']: module for module in modules}
        
        # Aggregate votes by module and priority
        results = defaultdict(lambda: {'priority_1': 0, 'priority_2': 0, 'priority_3': 0, 'total': 0})
        
        for vote in votes:
            module_id = vote['moduleId']
            priority = vote['priority']
            
            if module_id in module_lookup:
                results[module_id][f'priority_{priority}'] += 1
                results[module_id]['total'] += 1
        
        # Format for Chart.js
        labels = []
        priority_1_data = []
        priority_2_data = []
        priority_3_data = []
        total_data = []
        
        # Sort modules by total votes
        sorted_modules = sorted(results.items(), key=lambda x: x[1]['total'], reverse=True)
        
        for module_id, vote_counts in sorted_modules:
            if module_id in module_lookup:
                module_info = module_lookup[module_id]
                labels.append(f"{module_info['title']} ({vote_counts['total']} votes)")
                priority_1_data.append(vote_counts['priority_1'])
                priority_2_data.append(vote_counts['priority_2'])
                priority_3_data.append(vote_counts['priority_3'])
                total_data.append(vote_counts['total'])
        
        chart_data = {
            'labels': labels,
            'datasets': [
                {
                    'label': 'Priorité 1 (Important)',
                    'data': priority_1_data,
                    'backgroundColor': 'rgba(220, 38, 127, 0.8)',
                    'borderColor': 'rgba(220, 38, 127, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Priorité 2 (Moyen)',
                    'data': priority_2_data,
                    'backgroundColor': 'rgba(59, 130, 246, 0.8)',
                    'borderColor': 'rgba(59, 130, 246, 1)',
                    'borderWidth': 1
                },
                {
                    'label': 'Priorité 3 (Découverte)',
                    'data': priority_3_data,
                    'backgroundColor': 'rgba(16, 185, 129, 0.8)',
                    'borderColor': 'rgba(16, 185, 129, 1)',
                    'borderWidth': 1
                }
            ]
        }
        
        return jsonify({
            'success': True,
            'data': chart_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@modules_bp.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'message': 'API is running',
        'timestamp': datetime.now().isoformat()
    })

