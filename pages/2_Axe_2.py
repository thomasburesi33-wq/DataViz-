import streamlit as st
import plotly.express as px
import pandas as pd
from analysis.axe_2 import filter_axis, main_table, AXIS_FILTER

st.set_page_config(page_title="Axe 2 : Freins et confiance", layout="wide")

st.title("Axe 2 : Freins et confiance")
st.markdown("*Pourquoi les développeurs évitent-ils l'IA, et comment cela impacte-t-il la stratégie RSE de la DSI ?*")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_real_data():
    # On charge le fichier des vraies données
    return pd.read_csv("data/survey_2026_results.csv")

df = load_real_data()

# --- FILTRES ---
if AXIS_FILTER in df.columns:
    # On trie les âges pour que ce soit logique
    age_options = sorted(df[AXIS_FILTER].dropna().unique().tolist())
    selected_ages = st.sidebar.multiselect("Filtrer par tranche d'âge", age_options, default=age_options)
    df_filtered = filter_axis(df, selected_ages)
else:
    st.sidebar.warning(f"Colonne {AXIS_FILTER} introuvable.")
    df_filtered = df

# --- ONGLETS ---
tab_constat, tab_explorer, tab_donnees = st.tabs(["Le constat", "Explorer", "Données"])

# ==========================================
# ONGLET 1 : LE CONSTAT
# ==========================================
with tab_constat:
    # 1. Garde-fou (Effectif minimal)
    if len(df_filtered) < 50:
        st.warning(f"⚠️ Effectif trop faible ({len(df_filtered)} répondants). Impossible d'afficher une figure fiable.")
        st.stop()
        
    # 2. Calcul de la table
    table_principale = main_table(df_filtered)
    
    # 3. Les 3 métriques
    try:
        row_no_avoid = table_principale[table_principale['option'] == "Je n'évite pas l'IA au travail ou aux études"]
        row_env = table_principale[table_principale['option'] == "Préoccupations environnementales"]
        
        taux_evitement = (1 - row_no_avoid['share'].values[0]) * 100 if not row_no_avoid.empty else 0
        taux_env = row_env['share'].values[0] * 100 if not row_env.empty else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Taux d'évitement global", f"{taux_evitement:.1f} %", "Focus")
        col2.metric("Motif environnemental", f"{taux_env:.1f} %", "Cœur du sujet RSE", delta_color="inverse")
        col3.metric("Échantillon filtré", f"{len(df_filtered)}", "Répondants")
    except Exception as e:
        st.error(f"Impossible de calculer les métriques : {e}")

    st.markdown("---")
    
    # 4. La figure-clé (Titre affirmatif, couleur sur le message)
    st.subheader("L'environnement est un frein majeur à l'adoption de l'IA")
    
    # On enlève la ligne "Je n'évite pas" pour ne garder que les vrais freins
    df_freins = table_principale[table_principale['option'] != "Je n'évite pas l'IA au travail ou aux études"]
    df_freins = df_freins.sort_values('share', ascending=True) # Ascendant pour Plotly barh
    
    fig1 = px.bar(
        df_freins,
        x='share',
        y='option',
        orientation='h',
        title="Raisons d'évitement de l'IA",
        color='share',
        color_continuous_scale='Reds', # Rouge vif pour le message
        text=df_freins['share'].apply(lambda x: f'{x*100:.1f}%')
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(
        yaxis_title="",
        xaxis_title="Part des répondants (%)",
        xaxis_tickformat='.0%',
        showlegend=False,
        height=400
    )
    st.plotly_chart(fig1, width='stretch')
    
    # 5. L'indicateur de population dynamique (qui varie avec les filtres)
    st.info(f"👥 **Indicateur de population** : Ce graphique est basé sur un échantillon de **{len(df_filtered)} répondants** (volontaires de l'enquête en ligne) correspondant aux filtres sélectionnés.")
    
    # 6. Légende-source (Rigueur du cours)
    st.caption("**Source** : Enquête Stack Overflow 2026. "
               "**Population** : Volontaires en ligne ayant répondu à la question sur l'évitement de l'IA. "
               "**Dénominateur** : Nombre total de répondants filtrés. "
               "Il s'agit d'un échantillon de volontaires, et non d'une représentation de l'ensemble des développeurs.")

# ==========================================
# ONGLET 2 : EXPLORER
# ==========================================
with tab_explorer:
    st.header("Explorer les données")
    st.markdown("Croisez les variables pour approfondir l'analyse.")
    
    # Un graphique d'exploration simple (ex: Confiance vs Evitement si disponible)
    if "AITrust" in df.columns:
        st.subheader("Distribution de la confiance en l'IA")
        fig2 = px.histogram(df_filtered, x="AITrust", title="Score de confiance", color_discrete_sequence=['#4C78A8'])
        st.plotly_chart(fig2, width='stretch')
    else:
        st.info("La colonne AITrust n'est pas disponible pour l'exploration.")

# ==========================================
# ONGLET 3 : DONNÉES
# ==========================================
with tab_donnees:
    st.header("Les données derrière la figure-clé")
    st.markdown("Voici la table brute traduite qui permet de construire le graphique de l'onglet « Le constat ».")
    
    # On affiche la table traduite
    st.dataframe(table_principale, width='stretch')