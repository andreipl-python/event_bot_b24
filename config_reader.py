from pydantic import SecretStr
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv('config.env')


class Settings(BaseSettings):
    bot_token: SecretStr
    b24_url: SecretStr
    connector_url: SecretStr
    dsn: SecretStr
    admin_ids: SecretStr
    stripe_test_token: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
