import pandas as pd
from datetime import datetime
import streamlit as st
import plotly.graph_objects as go
from db_config import DatabaseManager
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration de la page Streamlit
st.set_page_config(
    page_title="Freelance Tracker",
    page_icon="📊",
    layout="wide"
)

# Gestion de l'authentification
def check_password():
    if not os.getenv("STREAMLIT_PASSWORD"):
        st.error("Mot de passe non configuré dans le fichier .env")
        return False
        
    if "password_correct" not in st.session_state:
        st.text_input(
            "Mot de passe", 
            type="password",
            key="password",
            on_change=verify_password
        )
        return False
    
    return st.session_state.password_correct

def verify_password():
    if st.session_state.password == os.getenv("STREAMLIT_PASSWORD"):
        st.session_state.password_correct = True
    else:
        st.error("Mot de passe incorrect")

# Initialisation de la base de données
db = DatabaseManager()

def format_amount(amount: float) -> str:
    """Formate les montants en format français"""
    return f"{amount:,.2f} €".replace(",", " ")

def create_transaction():
    """Gère la création d'une nouvelle transaction"""
    with st.sidebar:
        st.header("Nouvelle Transaction")
        date = st.date_input("Date", datetime.now())
        transaction_type = st.selectbox(
            "Type de Transaction",
            ["Facturation Client", "Salaire", "Utilisation Trésorerie"]
        )
        
        if transaction_type == "Facturation Client":
            amount = st.number_input("Montant Facture", min_value=0.0, value=0.0)
            client = st.text_input("Client")
            commission_percent = st.number_input("Commission (%)", min_value=0.0, max_value=100.0, value=15.0)
            commission_amount = (amount * commission_percent / 100)
            st.info(f"Commission calculée: {format_amount(commission_amount)}")
        else:
            amount = st.number_input("Montant", min_value=0.0, value=0.0)
            client = ""
            commission_amount = 0.0
            
        notes = st.text_area("Notes")
        
        if st.button("Ajouter Transaction"):
            transaction_data = {
                "id": f"{date.strftime('%Y%m%d')}-{hash(str(amount) + str(datetime.now()))}",
                "date": date.isoformat(),
                "type": transaction_type,
                "client": client,
                "amount": amount,
                "commission_amount": commission_amount,
                "treasury_impact": calculate_treasury_impact(transaction_type, amount, commission_amount),
                "notes": notes
                    }
            
            try:
                db.add_transaction(transaction_data)
                st.success("Transaction ajoutée avec succès!")
            except Exception as e:
                st.error(f"Erreur lors de l'ajout de la transaction: {str(e)}")

def calculate_treasury_impact(transaction_type: str, amount: float, commission_amount: float) -> float:
    """Calcule l'impact sur la trésorerie selon le type de transaction"""
    if transaction_type == "Facturation Client":
        return amount - commission_amount
    elif transaction_type in ["Salaire", "Utilisation Trésorerie"]:
        return -amount
    return 0.0

def display_dashboard():
    """Affiche le tableau de bord"""
    try:
        # Récupération des données
        response = db.get_all_transactions()
        if not response.data:
            st.info("Aucune transaction enregistrée")
            return
            
        df = pd.DataFrame(response.data)
        df['date'] = pd.to_datetime(df['date'])
        
        # Métriques principales
        col1, col2, col3 = st.columns(3)
        with col1:
            total_invoiced = df[df['type'] == 'Facturation Client']['amount'].sum()
            st.metric("Total Facturé", format_amount(total_invoiced))
        with col2:
            treasury = df['treasury_impact'].sum()
            st.metric("Trésorerie", format_amount(treasury))
        with col3:
            total_commissions = df['commission_amount'].sum()
            st.metric("Total Commissions", format_amount(total_commissions))
        
        # Graphique d'évolution
        st.subheader("Évolution mensuelle")
        monthly_stats = df.set_index('date').resample('M').agg({
            'amount': 'sum',
            'treasury_impact': 'sum'
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=monthly_stats.index, 
            y=monthly_stats['amount'],
            mode='lines+markers', 
            name='Montant'
        ))
        fig.add_trace(go.Scatter(
            x=monthly_stats.index, 
            y=monthly_stats['treasury_impact'],
            mode='lines+markers', 
            name='Impact Trésorerie'
        ))
        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Montant (€)",
            hovermode='x unified'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Tableau des transactions
        st.subheader("Transactions récentes")
        display_df = df.sort_values('date', ascending=False).head(10)
        st.dataframe(
            display_df[['date', 'type', 'client', 'amount', 'commission_amount', 'treasury_impact', 'notes']],
            use_container_width=True
        )
            
    except Exception as e:
        st.error(f"Erreur lors de l'affichage du tableau de bord: {str(e)}")

def main():
    if not check_password():
        return
        
    st.title("📊 Freelance Income Tracker")
    create_transaction()
    display_dashboard()

if __name__ == "__main__":
    main()