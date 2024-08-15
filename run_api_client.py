from app.factory import Factory
from app.settings import Settings

if __name__ == '__main__':
    factory = Factory(Settings)
    factory.run_api_client()
