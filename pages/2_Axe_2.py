import streamlit as st
import plotly.express as px
import pandas as pd
from analysis.axe_2 import filter_axis, main_table, AXIS_FILTER

st.set_page_config(page_title="Axe 2 : Freins et confiance", layout="wide")
st.title("Axe 2 : Freins et confiance")

# --- CHARGEMENT DES VRAIES DONNÉES ---
@st.cache_data
def load_real_data():
    # On charge le fichier que vous avez dans le dossier data/
    df = pd.read_csv("data/survey_2026_results.csv")
    return df

df = load_real_data()

# --- FILTRES ---
# On récupère les âges disponibles dans le vrai jeu de données
if AXIS_FILTER in df.columns:
    age_options = df[AXIS_FILTER].dropna().unique().tolist()
    selected_ages = st.sidebar.multiselect("Filtrer par âge", age_options, default=age_options[:3])
    df_filtered = filter_axis(df, selected_ages)
else:
    st.warning(f"La colonne {AXIS_FILTER} n'existe pas dans les données.")
    df_filtered = df

# --- ONGLETS ---
tab_constat, tab_explorer, tab_donnees = st.tabs(["Le constat", "Explorer", "Données"])

with tab_constat:
    st.header("Le constat")
    
    # Effectif minimal (on met 50 car on a de vraies données)
    if len(df_filtered) < 50:
        st.warning(f"Effectif trop faible ({len(df_filtered)} répondants) pour afficher une figure fiable.")
        st.stop()
        
    st.write(f"Nombre de répondants après filtre : **{len(df_filtered)}**")
    
    # On teste la fonction du professeur
    try:
        table_principale = main_table(df_filtered)
        st.write("### Répartition de l'évitement de l'IA")
        st.dataframe(table_principale)
        
        # On fait un graphique Plotly si la table a au moins 2 colonnes
        if len(table_principale.columns) >= 2:
            fig = px.bar(
                table_principale, 
                x=table_principale.columns[0], 
                y=table_principale.columns[1],
                title="Répartition de l'AIAvoid",
                color=table_principale.columns[0]
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erreur avec la fonction du professeur : {e}")
        st.write("Voici un aperçu des données brutes pour comprendre :")
        st.dataframe(df_filtered[[AXIS_FILTER, "AIAvoid"]].head(20))

with tab_explorer:
    st.header("Explorer")
    st.write(f"Effectif total filtré : {len(df_filtered)}")
    
    # Un petit graphique d'exploration avec Plotly
    if "AITrust" in df.columns:
        fig2 = px.histogram(df_filtered, x="AITrust", title="Distribution de la confiance en l'IA")
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("La colonne AITrust n'est pas disponible pour l'exploration.")

with tab_donnees:
    st.header("Données")
    st.dataframe(df_filtered.head(100))