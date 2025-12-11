import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- CONFIGURATION DU DESIGN ---
st.set_page_config(page_title="Stratégie & Patrimoine", page_icon="🏦", layout="wide")

# CSS pour un look moderne et sobre (Dark mode friendly)
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
# Note: Les montants varient, j'indique des fourchettes attractives standards
PARRAINAGE = {
    "BoursoBank": {"code": "GASA8477", "montant": "80€ à 150€", "desc": "La banque la moins chère (PEA, Comptes)"},
    "Fortuneo": {"code": "13528376", "montant": "80€ à 130€", "desc": "Idéal pour l'Assurance Vie et la Gold Mastercard"}
}

# --- LOGIQUE FINANCIÈRE ---
def obtenir_profil_et_conseils(score, horizon):
    # Définition du profil
    if score < 25:
        profil = "Trouillard 🛡️"
        desc = "La sécurité avant tout. Vous dormez mal si votre argent fluctue."
        alloc = {"Securité (Livrets/Fonds €)": 90, "Immobilier (SCPI)": 10, "Bourse": 0, "Crypto": 0}
    elif score < 50:
        profil = "Pépère 🛋️"
        desc = "Un équilibre sain. Vous voulez battre l'inflation sans trop de risques."
        alloc = {"Securité": 50, "Immobilier": 30, "Bourse (ETF World)": 15, "Crypto": 5}
    elif score < 75:
        profil = "Ambitieux 🚀"
        desc = "Vous visez la performance long terme et acceptez la volatilité."
        alloc = {"Securité": 20, "Immobilier": 20, "Bourse (Actions/ETF)": 50, "Crypto": 10}
    else:
        profil = "Tête Brûlée 🔥"
        desc = "Le risque est votre ami. Vous cherchez le rendement maximal."
        alloc = {"Securité": 10, "Immobilier": 10, "Bourse (Tech/Levier)": 50, "Crypto": 30}

    # Conseils produits détaillés
    conseils = []
    
    # 1. Épargne de précaution (Pour tous)
    conseils.append("**💰 Épargne de sécurité :** Remplissez Livret A et LDDS avant tout.")
    
    # 2. Enveloppes Fiscales (Bourse)
    if alloc["Bourse"] > 0:
        if horizon >= 5:
            conseils.append(f"**📈 Bourse ({alloc['Bourse']}%):** Ouvrez un **PEA** (Fiscalité douce après 5 ans). Investissez dans des **ETF MSCI World** (Panier de 1600 entreprises mondiales) pour diluer le risque.")
        else:
            conseils.append(f"**📈 Bourse ({alloc['Bourse']}%):** Privilégiez un **CTO** (Compte Titres) pour la flexibilité ou une Assurance Vie.")

    # 3. Immobilier
    if alloc["Immobilier"] > 0:
        if score > 60:
            conseils.append(f"**🏢 Immobilier ({alloc['Immobilier']}%):** Regardez le **Crowdfunding Immobilier** (Haut rendement court terme) ou l'investissement locatif direct.")
        else:
            conseils.append(f"**🏢 Immobilier ({alloc['Immobilier']}%):** Privilégiez les **SCPI** (Pierre-Papier) au sein d'une Assurance Vie pour éviter les soucis de gestion.")

    # 4. Crypto
    if alloc["Crypto"] > 0:
        details = "Bitcoin (BTC) et Ethereum (ETH) uniquement" if score < 80 else "BTC, ETH et Altcoins majeurs (Solana, etc.)"
        conseils.append(f"**⚡ Cryptomonnaies ({alloc['Crypto']}%):** {details}. Attention, c'est très volatil. À stocker sur clé Ledger ou plateforme sécurisée.")

    # 5. Assurance Vie (Couteau suisse)
    conseils.append("**💼 Le Couteau Suisse :** Ouvrez une bonne **Assurance Vie** en ligne (frais < 0.6%) pour faire cohabiter Fonds Euros garantis et Unités de Compte.")

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

    # Offres Parrainage (Mise en avant)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("🎁 VOS OFFRES DE BIENVENUE (Ouvrez vos comptes ici)"), 0, 1, 'L')
    
    pdf.set_font("Arial", '', 11)
    y_pos = pdf.get_y()
    
    # Boite Bourso
    pdf.set_fill_color(255, 245, 245) # Rose très pâle
    pdf.rect(10, y_pos, 90, 35, 'F')
    pdf.set_xy(15, y_pos+5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 5, txt(f"BoursoBank (Pour le PEA/Compte)"), 0, 1)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(200, 0, 0)
    pdf.set_xy(15, y_pos+12)
    pdf.cell(80, 5, txt(f"CODE : {PARRAINAGE['BoursoBank']['code']}"), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_xy(15, y_pos+19)
    pdf.cell(80, 5, txt(f"Jusqu'à {PARRAINAGE['BoursoBank']['montant']} offerts"), 0, 1)

    # Boite Fortuneo
    pdf.set_fill_color(245, 255, 245) # Vert très pâle
    pdf.rect(105, y_pos, 90, 35, 'F')
    pdf.set_xy(110, y_pos+5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(80, 5, txt(f"Fortuneo (Pour l'Assurance Vie)"), 0, 1)
    pdf.set_font("Arial", 'B', 11)
    pdf.set_text_color(0, 150, 0)
    pdf.set_xy(110, y_pos+12)
    pdf.cell(80, 5, txt(f"CODE : {PARRAINAGE['Fortuneo']['code']}"), 0, 1)
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", 'I', 9)
    pdf.set_xy(110, y_pos+19)
    pdf.cell(80, 5, txt(f"Jusqu'à {PARRAINAGE['Fortuneo']['montant']} offerts"), 0, 1)

    pdf.ln(30)

    # Allocation
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("Répartition ciblée"), 0, 1)
    pdf.set_font("Arial", '', 11)
    for k, v in alloc.items():
        if v > 0:
            pdf.cell(100, 8, txt(f"- {k}"), 1, 0)
            pdf.cell(20, 8, f"{v}%", 1, 1, 'C')

    pdf.ln(10)

    # Conseils Stratégiques
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("Stratégie détaillée"), 0, 1)
    pdf.set_font("Arial", '', 10)
    for cons in conseils:
        clean_cons = cons.replace("**", "").replace(":", " :") # Nettoyage markdown simple
        pdf.multi_cell(0, 6, txt(f"- {clean_cons}"))
        pdf.ln(2)

    return pdf.output(dest='S').encode('latin-1')

