import streamlit as st
import plotly.graph_objects as go
from fpdf import FPDF
from datetime import datetime
import re

# --- 1. CONFIGURATION & DESIGN ---
st.set_page_config(page_title="Mon Profil Investisseur", page_icon="💸", layout="centered")

# CSS pour look moderne (Mode Sombre)
st.markdown("""
<style>
    .stApp {background-color: #0e1117;}
    h1 {color: #ffffff; text-align: center;}
    h2 {color: #4da6ff;}
    .big-font {font-size:20px !important;}
    .stRadio > label {font-size: 18px; font-weight: bold; color: #fff;}
    div[data-baseweb="select-custom"] {background-color: #1f2937;}
    .parrain-box {
        padding: 20px; border-radius: 10px; margin-bottom: 20px;
        border: 1px solid #333; box-shadow: 0 4px 6px rgba(0,0,0,0.3);
    }
    .bourso {background-color: #2c0b1e; border-left: 5px solid #d63384;}
    .fortuneo {background-color: #052c18; border-left: 5px solid #28a745;}
</style>
""", unsafe_allow_html=True)

# --- 2. DONNÉES PARRAINAGE ---
PARRAINAGE = {
    "Bourso": {"code": "GASA8477", "prime": "jusqu'à 150€", "desc": "Le top pour le compte courant & PEA (frais mini)."},
    "Fortuneo": {"code": "13528376", "prime": "jusqu'à 130€", "desc": "La meilleure pour l'Assurance Vie et la Carte Gold."}
}

# --- 3. LOGIQUE MÉTIER ---

def nettoyer_texte_pdf(texte):
    # Enlève les emojis et caractères spéciaux pour le PDF (évite les bugs)
    return re.sub(r'[^\w\s,.€%:-]', '', texte)

def calculer_resultats(reponses, montant):
    score = 0
    
    # Q1: Horizon (Temps)
    if "Tout de suite" in reponses['temps']: score += 0
    elif "3-5 ans" in reponses['temps']: score += 4
    elif "10 ans" in reponses['temps']: score += 8
    elif "Retraite" in reponses['temps']: score += 12

    # Q2: Réaction (Psychologie)
    if "Panique" in reponses['reaction']: score += 0
    elif "Inquiet" in reponses['reaction']: score += 3
    elif "Zen" in reponses['reaction']: score += 7
    elif "Solde" in reponses['reaction']: score += 10

    # Q3: Connaissances
    if "Néophyte" in reponses['savoir']: score += 0
    elif "Curieux" in reponses['savoir']: score += 3
    elif "Averti" in reponses['savoir']: score += 6

    # Détermination Profil
    if score < 6:
        profil = "L'Écureuil Prudent 🐿️"
        alloc = {"Securite": 85, "Immobilier": 15, "Bourse": 0, "Crypto": 0}
        desc = "Tu ne veux prendre aucun risque. Ton but est de ne jamais perdre 1€."
    elif score < 14:
        profil = "Le Stratège Équilibré ⚖️"
        alloc = {"Securite": 50, "Immobilier": 30, "Bourse": 20, "Crypto": 0}
        desc = "Tu cherches un rendement correct mais tu veux dormir tranquille."
    elif score < 22:
        profil = "L'Investisseur Ambitieux 🚀"
        alloc = {"Securite": 20, "Immobilier": 20, "Bourse": 50, "Crypto": 10}
        desc = "Tu as du temps devant toi et tu acceptes que ça bouge pour gagner plus."
    else:
        profil = "La Tête Brûlée 🔥"
        alloc = {"Securite": 5, "Immobilier": 10, "Bourse": 55, "Crypto": 30}
        desc = "Le risque ne te fait pas peur. Tu vises la performance maximale."

    # Conseils
    conseils = []
    conseils.append(f"💰 **Épargne de sécurité** : Garde toujours {int(montant*0.1)}€ sur un Livret A dispo.")
    
    if alloc["Bourse"] > 0:
        conseils.append("📈 **Bourse** : Ouvre un **PEA chez BoursoBank**. Achète un ETF 'MSCI World' (c'est un panier de 1600 entreprises mondiales). Ça monte historiquement de 7%/an en moyenne.")
    
    if alloc["Immobilier"] > 0:
        if score < 15:
            conseils.append("🏢 **Immobilier** : Achète des parts de **SCPI** (immobilier papier) via une Assurance Vie Fortuneo. C'est de l'immo sans gérer les locataires.")
        else:
            conseils.append("🏢 **Immobilier** : Tu peux viser le Crowdfunding (prêter aux promoteurs) pour du 9-10% de rendement.")

    if alloc["Crypto"] > 0:
        conseils.append("⚡ **Crypto** : Achète seulement du **Bitcoin (BTC)** et **Ethereum (ETH)**. C'est très risqué, n'y mets que ce que tu es prêt à perdre.")

    return profil, desc, alloc, conseils

