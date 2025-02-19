import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import streamlit as st
from datetime import datetime
from typing import Optional, Dict, List

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        try:
            # Récupération des variables d'environnement via Streamlit
            supabase_url = st.secrets["SUPABASE_URL"]
            supabase_key = st.secrets["SUPABASE_KEY"]
            
            # Log des informations (masquées pour la sécurité)
            self.logger.info(f"URL format: {supabase_url[:8]}...{supabase_url[-12:]}")
            self.logger.info(f"Key length: {len(supabase_key)}")
            
            # Vérification de l'URL
            if not supabase_url.startswith("https://") or not supabase_url.endswith(".supabase.co"):
                raise ValueError("Format d'URL Supabase invalide")
                
            # Création du client Supabase
            self.supabase: Client = create_client(
                supabase_url=supabase_url,
                supabase_key=supabase_key
            )
            self.logger.info("Client Supabase créé avec succès")
            
        except Exception as e:
            self.logger.error(f"Erreur d'initialisation: {str(e)}")
            raise

    def add_transaction(self, transaction_data: Dict) -> Dict:
        """
        Ajoute une nouvelle transaction dans la base de données.
        """
        try:
            response = self.supabase.table('transactions').insert(transaction_data).execute()
            self.logger.info(f"Transaction ajoutée avec succès: {transaction_data.get('id', 'N/A')}")
            return response.data
        except Exception as e:
            self.logger.error(f"Erreur lors de l'ajout de la transaction: {str(e)}")
            raise

    def get_all_transactions(self):
        """
        Récupère toutes les transactions de la base de données.
        """
        try:
            response = self.supabase.table('transactions').select("*").order('date', desc=True).execute()
            self.logger.info(f"Récupération de {len(response.data)} transactions")
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des transactions: {str(e)}")
            raise

    def get_transactions_by_type(self, transaction_type: str):
        """
        Récupère les transactions d'un type spécifique.
        """
        try:
            response = self.supabase.table('transactions').select("*").eq('type', transaction_type).execute()
            self.logger.info(f"Récupération des transactions de type: {transaction_type}")
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des transactions par type: {str(e)}")
            raise

    def get_transactions_by_date_range(self, start_date: datetime, end_date: datetime):
        """
        Récupère les transactions dans une plage de dates.
        """
        try:
            response = self.supabase.table('transactions')\
                .select("*")\
                .gte('date', start_date.isoformat())\
                .lte('date', end_date.isoformat())\
                .execute()
            self.logger.info(f"Récupération des transactions entre {start_date} et {end_date}")
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la récupération des transactions par date: {str(e)}")
            raise

    def update_transaction(self, transaction_id: str, update_data: Dict):
        """
        Met à jour une transaction existante.
        """
        try:
            response = self.supabase.table('transactions')\
                .update(update_data)\
                .eq('id', transaction_id)\
                .execute()
            self.logger.info(f"Transaction mise à jour: {transaction_id}")
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la mise à jour de la transaction: {str(e)}")
            raise

    def delete_transaction(self, transaction_id: str):
        """
        Supprime une transaction.
        """
        try:
            response = self.supabase.table('transactions')\
                .delete()\
                .eq('id', transaction_id)\
                .execute()
            self.logger.info(f"Transaction supprimée: {transaction_id}")
            return response
        except Exception as e:
            self.logger.error(f"Erreur lors de la suppression de la transaction: {str(e)}")
            raise

    def get_transaction_stats(self) -> Dict:
        """
        Récupère les statistiques globales des transactions.
        """
        try:
            response = self.supabase.table('transactions').select("*").execute()
            data = response.data
            
            stats = {
                "total_count": len(data),
                "types": {},
                "total_amount": sum(float(t.get('amount', 0)) for t in data),
                "total_commission": sum(float(t.get('commission_amount', 0)) for t in data),
                "total_treasury_impact": sum(float(t.get('treasury_impact', 0)) for t in data)
            }
            
            # Comptage par type
            for transaction in data:
                t_type = transaction.get('type')
                if t_type:
                    stats["types"][t_type] = stats["types"].get(t_type, 0) + 1
            
            self.logger.info("Statistiques calculées avec succès")
            return stats
        except Exception as e:
            self.logger.error(f"Erreur lors du calcul des statistiques: {str(e)}")
            raise