# --- INTERFACE UTILISATEUR ---

col_title, col_logo = st.columns([4,1])
with col_title:
    st.title("🎯 Définissez votre profil d'investisseur")
    st.markdown("Analyse algorithmique, recommandations d'enveloppes (PEA, AV) et optimisation des frais.")

st.write("---")

# 1. Inputs
c1, c2, c3 = st.columns(3)
with c1:
    horizon = st.slider("Horizon de placement (Années)", 1, 35, 10)
with c2:
    risk_tol = st.slider("Niveau de risque accepté (1 à 10)", 1, 10, 5, help="10 = Je suis prêt à perdre 50% temporairement pour gagner plus.")
with c3:
    montant = st.number_input("Montant à investir (€)", 500, 1000000, 10000, step=500)

connaissance = st.radio("Connaissances financières", ["Débutant (Livret A)", "Intermédiaire (Je connais les ETF)", "Expert (Options, Crypto, Immo)"], horizontal=True)

# Calcul Score
score_risk = risk_tol * 6
score_horizon = 20 if horizon > 8 else (10 if horizon > 4 else 0)
score_know = 0 if "Débutant" in connaissance else (10 if "Intermédiaire" in connaissance else 20)
total_score = score_risk + score_horizon + score_know # Max approx 100

# Bouton Action
if st.button("📊 Analyser mon profil et voir les produits", type="primary"):
    
    st.spinner("Calcul des meilleures allocations...")
    profil, desc, alloc, conseils = obtenir_profil_et_conseils(total_score, horizon)
    
    st.divider()

    # --- RÉSULTATS ---
    res_c1, res_c2 = st.columns([2, 1])
    
    with res_c1:
        st.subheader(f"Vous êtes : {profil}")
        st.info(desc)
        
        st.markdown("### 💡 Vos recommandations personnalisées")
        for c in conseils:
            st.markdown(f"- {c}")

    with res_c2:
        # Graphique Donut
        labels = [k for k,v in alloc.items() if v > 0]
        values = [v for k,v in alloc.items() if v > 0]
        fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.4)])
        fig.update_layout(margin=dict(t=0, b=0, l=0, r=0), height=250, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # Jauge de risque
        fig_g = go.Figure(go.Indicator(
            mode = "gauge+number", value = total_score,
            title = {'text': "Niveau d'audace"},
            gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#4da6ff"}}
        ))
        fig_g.update_layout(height=200, margin=dict(t=30, b=0, l=20, r=20))
        st.plotly_chart(fig_g, use_container_width=True)

    # --- SECTION PARRAINAGE (Mise en avant visuelle) ---
    st.markdown("### 🎁 Optimisez vos frais dès le départ")
    st.markdown("Pour mettre en place cette stratégie, voici les meilleures banques actuelles avec leurs offres de bienvenue.")
    
    pc1, pc2 = st.columns(2)
    with pc1:
        st.markdown(f"""
        <div class="parrainage-box">
            <h3>🏦 BoursoBank</h3>
            <p>{PARRAINAGE['BoursoBank']['desc']}</p>
            <p>Code Parrain : <strong>{PARRAINAGE['BoursoBank']['code']}</strong></p>
            <p style="color:#ffd700">💰 Prime : {PARRAINAGE['BoursoBank']['montant']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with pc2:
        st.markdown(f"""
        <div class="parrainage-box">
            <h3>💳 Fortuneo</h3>
            <p>{PARRAINAGE['Fortuneo']['desc']}</p>
            <p>Code Parrain : <strong>{PARRAINAGE['Fortuneo']['code']}</strong></p>
            <p style="color:#ffd700">💰 Prime : {PARRAINAGE['Fortuneo']['montant']}</p>
        </div>
        """, unsafe_allow_html=True)

    # --- PDF ---
    pdf_bytes = generer_pdf("Investisseur", profil, desc, alloc, conseils)
    st.download_button("📥 Télécharger mon rapport complet (PDF)", data=pdf_bytes, file_name="mon_strategie_investisseur.pdf", mime="application/pdf", type="secondary")

    st.caption("Avertissement : Cette application fournit des simulations à titre éducatif et ne constitue pas un conseil en investissement financier certifié. Les performances passées ne préjugent pas des futures.")