# --- 4. GÉNÉRATION PDF ---
def creer_pdf(profil, desc, alloc, conseils):
    pdf = FPDF()
    pdf.add_page()
    
    def txt(t): return t.encode('latin-1', 'replace').decode('latin-1')

    # Titre
    pdf.set_font("Arial", 'B', 24)
    pdf.cell(0, 20, txt("Mon Plan d'Action Financier"), 0, 1, 'C')
    
    # Profil
    pdf.set_fill_color(230, 230, 230)
    pdf.rect(10, 30, 190, 25, 'F')
    pdf.set_y(35)
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(0, 50, 100)
    pdf.cell(0, 10, txt(f"Mon Profil : {nettoyer_texte_pdf(profil)}"), 0, 1, 'C')
    pdf.set_font("Arial", 'I', 11)
    pdf.set_text_color(50, 50, 50)
    pdf.cell(0, 10, txt(nettoyer_texte_pdf(desc)), 0, 1, 'C')

    pdf.ln(15)

    # Parrainage (Gros pavé)
    pdf.set_font("Arial", 'B', 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(0, 10, txt("Où ouvrir mes comptes ? (Codes Parrainage)"), 0, 1)
    
    pdf.set_font("Arial", '', 11)
    # Bourso
    pdf.set_text_color(180, 0, 80)
    pdf.cell(0, 8, txt(f"1. POUR LA BANQUE & BOURSE : BoursoBank"), 0, 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt(f"   CODE : {PARRAINAGE['Bourso']['code']}  ({PARRAINAGE['Bourso']['prime']})"), 0, 1)
    
    # Fortuneo
    pdf.set_font("Arial", '', 11)
    pdf.set_text_color(0, 100, 50)
    pdf.cell(0, 8, txt(f"2. POUR L'ASSURANCE VIE : Fortuneo"), 0, 1)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(0, 8, txt(f"   CODE : {PARRAINAGE['Fortuneo']['code']}  ({PARRAINAGE['Fortuneo']['prime']})"), 0, 1)

    pdf.ln(10)
    pdf.set_text_color(0, 0, 0)

    # Allocation
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("Répartition de mon argent"), 0, 1)
    pdf.set_font("Arial", '', 11)
    for k, v in alloc.items():
        if v > 0: pdf.cell(0, 8, txt(f"- {k} : {v}%"), 0, 1)

    pdf.ln(5)
    
    # Conseils
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, txt("Mes étapes à suivre"), 0, 1)
    pdf.set_font("Arial", '', 10)
    for c in conseils:
        c_clean = nettoyer_texte_pdf(c.replace("**", ""))
        pdf.multi_cell(0, 6, txt(f"- {c_clean}"))
        pdf.ln(2)
        
    return pdf.output(dest='S').encode('latin-1')

# --- 5. INTERFACE UTILISATEUR (QUIZ) ---

