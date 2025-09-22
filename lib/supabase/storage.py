import streamlit as st
from st_supabase_connection import SupabaseConnection

def upload_to_supabase(conn: SupabaseConnection, file_bytes: bytes, bucket_name: str, file_path_in_bucket: str, content_type: str):
    try:
        conn.client.storage.from_(bucket_name).upload(
            path=file_path_in_bucket,
            file=file_bytes,
            file_options={"content-type": content_type}
        )
        return True, None
    except Exception as e:
        if hasattr(e, 'message') and 'Duplicate' in e.message:
            error_message = f"File di path '{file_path_in_bucket}' sudah ada."
            return False, Exception(error_message)
        return False, e

def delete_from_supabase(conn: SupabaseConnection, bucket_name: str, file_path_in_bucket: str):
    try:
        conn.client.storage.from_(bucket_name).remove(paths=[file_path_in_bucket])
        return True, None
    except Exception as e:
        return False, e
    