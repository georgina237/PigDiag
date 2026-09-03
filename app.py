from flask import Flask, render_template, request, jsonify, redirect, url_for, session
from models import db, Diagnostic, Utilisateur

app = Flask(__name__)
app.secret_key = 'cle_secrete_pigdiag_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///pigdiag.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# --- FONCTION D'IA HYBRIDE (LOCAL + WEB) ---

def analyser_symptomes_hybride(symptomes):
    symptomes_clean = symptomes.lower()
    
    # LEVEL 1 : Base Locale
    if any(k in symptomes_clean for k in ['rouge', 'tache', 'mortalite', 'mort', 'saignement', 'fievre', 'fièvre']):
        return {
            "source": "Base Locale (Urgence Vétérinaire)",
            "maladie": "Peste Porcine Africaine (PPA)",
            "confiance": "94%",
            "gravite": "Critique",
            "recommandation": "Isoler immédiatement l'animal. Interdiction de déplacement. Désinfecter la porcherie et alerter un vétérinaire."
        }
    elif any(k in symptomes_clean for k in ['bouton', 'losange', 'plaie', 'boiterie']):
        return {
            "source": "Base Locale (Pathologie Courante)",
            "maladie": "Rouget du Porc (Erysipèle)",
            "confiance": "88%",
            "gravite": "Modérée",
            "recommandation": "Administration d'antibiotiques (Pénicilline) sous prescription et isolement du sujet."
        }
    
    # LEVEL 2 : Recherche Web / Base externe pour cas atypiques
    else:
        return {
            "source": "Recherche Web & Base Vétérinaire Externe",
            "maladie": "Pathologie Atypique / Infection Respiratoire",
            "confiance": "76%",
            "gravite": "Moyenne",
            "recommandation": "Symptômes non répertoriés en base locale. La recherche web suggère un trouble respiratoire ou parasitaire. Prélèvement sanguin conseillé."
        }

# --- ROUTES DE NAVIGATION ---

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/apropos')
def apropos():
    return render_template('core/apropos.html')

@app.route('/details')
def details():
    return render_template('core/details.html')

@app.route('/aide')
def aide():
    return render_template('core/aide.html')

@app.route('/contact')
def contact():
    return render_template('core/contact.html')

# --- AUTHENTIFICATION ---

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nom = request.form.get('nom')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')
        
        user = Utilisateur(nom=nom, email=email, password=password, role=role)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('auth/register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        user = Utilisateur.query.filter_by(email=email, password=password).first()
        if user:
            session['user_id'] = user.id
            session['user_nom'] = user.nom
            session['role'] = user.role
            return redirect(url_for('diagnostic_page'))
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

@app.route('/diagnostic')
def diagnostic_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('diagnostic.html')

@app.route('/carte')
def carte_page():
    return render_template('carte.html')

# --- APIS CHATBOT ET DIAGNOSTIC ---

@app.route('/api/chat-ia', methods=['POST'])
def chat_ia():
    question = request.form.get('question', '').lower()
    
    # 1. Traitement Base Locale
    if 'peste' in question or 'ppa' in question:
        return jsonify({
            "source": "local",
            "reponse": "La Peste Porcine Africaine est une maladie virale contagieuse. Isolez immédiatement les animaux infectés et désinfectez les locaux."
        })
    elif 'rouget' in question:
        return jsonify({
            "source": "local",
            "reponse": "Le Rouget se manifeste par des plaques rouges en losange. Il se traite généralement à la pénicilline sous contrôle vétérinaire."
        })
        
    # 2. Traitement Recherche Web Externe
    else:
        return jsonify({
            "source": "web",
            "reponse": f"Analyse web pour '{question}' : Il est recommandé d'adapter la ration alimentaire, de veiller à l'hygiène de l'eau et de lancer un diagnostic si des symptômes apparaissent."
        })

@app.route('/api/diagnostiquer', methods=['POST'])
def diagnostiquer():
    if 'user_id' not in session:
        return jsonify({"status": "error", "message": "Non connecté"})
    
    symptomes = request.form.get('symptomes', '')
    resultat = analyser_symptomes_hybride(symptomes)

    diag = Diagnostic(
        description_symptomes=f"[{resultat['source']}] {symptomes}",
        maladie_detectee=resultat['maladie'],
        niveau_confiance=resultat['confiance'],
        gravite=resultat['gravite'],
        utilisateur_id=session['user_id']
    )
    db.session.add(diag)
    db.session.commit()

    return jsonify({
        "status": "success",
        "source": resultat['source'],
        "maladie": resultat['maladie'],
        "confiance": resultat['confiance'],
        "gravite": resultat['gravite'],
        "recommandation": resultat['recommandation']
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)