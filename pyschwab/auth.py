import json
from datetime import datetime
from typing import Any, Dict

from dotenv import load_dotenv

from .user_input import InputRegistry
from .log import logger
from .utils import get_value, request


class Token:
    def __init__(self, config: Dict[str, Any]):
        self.refresh_token: str = None
        self.refresh_token_updated: str = None
        self.access_token: str = None
        self.access_token_updated: str = None
        self.id_token: str = None
        self.token_path = config.get("token_path")
        self.refresh_token_expires_in_sec = config.get('refresh_token_expires_in_sec', 7 * 24 * 60 * 60)
        self.access_token_expires_in_sec = config.get('access_token_expires_in_sec', 1800)

    def is_refresh_token_expired(self):
        diff = datetime.now() - self.refresh_token_updated
        return diff.total_seconds() > self.refresh_token_expires_in_sec

    def is_access_token_expired(self):
        diff = datetime.now() - self.access_token_updated
        return diff.total_seconds() > self.access_token_expires_in_sec

    def update(self, data: Dict[str, Any]):
        self.refresh_token = data['refresh_token']
        self.access_token = data['access_token']
        self.id_token = data['id_token']
        self.access_token_expires_in_sec = data['access_token_expires_in_sec']
        refresh_token_updated = data.get('refresh_token_updated', None)
        if refresh_token_updated:
            self.refresh_token_updated = datetime.fromisoformat(refresh_token_updated)
        access_token_updated = data.get('access_token_updated', None)
        if access_token_updated:
            self.access_token_updated = datetime.fromisoformat(access_token_updated)

    def save(self, response_data: Dict[str, Any], is_refresh_token: bool):
        response_data['access_token_expires_in_sec'] = response_data.pop('expires_in') # rename key
        self.update(response_data)
        now = datetime.now().isoformat()
        output_data = {
            'refresh_token': self.refresh_token,
            'access_token': self.access_token,
            'id_token': self.id_token,
            'refresh_token_updated': now if is_refresh_token else self.refresh_token_updated.isoformat(),
            'access_token_updated': now,
            'access_token_expires_in_sec': self.access_token_expires_in_sec,
        }
        with open(self.token_path, 'w') as f:
            json.dump(output_data, f, indent=4)


class Authorizer:
    def __init__(self, auth_config: Dict[str, Any]):
        load_dotenv()
        self.base_auth_url = get_value(auth_config, 'base_auth_url')
        auth_app_config = auth_config['app']
        self.app_key = get_value(auth_app_config, 'app_key')
        self.app_secret = get_value(auth_app_config, 'app_secret')
        self.callback_url = get_value(auth_app_config, 'callback_url')
        self.token = Token(auth_config['token'])
        self._get_input(auth_config.get('input', {}))
        self._load_tokens()

    def _get_input(self, config):
        input_type = config.get('type', 'terminal')
        input_prompt = config.get('prompt', None)
        input_class = InputRegistry.get_input(input_type)
        self.user_input = input_class(input_prompt)

    def get_access_token(self) -> str:
        return self.token.access_token

    def _load_tokens(self):
        try:
            with open(self.token.token_path, 'r') as f:
                data = json.load(f)
                self.token.update(data)
                self._update_token()
        except (FileNotFoundError, json.JSONDecodeError):
            logger.error("Error loading tokens.")
            self._update_refresh_token()

    def _update_token(self):
        if self.token.is_refresh_token_expired():
            logger.info("Your refresh token has expired, need manual update...")
            self._update_refresh_token()
        elif self.token.is_access_token_expired():
            logger.info("Your access token has expired, will be updated automatically.")
            self._update_access_token()
        else:
            logger.info("The tokens are up to date.")

    def _update_refresh_token(self):
        import webbrowser
        authUrl = f'{self.base_auth_url}/authorize?client_id={self.app_key}&redirect_uri={self.callback_url}'
        logger.info(f"Opening {authUrl} on your browser.")
        webbrowser.open(authUrl)
        url = self.user_input.get_input()
        start_mark = 'code='
        start = url.index(start_mark) + len(start_mark)
        end = url.index('%40&')
        code = f"{url[start:end]}@"
        resp = self._fetch_token('authorization_code', code)
        self.token.save(resp, is_refresh_token=True)
        logger.info("Refresh token and access token updated.")

    def _update_access_token(self):
        resp = self._fetch_token('refresh_token', self.token.refresh_token)
        self.token.save(resp, is_refresh_token=False)
        logger.info(f"Access token updated.")

    def _fetch_token(self, grant_type, code) -> Dict[str, Any]:
        import base64
        headers = {'Authorization': f'Basic {base64.b64encode(bytes(f"{self.app_key}:{self.app_secret}", "utf-8")).decode("utf-8")}', 'Content-Type': 'application/x-www-form-urlencoded'}
        if grant_type == 'authorization_code':
            data = {'grant_type': 'authorization_code', 'code': code, 'redirect_uri': self.callback_url}
        elif grant_type == 'refresh_token':
            data = {'grant_type': 'refresh_token', 'refresh_token': code}
        else:
            raise ValueError("Invalid grant type")
 
        return request(f'{self.base_auth_url}/token', method='POST', headers=headers, data=data).json()