st.title("🧙‍♂️ Le Quiz de l'Investisseur")
st.markdown("Réponds à 4 questions simples pour savoir où placer ton argent.")

# Question 1
st.subheader("1. Quand auras-tu besoin de cet argent ?")
q_temps = st.radio("L'horizon de temps est le critère n°1.", 
    ["Tout de suite (Urgence / Vacances)", 
     "D'ici 3-5 ans (Achat Immo / Voiture)", 
     "Dans 10 ans (Projet lointain)", 
     "Pour la retraite (Dans très longtemps)"], 
    label_visibility="collapsed")

st.write("---")

# Question 2
st.subheader("2. Si la bourse s'effondre de -20% demain...")
q_reaction = st.radio("Ta réaction émotionnelle ?", 
    ["😱 Je vends tout immédiatement (Panique)", 
     "😰 Je m'inquiète et je dors mal (Stress)", 
     "🧘 Je ne fais rien, ça remontera (Zen)", 
     "🤑 J'en profite pour acheter en solde (Opportunité)"],
    label_visibility="collapsed")

st.write("---")

# Question 3
st.subheader("3. Ton niveau en finance ?")
q_savoir = st.radio("Sois honnête !", 
    ["👶 Néophyte (Livret A et c'est tout)", 
     "🧐 Curieux (Je lis des articles parfois)", 
     "🧠 Averti (Je sais ce qu'est un ETF ou une Action)"],
    label_visibility="collapsed")

st.write("---")

# Question 4
st.subheader("4. Quel montant souhaites-tu investir ?")
montant = st.number_input("Montant en €", min_value=100, value=5000, step=100)

st.write("")
st.write("")

# Bouton Résultat
if st.button("✨ Découvrir ma stratégie", type="primary"):
    
    # Formatage des réponses pour l'algo
    reponses = {"temps": q_temps, "reaction": q_reaction, "savoir": q_savoir}
    
    # Calcul
    profil, desc, alloc, conseils = calculer_resultats(reponses, montant)
    
    st.divider()
    
    # AFFICHE RÉSULTAT
    st.markdown(f"<h2 style='text-align: center; color: #ffd700;'>🏆 Tu es : {profil}</h2>", unsafe_allow_html=True)
    st.info(desc)
    
    # Graphique Donut simple
    labels = [k for k,v in alloc.items() if v > 0]
    values = [v for k,v in alloc.items() if v > 0]
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5)])
    fig.update_layout(margin=dict(t=10,b=10,l=10,r=10), height=250, showlegend=True, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig, use_container_width=True)
    
    # Conseils texte
    st.subheader("📝 Ton plan d'action")
    for conseil in conseils:
        st.write(conseil)

    st.write("---")
    
    # PARRAINAGE (Mise en forme CSS custom)
    st.subheader("🎁 Pour commencer : Tes bonus")
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="parrain-box bourso">
            <h3>🏦 BoursoBank</h3>
            <p><strong>Code : {PARRAINAGE['Bourso']['code']}</strong></p>
            <p>Prime : {PARRAINAGE['Bourso']['prime']}</p>
            <p style="font-size:12px"><em>{PARRAINAGE['Bourso']['desc']}</em></p>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        st.markdown(f"""
        <div class="parrain-box fortuneo">
            <h3>🍀 Fortuneo</h3>
            <p><strong>Code : {PARRAINAGE['Fortuneo']['code']}</strong></p>
            <p>Prime : {PARRAINAGE['Fortuneo']['prime']}</p>
            <p style="font-size:12px"><em>{PARRAINAGE['Fortuneo']['desc']}</em></p>
        </div>
        """, unsafe_allow_html=True)

    # Bouton PDF
    pdf_data = creer_pdf(profil, desc, alloc, conseils)
    st.download_button("📄 Télécharger mon Bilan PDF", data=pdf_data, file_name="mon_profil_investisseur.pdf", mime="application/pdf")
