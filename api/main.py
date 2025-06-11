import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder='static')
CORS(app)

# Liste des participants autorisés
PARTICIPANTS = [
    "Julien.R",
    "Cathy.D", 
    "Az-Eddine.E",
    "Gaëlline.L",
    "Olivier.M",
    "Stéphanie.P",
    "Pierre-Louis.W"
]

# Données des modules
MODULES = [
    {
        "id": "m1_1",
        "title": "Introduction au Cloud Azure",
        "description": "Concepts fondamentaux du cloud computing, les modèles de service (IaaS, PaaS, SaaS) et les avantages d'Azure.",
        "duration": "4 heures"
    },
    {
        "id": "m1_2", 
        "title": "Panorama des services PaaS Azure",
        "description": "Présentation des principaux services PaaS d'Azure : App Service, Azure SQL Database, Azure Storage, Azure Functions, etc.",
        "duration": "5 heures"
    },
    {
        "id": "m1_3",
        "title": "Mise en place d'un environnement de démonstration", 
        "description": "Création et configuration d'un environnement Azure pour les démonstrations pratiques.",
        "duration": "4 heures"
    },
    {
        "id": "m1_4",
        "title": "Gestion des environnements multiples",
        "description": "Stratégies et outils pour gérer efficacement plusieurs environnements (développement, test, production) sur Azure.",
        "duration": "4 heures"
    },
    {
        "id": "m2_1",
        "title": "Gestion des identités et des accès (RBAC)",
        "description": "Mise en œuvre du contrôle d'accès basé sur les rôles (RBAC) pour sécuriser les ressources Azure.",
        "duration": "5 heures"
    },
    {
        "id": "m2_2",
        "title": "Sécurisation des secrets avec Azure Key Vault",
        "description": "Utilisation d'Azure Key Vault pour stocker et gérer de manière sécurisée les clés, secrets et certificats.",
        "duration": "4 heures"
    },
    {
        "id": "m2_3",
        "title": "Gouvernance et conformité avec Azure Policy",
        "description": "Application des politiques Azure pour assurer la conformité et la gouvernance des ressources.",
        "duration": "4 heures"
    },
    {
        "id": "m2_4",
        "title": "Audit et surveillance des accès",
        "description": "Mise en place de l'audit et de la surveillance pour suivre les activités et les accès aux ressources Azure.",
        "duration": "4 heures"
    },
    {
        "id": "m2_5",
        "title": "Intégration avec Azure AD Connect",
        "description": "Synchronisation des identités entre l'Active Directory on-premise et Azure Active Directory.",
        "duration": "4 heures"
    },
    {
        "id": "m3_1",
        "title": "Monitoring et alertes avec Azure Monitor",
        "description": "Utilisation d'Azure Monitor pour collecter, analyser et agir sur les données de télémétrie de vos environnements Azure.",
        "duration": "5 heures"
    },
    {
        "id": "m3_2",
        "title": "Analyse des logs avec KQL",
        "description": "Apprentissage du langage de requête Kusto (KQL) pour interroger les logs dans Azure Log Analytics.",
        "duration": "5 heures"
    },
    {
        "id": "m3_3",
        "title": "Création de tableaux de bord personnalisés",
        "description": "Conception et implémentation de tableaux de bord Azure pour visualiser les métriques et les logs clés.",
        "duration": "4 heures"
    },
    {
        "id": "m3_4",
        "title": "Optimisation des coûts Azure",
        "description": "Stratégies et outils pour analyser et optimiser les dépenses liées à l'utilisation des services Azure.",
        "duration": "4 heures"
    },
    {
        "id": "m4_1",
        "title": "Déploiement Continu avec Azure DevOps",
        "description": "Intégration d'Azure DevOps dans les projets Azure PaaS pour automatiser les déploiements et améliorer la qualité du code.",
        "duration": "7 heures"
    },
    {
        "id": "m4_2",
        "title": "Infrastructure as Code (IaC) avec ARM Templates et Bicep",
        "description": "Principes de l'Infrastructure as Code et l'utilisation d'ARM Templates et Bicep pour déployer des infrastructures Azure reproductibles.",
        "duration": "8 heures"
    },
    {
        "id": "m4_3",
        "title": "Fonctions Serverless et Logic Apps",
        "description": "Développement serverless sur Azure avec Azure Functions et l'automatisation des workflows avec Logic Apps.",
        "duration": "8 heures"
    },
    {
        "id": "m5_1",
        "title": "Azure Virtual Networks (VNets)",
        "description": "Configuration et gestion des réseaux virtuels Azure pour sécuriser et optimiser les services PaaS.",
        "duration": "8 heures"
    }
]

# Fichier de stockage des votes
VOTES_FILE = 'data/votes.json'

