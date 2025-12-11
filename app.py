import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION DU DESIGN ---
st.set_page_config(page_title="Stratégie & Patrimoine", page_icon="🏦", layout="wide")

# CSS pour un look moderne
st.markdown("""
<style>
    .main {background-color: #0e1117;}
    h1 {color: #ffffff; font-family: 'Helvetica Neue', sans-serif;}
    h2 {color: #e0e0e0; font-weight: 300;}
    h3 {color: #4da6ff;}
    .stButton>button {
        background-color: #4da6ff; color: white; border-radius: 8px; height: 50px; width: 100%; border: none; font-weight: bold;
    }
    .stButton>button:hover {background-color: #0066cc;}
    .parrainage-box {
        background-color: #1f2937; padding: 20px; border-radius: 10px; border-left: 5px solid #ffd700; margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# --- DONNÉES DE PARRAINAGE ---
PARRAINAGE = {
    "BoursoBank": {"code": "GASA8477", "montant": "80€ à 150€", "desc": "La banque la moins chère (PEA, Comptes)"},
    "Fortuneo": {"code": "13528376", "montant": "80€ à 130€", "desc": "Idéal pour l'Assurance Vie et la Gold Mastercard"}
}

# --- LOGIQUE FINANCIÈRE ---
def obtenir_profil_et_conseils(score, horizon):
    # Définition du profil avec clés simplifiées pour éviter le crash
    if score < 25:
        profil = "Trouillard 🛡️"
        desc = "La sécurité avant tout. Vous dormez mal si votre argent fluctue."
        # Clés simples : Securite, Immobilier, Bourse, Crypto
        alloc = {"Securite": 90, "Immobilier": 10, "Bourse": 0, "Crypto": 0}
    elif score < 50:
        profil = "Pépère 🛋️"
        desc = "Un équilibre sain. Vous voulez battre l'inflation sans trop de risques."
        alloc = {"Securite": 50, "Immobilier": 30, "Bourse": 15, "Crypto": 5}
    elif score < 75:
        profil = "Ambitieux 🚀"
        desc = "Vous visez la performance long terme et acceptez la volatilité."
        alloc = {"Securite": 20, "Immobilier": 20, "Bourse": 50, "Crypto": 10}
    else:
        profil = "Tête Brûlée 🔥"
        desc = "Le risque est votre ami. Vous cherchez le rendement maximal."
        alloc = {"Securite": 10, "Immobilier": 10, "Bourse": 50, "Crypto": 30}

    # Conseils produits détaillés
    conseils = []
    
    # 1. Épargne de précaution
    conseils.append("**💰 Épargne de sécurité :** Remplissez Livret A et LDDS avant tout.")
    
    # 2. Enveloppes Fiscales (Bourse)
    # C'est ici que ça plantait avant, maintenant "Bourse" existe tout le temps
    if alloc["Bourse"] > 0:
        if horizon >= 5:
            conseils.append(f"**📈 Bourse ({alloc['Bourse']}%):** Ouvrez un **PEA** (Fiscalité douce après 5 ans). Investissez dans des **ETF MSCI World**.")
        else:
            conseils.append(f"**📈 Bourse ({alloc['Bourse']}%):** Privilégiez un **CTO** ou une Assurance Vie.")

    # 3. Immobilier
    if alloc["Immobilier"] > 0:
        if score > 60:
            conseils.append(f"**🏢 Immobilier ({alloc['Immobilier']}%):** Regardez le **Crowdfunding Immobilier**.")
        else:
            conseils.append(f"**🏢 Immobilier ({alloc['Immobilier']}%):** Privilégiez les **SCPI** (Pierre-Papier) en Assurance Vie.")

    # 4. Crypto
    if alloc["Crypto"] > 0:
        details = "Bitcoin (BTC) uniquement" if score < 80 else "BTC, ETH et Solana"
        conseils.append(f"**⚡ Cryptomonnaies ({alloc['Crypto']}%):** {details}. Attention, c'est volatil.")

    conseils.append("**💼 Le Couteau Suisse :** Ouvrez une bonne **Assurance Vie** en ligne (frais < 0.6%).")

    return profil, desc, alloc, conseils

# --- GÉNÉRATION PDF ---
def generer_pdf(nom, profil, desc, alloc, conseils):
    pdf = FPDF()
    pdf.add_page()
    
    def txt(t): return t.encode('latin-1', 'replace').decode('latin-1')
    
    # Header
    pdf.set_font("Arial", 'B', 20)
    pdf.set_text_color(33, 37, 41)
    pdf.cell(0, 15, txt("Bilan Patrimonial & Stratégie"), 0, 1, 'C')
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, txt(f"Généré le {datetime.now().strftime('%d/%m/%Y')}"), 0, 1, 'C')
    pdf.ln(5)

    # Profil
    pdf.set_fill_color(240, 240, 240)
    pdf.rect(10, 35, 190, 30, 'F')
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 102, 204)
    pdf.set_xy(15, 40)
    pdf.cell(0, 10, txt(f"Votre Profil : {profil}"), 0, 1)
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 0, 0)
    pdf.set_xy(15, 50)
    pdf.multi_cell(180, 5, txt(desc))
    
    pdf.set_y(75)

    # Offres Parrainage
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("🎁 VOS OFFRES DE BIENVENUE"), 0, 1, 'L')
    
    pdf.set_font("Arial", '', 11)
    y_pos = pdf.get_y()
    
    # Boite Bourso
    pdf.set_fill_color(255, 245, 245)
    pdf.rect(10, y_pos, 90, 35, 'F')
    pdf.set_xy(15, y_pos+5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 5, txt(f"BoursoBank (PEA/Banque)"), 0, 1)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(200, 0, 0)
    pdf.set_xy(15, y_pos+12)
    pdf.cell(80, 5, txt(f"CODE : {PARRAINAGE['BoursoBank']['code']}"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    # Boite Fortuneo
    pdf.set_fill_color(245, 255, 245)
    pdf.rect(105, y_pos, 90, 35, 'F')
    pdf.set_xy(110, y_pos+5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 5, txt(f"Fortuneo (Assurance Vie)"), 0, 1)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 150, 0)
    pdf.set_xy(110, y_pos+12)
    pdf.cell(80, 5, txt(f"CODE : {PARRAINAGE['Fortuneo']['code']}"), 0, 1)
    pdf.set_text_color(0, 0, 0)

    pdf.ln(40)

    # Allocation & Conseils
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("Allocation & Conseils"), 0, 1)
    pdf.set_font("Arial", '', 10)
    
    for k, v in alloc.items():
        if v > 0:
            pdf.cell(50, 8, txt(f"{k} : {v}%"), 1, 1)

    pdf.ln(5)
    for cons in conseils:
        clean = cons.replace("**", "")
        pdf.multi_cell(0, 6, txt(f"- {clean}"))
        pdf.ln(1)

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE ---
col_title, col_logo = st.columns([4,1])
with col_title:
    st.title("🎯 Définissez votre profil d'investisseur")

st.write("---")

c1, c2, c3 = st.columns(3)
with c1: horizon = st.slider("Horizon (Années)", 1, 35, 10)
with c2: risk_tol = st.slider("Risque (1 à 10)", 1, 10, 5)
with c3: montant = st.number_input("Montant (€)", 500, 1000000, 10000)

connaissance = st.radio("Niveau", ["Débutant", "Intermédiaire", "Expert"], horizontal=True)

# Calcul Score
score_risk = risk_tol * 6
score_horizon = 20 if horizon > 8 else (10 if horizon > 4 else 0)
score_know = 0 if connaissance == "Débutant" else (10 if connaissance == "Intermédiaire" else 20)
total_score = score_risk + score_horizon + score_know

if st.button("📊 Analyser mon profil", type="primary"):
    profil, desc, alloc, conseils = obtenir_profil_et_conseils(total_score, horizon)
    
    st.divider()
    res_c1, res_c2 = st.columns([2, 1])
    
    with res_c1:
        st.subheader(f"Profil : {profil}")
        st.info(desc)
        for c in conseils: st.markdown(f"- {c}")

    with res_c2:
        labels = [k for k,v in alloc.items() if v > 0]
        values = [v for k,v in alloc.items() if v > 0]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
        fig.update_layout(margin=dict(t=0,b=0,l=0,r=0), height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

    # Parrainage
    st.markdown("### 🎁 Vos Avantages")
    pc1, pc2 = st.columns(2)
    with pc1:
        st.info(f"**BoursoBank**\n\nCode: **{PARRAINAGE['BoursoBank']['code']}**\n\n{PARRAINAGE['BoursoBank']['desc']}")
    with pc2:
        st.success(f"**Fortuneo**\n\nCode: **{PARRAINAGE['Fortuneo']['code']}**\n\n{PARRAINAGE['Fortuneo']['desc']}")

    pdf_bytes = generer_pdf("Inv", profil, desc, alloc, conseils)
    st.download_button("📥 Télécharger PDF", data=pdf_bytes, file_name="bilan.pdf", mime="application/pdf")
