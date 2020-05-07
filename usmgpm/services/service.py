import os
import abc
import json
from abc import ABC

import requests

from usmgpm.services.exceptions import *


class Service(ABC):
    @property
    @abc.abstractmethod
    def url(self):
        """
        This property returns the URL where requests will be made
        :return: URL where requests are made
        :rtype: str
        """
        return ''

    user_agent = 'USM-Games-Page-Manager-0.1a'
    authorization = None

    @property
    def headers(self):
        headers = dict()
        headers['User-Agent'] = self.user_agent
        if self.authorization:
            headers['Authorization'] = self.authorization
        return headers

    def set_user_agent(self, user_agent):
        self.user_agent = user_agent

    def set_token(self, token: str, t_type: str = "Bearer"):
        self.authorization = f"{t_type} {token}"

    def remove_token(self):
        self.authorization = None

    @property
    def token(self):
        if self.authorization:
            return self.authorization.split(' ')[1]

    @property
    def token_type(self):
        if self.authorization:
            return self.authorization.split(' ')[0]

    @staticmethod
    def _process_response(res: requests.Response):
        """
        Process response status code to raise the corresponding ServiceError and
        parses the given JSON.
        :param res: The response given by a request to the provider
        :type res: requests.Response
        :return: Dictionary with the response data
        :rtype: dict
        """
        if res.status_code == 400:
            raise InvalidDataError(res)
        elif res.status_code == 401:
            raise UnauthorizedError(res)
        elif res.status_code == 403:
            raise ForbiddenError(res)
        elif res.status_code == 404:
            raise NotFoundError(res)
        elif res.status_code == 410:
            raise AlreadyDeletedError(res)
        elif res.status_code >= 400:
            raise ServiceError()
        decoded = res.content.decode()
        try:
            return json.loads(decoded)
        except ValueError:
            return decoded

    def get(self, path: str, params: dict = None):
        """
        Make a GET request to the given path.
        :param path: The path in the service where to make the request
        :type path: str
        :param params: Query params for the request
        :type params: dict
        :return: The returned JSON serialized as a dict
        :rtype: dict
        """
        req = requests.get(os.path.join(self.url, path), headers=self.headers, params=params)
        data = self._process_response(req)
        return data

    def post(self, path: str = None, data: dict = None):
        """
        Make a POST request to the given path.
        :param path: The path in the service where to make the request
        :type path: str
        :param data: Data to be sent in the request
        :type data: dict
        :return: The returned JSON serialized as a dict
        :rtype: dict
        """
        final_url = self.url if path is None else os.path.join(self.url, path)
        req = requests.post(final_url, json=data, headers=self.headers)
        data = self._process_response(req)
        return data

    def put(self, path: str, data: dict = None):
        """
        Make a PUT request to the given path.
        :param path: The path in the service where to make the request
        :type path: str
        :param data: Data to be sent in the request
        :type data: dict
        :return: The returned JSON serialized as a dict
        :rtype: dict
        """
        req = requests.post(os.path.join(self.url, path), json=data, headers=self.headers)
        data = self._process_response(req)
        return data

    def delete(self, path: str):
        """
        Make a DELETE request to the given path.
        :param path: The path in the service where to make the request
        :type path: str
        :return: The returned JSON serialized as a dict
        :rtype: dict
        """
        req = requests.delete(os.path.join(self.url, path), headers=self.headers)
        data = self._process_response(req)
        return data
