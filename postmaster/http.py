import requests

try:
    import json
except ImportError:
    import simplejson as json

from .conf import config

__all__ = [
    'PostmasterError',
    'APIError',
    'NetworkError',
    'AuthenticationError',
    'PermissionError',
    'InvalidDataError',
    'HTTPTransport'
]


class PostmasterError(Exception):
    def __init__(self, message=None, http_body=None, http_status=None, json_body=None):
        super(PostmasterError, self).__init__(message)
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body


class APIError(PostmasterError):
    """
    An error with the Postmaster API, 500 or similar.
    """
    def __str__(self):
        return self.__unicode__()
    def __unicode__(self):
        return 'API Error: %s' % (self.http_body)


class NetworkError(PostmasterError):
    """
    An error with your network connectivity.
    """
    pass

class AuthenticationError(PostmasterError):
    """
    401 style error
    """
    pass


class PermissionError(PostmasterError):
    """
    403 style error.
    """
    pass


class InvalidDataError(PostmasterError):
    """
    400 style error.
    """
    pass


class HTTPTransport(object):

    @classmethod
    def _decode(cls, response_data, response_code):
        if response_code >= 500:
            raise APIError("There was an API error.", http_body=response_data)

        try:
            data = json.loads(response_data)
            if response_code > 299:
                data = data['message']
        except (ValueError, KeyError):
            data = response_data

        if response_code == 400:
            raise InvalidDataError(data, json_body=response_data)
        elif response_code == 401:
            raise AuthenticationError(data, json_body=response_data)
        elif response_code == 403:
            raise PermissionError(data, json_body=response_data)

        return data

    @classmethod
    def post(cls, url, data=None, headers=None):
        # Pass data in already encoded, valid data is returned as a dict
        headers = headers if headers else {}
        headers.update(config.headers)
        headers['content-type'] = 'application/json'
        if data:
            data = json.dumps(data)
        url = '%s%s' % (config.base_url, url)
        try:
            resp = requests.post(url, data=data, headers=headers, timeout=30)
            return cls._decode(resp.text, resp.status_code)
        except requests.ConnectionError, e:
            return cls._decode(e.message, 500)

    @classmethod
    def get(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)
        headers['Accept'] = 'application/json'
        url = '%s%s' % (config.base_url, url)
        try:
            resp = requests.get(url, params=data, headers=headers, timeout=30)
            return cls._decode(resp.text, resp.status_code)
        except requests.ConnectionError, e:
            return cls._decode(e.message, 500)

    @classmethod
    def put(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)
        headers['content-type'] = 'application/json'
        if data:
            data = json.dumps(data)
        url = '%s%s' % (config.base_url, url)
        try:
            resp = requests.put(url, data=data, headers=headers, timeout=30)
            return cls._decode(resp.text, resp.status_code)
        except requests.ConnectionError, e:
            return cls._decode(e.message, 500)

    @classmethod
    def delete(cls, url, data=None, headers=None):
        headers = headers if headers else {}
        headers.update(config.headers)
        headers['content-type'] = 'application/json'
        if data:
            data = json.dumps(data)
        url = '%s%s' % (config.base_url, url)
        try:
            resp = requests.delete(url, data=data, headers=headers, timeout=30)
            return cls._decode(resp.text, resp.status_code)
        except requests.ConnectionError, e:
            return cls._decode(e.message, 500)
