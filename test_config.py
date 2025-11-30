import os
from dotenv import load_dotenv, find_dotenv

# Find and show which .env file is being used
dotenv_path = find_dotenv()
print(f'Loading .env from: {dotenv_path}')
print(f'Current directory: {os.getcwd()}')

load_dotenv()

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
SERPAPI_KEY = os.getenv('SERPAPI_KEY')

print(f'\nGoogle API Key: {GOOGLE_API_KEY[:10] if GOOGLE_API_KEY else None}...{GOOGLE_API_KEY[-5:] if GOOGLE_API_KEY else None}')
print(f'Key Length: {len(GOOGLE_API_KEY) if GOOGLE_API_KEY else 0}')
print(f'SerpAPI Key: {SERPAPI_KEY[:10] if SERPAPI_KEY else None}...')

if GOOGLE_API_KEY and len(GOOGLE_API_KEY) > 30:
    print('\n? API keys loaded successfully!')
else:
    print('\n? API keys NOT loaded properly')
    print(f'\nDirect file read:')
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            print(f.read())