def load_votes():
    """Charge les votes depuis le fichier JSON"""
    if os.path.exists(VOTES_FILE):
        with open(VOTES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_votes(votes):
    """Sauvegarde les votes dans le fichier JSON"""
    os.makedirs(os.path.dirname(VOTES_FILE), exist_ok=True)
    with open(VOTES_FILE, 'w', encoding='utf-8') as f:
        json.dump(votes, f, ensure_ascii=False, indent=2)

@app.route('/')
def index():
    """Sert la page principale"""
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_files(path):
    """Sert les fichiers statiques"""
    return send_from_directory(app.static_folder, path)

@app.route('/api/health')
def health():
    """Point de santé de l'API"""
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route('/api/participants')
def get_participants():
    """Retourne la liste des participants"""
    return jsonify(PARTICIPANTS)

@app.route('/api/modules')
def get_modules():
    """Retourne la liste des modules"""
    return jsonify(MODULES)

@app.route('/api/votes/<participant>', methods=['GET'])
def get_participant_votes(participant):
    """Retourne les votes d'un participant spécifique"""
    if participant not in PARTICIPANTS:
        return jsonify({"error": "Participant non autorisé"}), 400
    
    votes = load_votes()
    participant_votes = votes.get(participant, {})
    return jsonify(participant_votes.get('votes', {}))

@app.route('/api/votes', methods=['POST'])
def submit_votes():
    """Soumet les votes d'un participant"""
    try:
        data = request.get_json()
        participant = data.get('participant')
        votes = data.get('votes', {})
        
        if not participant:
            return jsonify({"error": "Participant requis"}), 400
            
        if participant not in PARTICIPANTS:
            return jsonify({"error": "Participant non autorisé"}), 400
        
        if not votes:
            return jsonify({"error": "Aucun vote fourni"}), 400
        
        # Charge les votes existants
        all_votes = load_votes()
        
        # Met à jour ou ajoute les votes du participant
        all_votes[participant] = {
            "timestamp": datetime.now().isoformat(),
            "votes": votes
        }
        
        # Sauvegarde
        save_votes(all_votes)
        
        return jsonify({"message": "Votes enregistrés avec succès", "count": len(votes)})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/votes/<participant>', methods=['DELETE'])
def reset_participant_votes(participant):
    """Réinitialise les votes d'un participant"""
    try:
        if participant not in PARTICIPANTS:
            return jsonify({"error": "Participant non autorisé"}), 400
        
        # Charge les votes existants
        all_votes = load_votes()
        
        # Supprime les votes du participant
        if participant in all_votes:
            del all_votes[participant]
            save_votes(all_votes)
            return jsonify({"message": "Votes réinitialisés avec succès"})
        else:
            return jsonify({"message": "Aucun vote à réinitialiser"})
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/results')
def get_results():
    """Retourne les résultats du sondage"""
    try:
        votes = load_votes()
        
        # Calcule les statistiques
        total_participants = len(votes)
        modules_voted = set()
        priority_counts = {1: 0, 2: 0, 3: 0}
        module_stats = {}
        participant_details = []
        
        for participant, vote_data in votes.items():
            participant_votes = vote_data.get('votes', {})
            vote_count = len(participant_votes)
            
            participant_details.append({
                'participant': participant,
                'vote_count': vote_count,
                'timestamp': vote_data.get('timestamp', '')
            })
            
            for module_id, priority in participant_votes.items():
                modules_voted.add(module_id)
                priority_counts[priority] += 1
                
                if module_id not in module_stats:
                    module_stats[module_id] = {1: 0, 2: 0, 3: 0}
                module_stats[module_id][priority] += 1
        
        # Prépare les données pour les graphiques
        chart_data = []
        for module in MODULES:
            module_id = module['id']
            stats = module_stats.get(module_id, {1: 0, 2: 0, 3: 0})
            total_votes = stats[1] + stats[2] + stats[3]
            
            if total_votes > 0:  # Seulement les modules avec des votes
                chart_data.append({
                    'module': module['title'][:30] + '...' if len(module['title']) > 30 else module['title'],
                    'priority_1': stats[1],
                    'priority_2': stats[2], 
                    'priority_3': stats[3],
                    'total': total_votes
                })
        
        # Données pour le graphique circulaire
        total_priority_votes = sum(priority_counts.values())
        pie_data = []
        if total_priority_votes > 0:
            pie_data = [
                {'name': 'Priorité 1 (Important)', 'value': priority_counts[1], 'color': '#dc2626'},
                {'name': 'Priorité 2 (Moyen)', 'value': priority_counts[2], 'color': '#2563eb'},
                {'name': 'Priorité 3 (Découverte)', 'value': priority_counts[3], 'color': '#16a34a'}
            ]
        
        # Données détaillées pour le tableau
        detailed_data = []
        for module in MODULES:
            module_id = module['id']
            stats = module_stats.get(module_id, {1: 0, 2: 0, 3: 0})
            total_module_votes = stats[1] + stats[2] + stats[3]
            
            if total_module_votes > 0:  # Seulement les modules avec des votes
                detailed_data.append({
                    'module': module['title'],
                    'duration': module['duration'],
                    'priority_1': stats[1],
                    'priority_2': stats[2],
                    'priority_3': stats[3],
                    'total': total_module_votes
                })
        
        return jsonify({
            'summary': {
                'total_votes': sum(priority_counts.values()),
                'participants': total_participants,
                'modules_voted': len(modules_voted),
                'total_modules': len(MODULES)
            },
            'chart_data': chart_data,
            'pie_data': pie_data,
            'detailed_data': detailed_data,
            'participant_details': participant_details
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

