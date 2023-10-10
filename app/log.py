from datetime import datetime
from flask import request
import geoip2.database

def get_location_from_ip(ip_address):
    # Abra o banco de dados (substitua 'path_to_database' pelo caminho real do arquivo baixado)
    with geoip2.database.Reader('bd_location\\GeoLite2-City.mmdb') as reader:
        try:
            response = reader.city('187.110.234.124')
            city = response.city.name if response.city.name else "Unknown"
            region = response.subdivisions.most_specific.name if response.subdivisions.most_specific.name else "Unknown"
            country = response.country.name if response.country.name else "Unknown"
            return city, region, country
        except:
            return "Unknown", "Unknown", "Unknown"
        
def collect_request_data():
    # Coletando informações do cabeçalho
    user_agent = request.headers.get('User-Agent')
    host = request.headers.get('Host')
    referer = request.headers.get('Referer')
    accept_language = request.headers.get('Accept-Language')

    # Coletando informações da URL
    full_url = request.url
    base_url = request.base_url
    query_parameters = request.args

    # Coletando informações do método e endereço IP
    request_method = request.method
    remote_addr = request.remote_addr

    # Coletando dados da forma (se houver)
    form_data = request.form

    # Coletando cookies (se houver)
    cookies = request.cookies

    # Obtendo a data e hora atual
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    city, region, country = get_location_from_ip(remote_addr)
    # Formatando a mensagem para salvar no arquivo de log
    log_message = f"""
    {timestamp}
    User Agent: {user_agent}
    Host: {host}
    Referer: {referer}
    Accept-Language: {accept_language}
    Full URL: {full_url}
    Base URL: {base_url}
    Query Parameters: {query_parameters}
    Request Method: {request_method}
    Remote Address (IP): {remote_addr}
    Form Data: {form_data}
    Cookies: {cookies}
    -------------------------------------------
    """
    log_message += f"""
    City: {city}
    Region: {region}
    Country: {country}
    -------------------------------------------
    """
    return log_message

def log_request_data(log_message, filename="user_session_log.txt"):
    with open(filename, "a") as log_file:
        log_file.write(log_message)
