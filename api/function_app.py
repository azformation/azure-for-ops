import azure.functions as func
import json
import os
from datetime import datetime

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

app = func.FunctionApp()

# Stockage en mémoire pour les votes (dans un vrai déploiement, utiliser Azure Storage)
votes_storage = {}

@app.route(route="health", methods=["GET"])
def health(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps({"status": "healthy", "timestamp": datetime.now().isoformat()}),
        mimetype="application/json"
    )

@app.route(route="participants", methods=["GET"])
def get_participants(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(PARTICIPANTS),
        mimetype="application/json"
    )

@app.route(route="modules", methods=["GET"])
def get_modules(req: func.HttpRequest) -> func.HttpResponse:
    return func.HttpResponse(
        json.dumps(MODULES),
        mimetype="application/json"
    )

@app.route(route="votes/{participant}", methods=["GET"])
def get_participant_votes(req: func.HttpRequest) -> func.HttpResponse:
    participant = req.route_params.get('participant')
    
    if participant not in PARTICIPANTS:
        return func.HttpResponse(
            json.dumps({"error": "Participant non autorisé"}),
            status_code=400,
            mimetype="application/json"
        )
    
    participant_votes = votes_storage.get(participant, {})
    return func.HttpResponse(
        json.dumps(participant_votes.get('votes', {})),
        mimetype="application/json"
    )

@app.route(route="votes", methods=["POST"])
def submit_votes(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        participant = req_body.get('participant')
        votes = req_body.get('votes', {})
        
        if not participant:
            return func.HttpResponse(
                json.dumps({"error": "Participant requis"}),
                status_code=400,
                mimetype="application/json"
            )
            
        if participant not in PARTICIPANTS:
            return func.HttpResponse(
                json.dumps({"error": "Participant non autorisé"}),
                status_code=400,
                mimetype="application/json"
            )
        
        if not votes:
            return func.HttpResponse(
                json.dumps({"error": "Aucun vote fourni"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Met à jour ou ajoute les votes du participant
        votes_storage[participant] = {
            "timestamp": datetime.now().isoformat(),
            "votes": votes
        }
        
        return func.HttpResponse(
            json.dumps({"message": "Votes enregistrés avec succès", "count": len(votes)}),
            mimetype="application/json"
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="votes/{participant}", methods=["DELETE"])
def reset_participant_votes(req: func.HttpRequest) -> func.HttpResponse:
    try:
        participant = req.route_params.get('participant')
        
        if participant not in PARTICIPANTS:
            return func.HttpResponse(
                json.dumps({"error": "Participant non autorisé"}),
                status_code=400,
                mimetype="application/json"
            )
        
        # Supprime les votes du participant
        if participant in votes_storage:
            del votes_storage[participant]
            return func.HttpResponse(
                json.dumps({"message": "Votes réinitialisés avec succès"}),
                mimetype="application/json"
            )
        else:
            return func.HttpResponse(
                json.dumps({"message": "Aucun vote à réinitialiser"}),
                mimetype="application/json"
            )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

@app.route(route="results", methods=["GET"])
def get_results(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Calcule les statistiques
        total_participants = len(votes_storage)
        modules_voted = set()
        priority_counts = {1: 0, 2: 0, 3: 0}
        module_stats = {}
        participant_details = []
        
        for participant, vote_data in votes_storage.items():
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
        
        results = {
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
        }
        
        return func.HttpResponse(
            json.dumps(results),
            mimetype="application/json"
        )
    
    except Exception as e:
        return func.HttpResponse(
            json.dumps({"error": str(e)}),
            status_code=500,
            mimetype="application/json"
        )

