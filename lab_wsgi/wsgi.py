from wsgiref.simple_server import make_server
import json
from datetime import datetime
import pytz
import requests

def get_current_time(environ, start_response):
    tz_name = environ.get('PATH_INFO')[1:]
    if not tz_name:
        tz_name = 'GMT'
    try:
        tz = pytz.timezone(tz_name)
    except pytz.UnknownTimeZoneError:
        start_response('404 Not Found', [('Content-type', 'text/html; charset=utf-8')])
        return [b'<html><body><h1>TZ not found </h1></body></html>']
    current_time = datetime.now(tz).strftime('%d.%m.%Y %H:%M:%S %Z')
    html_content = f'<html><body><h1>Current Time in {tz_name}</h1><p>{current_time}</p></body></html>'
    start_response('200 OK', [('Content-type', 'text/html')])
    return [html_content.encode()]

def convert_time(environ, start_response):
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [('Content-type', 'text/html')])
        return [b'<html><body><h1>Method not allowed</h1></body></html>']
    
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    request_body = environ['wsgi.input'].read(content_length)
    try:
        request_body = request_body.decode().split('\r\n')
        data_json = json.loads(request_body[0])
        trg_tz = pytz.timezone(request_body[1])
        src_tz = data_json['tz']
        date_src = data_json['date'].split(' ')
        m, d, y = list(map(int, date_src[0].split('.')))
        h, mi, sec = list(map(int, date_src[1].split(':')))
        trg_tz = request_body[1]
        date_trg = datetime(y, m, d, h, mi, sec, tzinfo=pytz.timezone(src_tz)).astimezone(pytz.timezone(trg_tz)).strftime('%d-%m-%Y %H:%M:%S %Z')
        html_content = f'<html><body><h1>Converted Time</h1><p>{date_trg}</p></body></html>'
        start_response('200 OK', [('Content-type', 'text/html')])
        return [html_content.encode()]
    except KeyError:
        start_response('400 Bad Request', [('Content-type', 'text/html')])
        return [b'<html><body><h1>Bad Request</h1></body></html>']

def date_diff(environ, start_response):
    if environ['REQUEST_METHOD'] != 'POST':
        start_response('405 Method Not Allowed', [('Content-type', 'text/html')])
        return [b'<html><body><h1>Method Not Allowed</h1></body></html>']
    
    content_length = int(environ.get('CONTENT_LENGTH', 0))
    request_body = environ['wsgi.input'].read(content_length)
    try:
        data_json = json.loads(request_body.decode())
        tz_first = pytz.timezone(data_json['first_tz'])
        datetime_first = datetime.strptime(data_json['first_date'], '%d.%m.%Y %H:%M:%S')
        datetime_first = tz_first.localize(datetime_first)
        tz_sec = pytz.timezone(data_json['second_tz'])
        datetime_sec = datetime.strptime(data_json['second_date'], '%I:%M%p %Y-%m-%d')
        datetime_sec = tz_sec.localize(datetime_sec)
        diff_seconds = round(abs((datetime_sec - datetime_first).total_seconds()))
        html_content = f'<html><body><h1>Date Difference</h1><p>{diff_seconds} seconds</p></body></html>'
        start_response('200 OK', [('Content-type', 'text/html')])
        return [html_content.encode()]
    except KeyError:
        start_response('400 Bad Request', [('Content-type', 'text/html')])
        return [b'<html><body><h1>Bad Request</h1></body></html>']

def app(environ, start_response):
    path = environ.get('PATH_INFO')
    if path == '/api/v1/convert':
        return convert_time(environ, start_response)
    elif path == '/api/v1/datediff':
        return date_diff(environ, start_response)
    else:
        return get_current_time(environ, start_response)

if __name__ == '__main__':
    port = int(input('Enter the desired port: '))
    # port = 8080
    with make_server('', port, app) as serv:
        print(f"The server will start on the port: {port}")
        serv.serve_forever()
