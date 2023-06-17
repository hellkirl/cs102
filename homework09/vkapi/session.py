import time
import typing as tp

import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from requests.packages.urllib3.util.retry import Retry  # type: ignore


class Session(requests.Session):
    def __init__(
            self,
            base_url: str,
            timeout: float = 5.0,
            max_retries: int = 3,
            backoff_factor: float = 0.3,
    ) -> None:
        super().__init__()
        self.base_url = base_url
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_factor = backoff_factor

    def get(self, url, **kwargs: tp.Any) -> requests.Response:
        retries = 0
        while retries <= self.max_retries:
            try:
                full_url = self.base_url + url
                response = super().get(full_url, timeout=self.timeout, **kwargs)
                return response
            except requests.exceptions.RequestException:
                if retries == self.max_retries:
                    raise
                retries += 1
                delay = self.backoff_factor * (2 ** retries)
                time.sleep(delay)

    def post(self, url, data=None, json=None, **kwargs: tp.Any) -> requests.Response:
        retries = 0
        while retries <= self.max_retries:
            try:
                full_url = self.base_url + url
                response = super().post(full_url, data=data, json=json, timeout=self.timeout, **kwargs)
                return response
            except requests.exceptions.RequestException:
                if retries == self.max_retries:
                    raise
                retries += 1
                delay = self.backoff_factor * (2 ** retries)
                time.sleep(delay)

