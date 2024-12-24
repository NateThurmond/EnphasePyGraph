import sqlite3
import time
import requests
import os
import json

class TokenManager:
    def __init__(self, db_path="token_db.sqlite", expiration_time=3600):
        self.db_path = db_path
        self.expiration_time = expiration_time  # expiration time in seconds
        self.token = None
        self.token_time = None

        # Connect to the SQLite database (or create it if it doesn't exist)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self._create_table()
        self._get_saved_token()

    def _create_table(self):
        """Create a table to store token if it doesn't already exist."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS tokens (
                id INTEGER PRIMARY KEY,
                token TEXT,
                time INTEGER
            )
        """)
        self.conn.commit()

    def _get_saved_token(self):
        """Retrieve the saved token and time from the database."""
        self.cursor.execute("SELECT token, time FROM tokens WHERE id = 1")
        result = self.cursor.fetchone()
        if result:
            self.token, self.token_time = result
        return self.token, self.token_time

    def _save_token(self, token):
        """Save the new token and time in the database."""
        self.token_time = int(time.time())
        self.token = token
        self.cursor.execute("REPLACE INTO tokens (id, token, time) VALUES (1, ?, ?)", (self.token, self.token_time))
        self.conn.commit()

    def _is_token_valid(self):
        """Check if the token is valid based on expiration time."""
        if self.token_time and (int(time.time()) - self.token_time) < self.expiration_time:
            return True
        return False

    def _retrieve_new_token(self):
        """Retrieve a new token from the API."""

        # Authentication data passed in login get token request
        data = {
            'user[email]': os.getenv('ENVOY_USER'),
            'user[password]': os.getenv('ENVOY_USER_PASS')
        }
        envoy_token_url = os.getenv('ENVOY_TOKEN_URL')
        response = requests.post(f'{envoy_token_url}?', data=data)

        if response.status_code != 200:
            raise Exception("Failed to retrieve the token: Status Code: {response.status_code}")

        # Still need to register the token
        response_data = json.loads(response.text)
        data = {
            'session_id': response_data['session_id'],
            'serial_num': os.getenv('ENPHASE_IQ_GATEWAY'),
            'username': os.getenv('ENVOY_USER')
        }
        envoy_token_url_reg = os.getenv('ENVOY_TOKEN_URL_REG')
        response = requests.post(envoy_token_url_reg, json=data)

        if response.status_code != 200:
            raise Exception("Failed to register the token: Status Code: {response.status_code}")

        new_token = response.text

        if new_token:
            return new_token
        else:
            raise Exception("Failed to retrieve the token: No manager_token in the response.")

    def get_token(self):
        """Get the valid token, either from the database or by requesting a new one."""
        if self._is_token_valid():
            print("Using saved token.")
            return self.token
        else:
            print("Token expired or not found. Retrieving new token.")
            new_token = self._retrieve_new_token()
            self._save_token(new_token)
            return new_token

    def close(self):
        """Close the database connection."""
        self.conn.close()
