import hashlib
import hmac
import time
from typing import Optional
from urllib.parse import urlencode

import requests

from .logging_config import setup_logger

logger = setup_logger("trading_bot.client")

BASE_URL = "https://testnet.binancefuture.com"


class BinanceAPIError(Exception):
    def __init__(self, status_code: int, code: int, msg: str):
        self.status_code = status_code
        self.code = code
        self.msg = msg
        super().__init__(f"API Error {code}: {msg} (HTTP {status_code})")


class BinanceConnectionError(Exception):
    pass


class BinanceFuturesClient:
    def __init__(self, api_key: str, secret_key: str, base_url: str = BASE_URL):
        self.api_key = api_key
        self.secret_key = secret_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})
        logger.info(f"Client initialized for {self.base_url}")

    def _sign(self, params: dict) -> dict:
        params["timestamp"] = int(time.time() * 1000)
        query_string = urlencode(params)
        signature = hmac.new(
            self.secret_key.encode("utf-8"),
            query_string.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()
        params["signature"] = signature
        logger.debug(f"Signed request with params: {list(params.keys())}")
        return params

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[dict] = None,
        signed: bool = True,
    ) -> dict:
        url = f"{self.base_url}{endpoint}"
        params = params or {}

        if signed:
            params = self._sign(params)

        logger.info(f"{method} {url}")
        logger.debug(f"Request params: {params}")

        try:
            response = self.session.request(
                method, url, params=params, timeout=10
            )
        except requests.exceptions.Timeout:
            msg = "Request timed out after 10 seconds."
            logger.error(msg)
            raise BinanceConnectionError(msg)
        except requests.exceptions.ConnectionError as e:
            msg = f"Connection error: {e}"
            logger.error(msg)
            raise BinanceConnectionError(msg)
        except requests.exceptions.RequestException as e:
            msg = f"Request failed: {e}"
            logger.error(msg)
            raise BinanceConnectionError(msg)

        logger.debug(f"Response status: {response.status_code}")
        logger.debug(f"Response body: {response.text}")

        if response.status_code != 200:
            try:
                error_data = response.json()
                code = error_data.get("code", -1)
                msg = error_data.get("msg", response.text)
            except ValueError:
                code = -1
                msg = response.text
            logger.error(f"API error: {code} - {msg}")
            raise BinanceAPIError(response.status_code, code, msg)

        return response.json()

    def place_order(self, **kwargs) -> dict:
        logger.info(f"Placing order: {kwargs}")
        return self._request("POST", "/fapi/v1/order", params=kwargs)

    def place_stop_order(self, **kwargs) -> dict:
        logger.info(f"Placing stop order: {kwargs}")
        params = dict(kwargs)
        params.setdefault("workingType", "CONTRACT_PRICE")
        params.setdefault("closePosition", "false")
        return self._request("POST", "/fapi/v1/order", params=params)

    def get_exchange_info(self) -> dict:
        return self._request("GET", "/fapi/v1/exchangeInfo", signed=False)

    def get_account_info(self) -> dict:
        return self._request("GET", "/fapi/v2/account", signed=True)

    def change_leverage(self, symbol: str, leverage: int) -> dict:
        logger.info(f"Changing leverage for {symbol} to {leverage}x")
        return self._request(
            "POST", "/fapi/v1/leverage", params={"symbol": symbol, "leverage": leverage}
        )