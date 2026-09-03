from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Table des Utilisateurs (Éleveurs / Vétérinaires)
class Utilisateur(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default='eleveur')
    diagnostics = db.relationship('Diagnostic', backref='auteur', lazy=True)

# Table des Diagnostics enregistrés
class Diagnostic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description_symptomes = db.Column(db.Text, nullable=True)
    maladie_detectee = db.Column(db.String(150), nullable=False)
    niveau_confiance = db.Column(db.String(10), nullable=False)
    gravite = db.Column(db.String(50), nullable=False)
    date_creation = db.Column(db.DateTime, default=datetime.utcnow)
    utilisateur_id = db.Column(db.Integer, db.ForeignKey('utilisateur.id'), nullable=True)