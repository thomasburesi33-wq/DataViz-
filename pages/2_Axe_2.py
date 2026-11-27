import streamlit as st
import plotly.express as px
import pandas as pd
from analysis.axe_2 import (
    filter_axis, filter_countries, main_table, 
    AXIS_FILTER, PAYS_CIBLES, TRADUCTION_AIAVOID
)

st.set_page_config(page_title="Axe 2 : Freins et confiance", layout="wide")

st.title("Axe 2 : Freins et confiance")
st.markdown("*Quels sont les freins à l'adoption de l'IA en Europe, et comment la France se positionne-t-elle sur les enjeux RSE ?*")

# --- CHARGEMENT DES DONNÉES ---
@st.cache_data
def load_real_data():
    return pd.read_csv("data/survey_2026_results.csv", low_memory=False)

df = load_real_data()

# --- FILTRES ---
# Filtre pays : France vs 8 pays les plus représentés
pays_disponibles = [p for p in PAYS_CIBLES if p in df['Country'].unique()]
selected_countries = st.sidebar.multiselect(
    "Filtrer par pays (France vs 8 pays européens)",
    options=pays_disponibles,
    default=["France"] # La France par défaut, comme demandé
)
df_filtered = filter_countries(df, selected_countries)

# Filtre âge
if AXIS_FILTER in df.columns:
    age_options = sorted(df[AXIS_FILTER].dropna().unique().tolist())
    selected_ages = st.sidebar.multiselect("Filtrer par tranche d'âge", age_options, default=age_options)
    df_filtered = filter_axis(df_filtered, selected_ages)

# --- ONGLETS ---
tab_constat, tab_explorer, tab_donnees = st.tabs(["Le constat", "Explorer", "Données"])

# ==========================================
# ONGLET 1 : LE CONSTAT
# ==========================================
with tab_constat:
    if len(df_filtered) < 50:
        st.warning(f"⚠️ Effectif trop faible ({len(df_filtered)} répondants). Impossible d'afficher une figure fiable.")
        st.stop()
        
    table_principale = main_table(df_filtered)
    
    # Métriques
    try:
        row_no_avoid = table_principale[table_principale['option'] == "Je n'évite pas l'IA"]
        row_env = table_principale[table_principale['option'] == "Préoccupations environnementales"]
        
        taux_evitement = (1 - row_no_avoid['share'].values[0]) * 100 if not row_no_avoid.empty else 0
        taux_env = row_env['share'].values[0] * 100 if not row_env.empty else 0
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Taux d'évitement global", f"{taux_evitement:.1f} %")
        col2.metric("Motif environnemental (RSE)", f"{taux_env:.1f} %", delta_color="inverse")
        col3.metric("Échantillon filtré", f"{len(df_filtered)}", "Répondants")
    except Exception:
        pass

    st.markdown("---")
    
    # Figure principale
    st.subheader("L'environnement est un frein majeur, juste derrière la sécurité et la peur de perdre son emploi")
    
    df_freins = table_principale[table_principale['option'] != "Je n'évite pas l'IA"]
    df_freins = df_freins.sort_values('share', ascending=True)
    
    fig1 = px.bar(
        df_freins,
        x='share',
        y='option',
        orientation='h',
        title="Raisons d'évitement de l'IA (en %)",
        color='share',
        color_continuous_scale='Reds',
        text=df_freins['share'].apply(lambda x: f'{x*100:.1f}%'),
        labels={'share': 'Part des répondants (%)', 'option': 'Raisons'} # Traduction des axes
    )
    fig1.update_traces(textposition='outside')
    fig1.update_layout(height=400, showlegend=False, xaxis_tickformat='.0%')
    st.plotly_chart(fig1, width='stretch')
    
    # Indicateur de population dynamique
    st.info(f"👥 **Indicateur de population** : Ce graphique repose sur **{len(df_filtered)} répondants** (volontaires en ligne) correspondant aux filtres sélectionnés.")
    
    # Légende source
    st.caption("**Source** : Enquête Stack Overflow 2026. "
               "**Population** : Volontaires en ligne (focus France vs 8 pays européens). "
               "**Dénominateur** : Répondants filtrés. "
               "Ne représente pas l'ensemble des développeurs.")

# ==========================================
# ONGLET 2 : EXPLORER
# ==========================================
with tab_explorer:
    st.header("Explorer les données")
    
    # --- GRAPHIQUE 1 : Comparaison par pays (freins environnementaux) ---
    st.subheader("1. Comparaison européenne sur les freins environnementaux")
    
    # On calcule la part de l'environnement par pays
    df_env = df_filtered[df_filtered['AIAvoid'] == "Environmental concerns"]
    df_env_counts = df_env['Country'].value_counts().reset_index()
    df_env_counts.columns = ['Pays', 'Nombre de répondants']
    
    fig2 = px.bar(
        df_env_counts,
        x='Pays',
        y='Nombre de répondants',
        title="Nombre de développeurs citant l'environnement comme frein",
        color='Pays',
        labels={'Pays': 'Pays', 'Nombre de répondants': 'Nombre de personnes'} # Traduction
    )
    fig2.update_layout(showlegend=False)
    st.plotly_chart(fig2, width='stretch')
    
    # --- GRAPHIQUE 2 : Distribution par âge (Est-ce que les jeunes évitent plus ?) ---
    st.subheader("2. L'âge influence-t-il l'évitement ?")
    
    if AXIS_FILTER in df_filtered.columns:
        df_age = df_filtered[df_filtered['AIAvoid'] == "Environmental concerns"]
        df_age_counts = df_age[AXIS_FILTER].value_counts().reset_index()
        df_age_counts.columns = ['Tranche d\'âge', 'Nombre de répondants']
        
        fig3 = px.pie(
            df_age_counts,
            names='Tranche d\'âge',
            values='Nombre de répondants',
            title="Répartition par âge des personnes citant l'environnement",
            labels={'Tranche d\'âge': 'Âge', 'Nombre de répondants': 'Effectif'}
        )
        st.plotly_chart(fig3, width='stretch')
    else:
        st.info("La colonne Age n'est pas disponible.")

# ==========================================
# ONGLET 3 : DONNÉES
# ==========================================
with tab_donnees:
    st.header("Les données derrière la figure-clé")
    st.markdown("Voici la table brute traduite qui permet de construire le graphique de l'onglet « Le constat ».")
    st.dataframe(table_principale, width='stretch')