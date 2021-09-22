import pandas as pd
import streamlit as st
import requests
import io
import datetime as dt
from universal.algos import *
from universal.algos.reversaltrend import ReversalTrend
from universal.tools import *

st.set_option('deprecation.showPyplotGlobalUse', False)

st.markdown("<h1 style='text-align: center; color: blue;'>REVERSALTREND</h1>", unsafe_allow_html=True)
st.sidebar.header("Les paramètres")
# sidebar pour les Moyennes mobile
Moyenne_Mobile_Long_Terme = st.sidebar.slider("Lissage long terme", 2, 200, 2)
Moyenne_Mobile_Court_Terme = st.sidebar.slider("Lissage court terme", 1,1+ Moyenne_Mobile_Long_Terme//2, 1)

# DAte historique des données
Date_start = st.sidebar.date_input('Date de début', dt.date(2021, 1, 1))
Date_fin = st.sidebar.date_input('Date de Fin', dt.date.today())

fee=st.sidebar.number_input(
    "Frais de transaction",
    min_value=0.000,
    max_value=0.02,
    step=0.001,
    format="%.3f")

utilisation_data=st.sidebar.radio("Merci de choisir les tickers:",("Selectionner une liste de tickers:","Vos listes de tickers:"))

#Création de chois de selectioner une liste de nos tickers ou permettre aux utilisateurs de mettre leurs liste de tickers
if utilisation_data=="Selectionner une liste de tickers:":
    #st.sidebar.subheader('Les Tickers')
    #chargemenr de liste de tickers
    companies= pd.read_csv("universal/data/Liste_Tickers.csv",sep=';',encoding='latin-1')
    Symbol_Tickers = list(companies["Company Name"].unique())
    Nom_Tickers = st.sidebar.multiselect("", Symbol_Tickers)
    index = companies[companies['Company Name'].isin(Nom_Tickers)].index
    ticker_Select = list(companies.loc[index, "Symbol"])

elif utilisation_data=="Vos listes de tickers:":
    # chargemenr de liste de tickers
     ticker_Select= list(st.sidebar.text_input('Entrer vos symbols séparés par point-virgules:').split(";"))

# Affichage du dataset
if len(ticker_Select) > 1: #Sélectionner un minimun 2 tickers
    # chargement des données de tickers selectionnés
    TickersData = tools.GetTickersData(ticker_Select, Date_start, Date_fin)

    #renomer les noms des colonnes sinon pas possible d'importer la crypto "BTC-USD;ETH-USD" plante
    TickersData.columns = TickersData.columns.str.replace('-', '_')

    st.subheader("**Graphiques des prix des actions selectionnées**")
    st.line_chart(TickersData)

    st.markdown(
        '''*Info: La rentabilité annuelle historique des actions sélèctionnées sont:*''')

    ret_stock = (np.log(TickersData / TickersData.shift()).mean()) * 252 * 100
    st.write(ret_stock)

    rt = ReversalTrend(Moyenne_Mobile_Court_Terme, Moyenne_Mobile_Long_Terme)
    # data = tools.data('nyse_o')
    result = rt.run(TickersData)
    result.fee=fee
    st.write(pd.DataFrame(result.summary().split('\n'),index=None))

    result.plot(assets=False, logy=True, portfolio_label="ReversalTrend", bah=True, ucrp=True, bcrp=True, olmar=True, bnn=True, corn=True,crp=False,cwmr=False,eg=False,kelly=False,ons=False,pamr=False,rmr=False,up=False)
    st.pyplot()

    st.subheader("Résultat:")
    st.write("Pour le jour suivant, le modèle ReversalTrend vous propose les proportions d'investissement ci-dessous:")
    st.write(result.weights.tail(1))

    st.subheader("Histogramme des poids")
    result.plot_total_weights()
    st.pyplot()
else: st.write("Merci de séléctionner au moins deux actions svp")

