import json
import base64
import datetime 
from urllib.parse import urlencode

import requests

class SpotifyAPI(object):
    """
    Spotify API used to Authenticate client and Search Artists, Tracks, Albums etc.
    """
    _token_url = 'https://accounts.spotify.com/api/token'
    _access_token = None
    _access_token_expires = datetime.datetime.now()
    _access_token_did_expire = True
    _client_id = None
    _client_secret = None

    def __init__(self, client_id, client_secret, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._client_id = client_id
        self._client_secret = client_secret

    def _get_access_token_data(self):
        """
        Returns the body for POST request to be send for client Auithentication
        """
        return {
            "grant_type": "client_credentials"
        }

    def _get_client_crediantials(self):
        """
        Returns base64 credential string
        """
        if self._client_id == None or self._client_secret == None:
            raise Exception("You must set Client ID and Client Secret")
        client_creds = f"{self._client_id}:{self._client_secret}"
        clients_creds_b64 = base64.b64encode(client_creds.encode())
        return clients_creds_b64.decode()

    def _get_access_token_headers(self):
        """
        Returns the header data for POST request to be send for client Auithentication
        """
        client_crediantials = self._get_client_crediantials()
        return {
            "Authorization": f"Basic {client_crediantials}"
        }

    def _perform_auth(self):
        """
        Performs Authentication for client
        """
        token_url = self._token_url
        token_data = self._get_access_token_data()
        token_headers = self._get_access_token_headers()
        r = requests.post(token_url, data=token_data, headers=token_headers)
        if r.status_code not in range(200, 299):
            raise Exception("Authentication Failed")
        data = r.json()
        now = datetime.datetime.now()
        self._access_token = data['access_token']
        expires_in = data['expires_in']
        expires = now + datetime.timedelta(seconds=expires_in)
        self._access_token_expires = expires
        self._access_token_did_expire = expires < now
        return True

    def _get_access_token(self):
        """
        Returns Access token by performing Authentication
        """
        token = self._access_token
        expires = self._access_token_expires
        now = datetime.datetime.now()
        if expires < now:
            self._perform_auth()
            return self._get_access_token()
        elif token == None:
            self._perform_auth()
            return self._get_access_token()
        return token

    def _get_resource_headers(self):
        """
        Returns header data for GET request to be send for getting resources
        """
        access_token = self._get_access_token()
        headers = {
            "Authorization": f"Bearer {access_token}"
        }
        return headers

    def _get_resource(self, _id, resource_type='albums', version='v1'):
        """
        Returns resources for either getting albums or artists.
        """
        endpoint = f"https://api.spotify.com/{version}/{resource_type}/{_id}"
        headers = self._get_resource_headers()
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
        
    def get_album(self, _id):
        """
        Returns albums JSON on passing Album ID
        """
        return self._get_resource(_id, resource_type='albums')

    def get_artist(self, _id):
        """
        Returns artists JSON on passing Artist ID
        """
        return self._get_resource(_id, resource_type='artists')

    def _base_search(self, query_params):
        """
        Returns JSON on passing search query
        """
        headers = self._get_resource_headers()
        endpoint = f"https://api.spotify.com/v1/search?{query_params}"
        r = requests.get(endpoint, headers=headers)
        if r.status_code not in range(200,299):
            return {}
        return r.json()

    def search(self, query=None, operator=None, operator_query=None, search_type='track'):
        """
        query -> string or Dictionary
        operator -> OR/NOT
        operator_query -> string
        search_type -> string.
        Returns JSON for search query
        """
        if query == None:
            raise Exception("A Search query is required")
        if isinstance(query, dict):
            query = " ".join([f"{k}:{v}" for k,v in query.items()])
        if operator != None and operator_query != None:
            if operator.lower() == "or" or operator.lower() == "not":
                operator = operator.upper()
                if isinstance(operator_query, str):
                    query = f"{query} {operator} {operator_query}"
        query_params = urlencode({
            "q": query,
            "type": search_type.lower()
        })
        return self._base_search(query_params)

client_id = "<YOUR CLIENT ID>"
client_secret = "<YOUR CLIENT SECRET KEY>"

spotify = SpotifyAPI(client_id, client_secret)

# Examples for searching songs by simply track title or track title and artist name

# blinding_lights = spotify.search({"track": "Blinding Lights", "artist": "The Weeknd"}, search_type='track')
# sun_is_shining = spotify.search("Sun is shining", search_type="track")