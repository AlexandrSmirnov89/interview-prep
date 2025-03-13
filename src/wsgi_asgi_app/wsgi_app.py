import json
import urllib.request


def fetch_exchange_rate(currency: str):
    url = f'https://api.exchangerate-api.com/v4/latest/{currency}'
    try:
        with urllib.request.urlopen(url) as response:
            return response.read().decode('utf-8')
    except Exception as e:
        return json.dumps({'error': str(e)})

def currency_app(environ, start_response):
    path = environ.get('PATH_INFO', '/').strip('/')

    if not path:
        response_body = json.dumps({'error': 'Currency not provided'}).encode('utf-8')
        status = '400 Bad Request'
    else:
        response_body = fetch_exchange_rate(path).encode('utf-8')
        status = '200 OK'

    headers = [('Content-Type', 'application/json')]
    start_response(status, headers)
    return [response_body]


if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('127.0.0.1', 8000, currency_app)
    print('WSGI-сервер запущен на http://127.0.0.1:8000')
    server.serve_forever()
