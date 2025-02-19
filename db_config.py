import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
import streamlit as st

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Configuration du logging
        logging.basicConfig(level=logging.INFO)
        logger = logging.getLogger(__name__)
        
        # Récupération des variables d'environnement
        supabase_url = st.secrets["SUPABASE_URL"]
        supabase_key = st.secrets["SUPABASE_KEY"]
        
        # Log des informations (masquées pour la sécurité)
        logger.info(f"URL format: {supabase_url[:8]}...{supabase_url[-12:]}")
        logger.info(f"Key length: {len(supabase_key)}")
        
        # Vérification de l'URL
        if not supabase_url.startswith("https://") or not supabase_url.endswith(".supabase.co"):
            raise ValueError("Invalid Supabase URL format")
            
        try:
            self.supabase: Client = create_client(
                supabase_url=supabase_url,
                supabase_key=supabase_key
            )
            logger.info("Supabase client created successfully")
        except Exception as e:
            logger.error(f"Failed to create Supabase client: {type(e).__name__}")
            raise