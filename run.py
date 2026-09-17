import os
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

from app import create_app

env_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(env_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', True)
    print(f"Starting {app.config.get('APP_NAME')} in [{env_name}] mode on http://127.0.0.1:{port}")
    app.run(host='127.0.0.1', port=port, debug=debug)
