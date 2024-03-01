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
    redsys_test_token: SecretStr
    products_cities: SecretStr
    products_custom_property_lvl2: SecretStr

    class Config:
        env_file = '.env'
        env_file_encoding = 'utf-8'


config = Settings()
