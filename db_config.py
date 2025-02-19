import os
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

load_dotenv()

class DatabaseManager:
    def __init__(self):
        # Ajout de logging pour debug
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        logging.info(f"URL found: {'Yes' if supabase_url else 'No'}")
        logging.info(f"Key found: {'Yes' if supabase_key else 'No'}")
        
        if not supabase_url or not supabase_key:
            raise ValueError("Missing Supabase configuration. Check your environment variables.")
            
        try:
            self.supabase: Client = create_client(supabase_url, supabase_key)
        except Exception as e:
            logging.error(f"Error creating Supabase client: {str(e)}")
            raise