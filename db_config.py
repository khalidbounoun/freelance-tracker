import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.supabase: Client = create_client(
            os.getenv("SUPABASE_URL"),
            os.getenv("SUPABASE_KEY")
        )
    
    def add_transaction(self, transaction_data: dict):
        return self.supabase.table('transactions').insert(transaction_data).execute()
    
    def get_all_transactions(self):
        return self.supabase.table('transactions').select("*").execute()
    
    def get_transactions_by_type(self, transaction_type: str):
        return self.supabase.table('transactions').select("*").eq('type', transaction_type).execute()