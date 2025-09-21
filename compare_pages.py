import requests
from bs4 import BeautifulSoup

session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'})

# Login
login_url = 'https://sachtienganhhanoi.com/my-account/'
response = session.get(login_url)
soup = BeautifulSoup(response.text, 'html.parser')
form = soup.find('form', {'class': 'woocommerce-form-login'})
nonce = form.find('input', {'name': 'woocommerce-login-nonce'}).get('value')

login_data = {
    'username': 'dungla2011@gmail.com',
    'password': '11111111', 
    'woocommerce-login-nonce': nonce,
    '_wp_http_referer': '/my-account/',
    'login': 'Log in'
}
session.post(login_url, data=login_data)

# Check both pages
pages = [
    ('Now I Know 2', 'https://sachtienganhhanoi.com/audio-now-i-know-2-student-book-audio-cd/'),
    ('Now I Know 5', 'https://sachtienganhhanoi.com/audio-now-i-know-5-student-book-audio-cd/')
]

for page_name, url in pages:
    print(f'\n=== {page_name} ===')
    response = session.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    modules = soup.find_all('div', {'class': lambda x: x and 'wpcp-module' in x and 'ShareoneDrive' in x})
    
    for i, module in enumerate(modules, 1):
        print(f'Module {i}:')
        print(f'  Token: {module.get("data-token")}')
        print(f'  Account ID: {module.get("data-account-id")}')  
        print(f'  Drive ID: {module.get("data-drive-id")}')
        print(f'  Source: {module.get("data-source")}')