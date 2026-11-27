import streamlit as st
import plotly.express as px
import pandas as pd

# On importe les fonctions de notre analyse
from analysis.axe_2 import filter_axis, main_table

st.set_page_config(page_title="Axe 2 : Freins et confiance", layout="wide")

st.title("Axe 2 : Freins et confiance")

# --- Chargement des données (À adapter) ---
# Normalement, vous devriez avoir un fichier commun qui charge les données 
# de l'enquête (ex: depuis data/). Voici comment faire pour tester :
@st.cache_data
def load_data():
    # Remplacer par la vraie fonction de chargement de votre cours
    # ex: return pd.read_csv("data/stack_overflow.csv")
    data = {
        'Country': ['France', 'Allemagne', 'Royaume-Uni', 'Italie', 'Espagne'],
        'Age': ['18-24', '25-34', '35-44', '18-24', '25-34'],
        'AIAvoid': ['Oui', 'Non', 'Oui', 'Oui', 'Non'],
        'AITrust_Score': [2.8, 3.1, 2.9, 2.7, 3.0],
    }
    return pd.DataFrame(data)

df = load_data()

# --- Barre latérale (Filtres) ---
# On utilise la fonction filter_axis du prof
age_options = df['Age'].unique().tolist()
selected_ages = st.sidebar.multiselect("Filtrer par âge", age_options, default=age_options)

# On applique le filtre
df_filtered = filter_axis(df, selected_ages)

# --- Création des onglets ---
tab_constat, tab_explorer, tab_donnees = st.tabs(["Le constat", "Explorer", "Données"])

with tab_constat:
    st.header("Le constat")
    
    # Effectif minimal
    if len(df_filtered) < 50:
        st.warning("Effectif trop faible pour afficher une figure fiable.")
        st.stop()
        
    # On récupère la table principale calculée par le prof
    try:
        table = main_table(df_filtered)
        st.dataframe(table) # À remplacer par un graphique Plotly
    except Exception as e:
        st.info(f"La table n'a pas pu être générée avec les données de test : {e}")

with tab_explorer:
    st.header("Explorer")
    st.write("Ajoutez vos graphiques interactifs ici.")

with tab_donnees:
    st.header("Données")
    st.dataframe(df_filtered)