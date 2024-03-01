import json
from datetime import datetime
from typing import List, Optional

import asyncpg
from aiogram.types import SuccessfulPayment
from asyncpg import Record

from config_reader import config


class Database:

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.pool.close()

    def __init__(self, min_size=10, max_size=500, max_queries=500, timeout=30):
        self.dsn = config.dsn.get_secret_value()
        self.pool = None
        self.min_size = min_size
        self.max_size = max_size
        self.max_queries = max_queries
        self.timeout = timeout

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.dsn,
            min_size=self.min_size,
            max_size=self.max_size,
            max_queries=self.max_queries,
            max_inactive_connection_lifetime=self.timeout,
        )

    async def select(self, query: str, *args) -> List[asyncpg.Record]:
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                result = await conn.fetch(query, *args)
                return result

    async def update(self, query: str, *args) -> None:
        if self.pool is None:
            await self.connect()
        async with self.pool.acquire() as conn:
            async with conn.transaction():
                await conn.execute(query, *args)

    async def create_table_users(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, 
        user_id BIGINT CONSTRAINT uk_users_user_id UNIQUE, 
        username TEXT, full_name TEXT, b24_id INT, im_link_b24 TEXT, lead_id INT, bot_blocked BOOLEAN DEFAULT FALSE, 
        phone TEXT, city TEXT);'''
        return await self.update(query)

    async def create_table_deals(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS deals (id SERIAL PRIMARY KEY, user_id BIGINT, deal_id INT, product_id INT, 
        opportunity REAL, paid BOOLEAN DEFAULT FALSE, create_time TIMESTAMP);'''
        return await self.update(query)

    async def add_new_deal(self, user_id: int, deal_id: int, product_id: int, opportunity: float):
        time_now = datetime.now()
        query = '''INSERT INTO deals (user_id, deal_id, product_id, opportunity, create_time) VALUES ($1, $2, $3, $4, $5);'''
        return await self.update(query, user_id, deal_id, product_id, opportunity, time_now)

    async def create_table_admin_messages(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS admin_messages (id SERIAL PRIMARY KEY, start_message TEXT);'''
        return await self.update(query)

    async def create_table_buttons_stat(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS buttons_stat (id SERIAL PRIMARY KEY, user_id BIGINT, button_name TEXT, 
        count INT, last_press TIMESTAMP DEFAULT '2023-01-01 00:00:00', 
        CONSTRAINT unique_user_button UNIQUE (user_id, button_name));'''
        return await self.update(query)

    async def create_table_products(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS products (id INT PRIMARY KEY, name TEXT, active_from TIMESTAMP, 
        active_to TIMESTAMP, price REAL, currency_id TEXT, description TEXT, city TEXT, activities TEXT, topics TEXT, 
        sales_types TEXT);'''
        return await self.update(query)

    async def create_table_payments(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS payments (id SERIAL PRIMARY KEY, user_id BIGINT, currency TEXT, 
        total_amount INT, product_id INT, deal_id INT, telegram_payment_charge_id TEXT, provider_payment_charge_id TEXT, 
        create_time TIMESTAMP);'''
        return await self.update(query)

    async def create_table_newsletters(self) -> None:
        query = '''CREATE TABLE IF NOT EXISTS newsletters (user_id BIGINT PRIMARY KEY, reminder TIMESTAMP);'''
        return await self.update(query)

    async def add_payment(self, user_id: int, payment_data: SuccessfulPayment) -> None:
        time_now = datetime.now()
        currency = payment_data.currency
        total_amount = payment_data.total_amount
        product_id = int(payment_data.invoice_payload.split(':')[0])
        deal_id = int(payment_data.invoice_payload.split(':')[1])
        telegram_payment_charge_id = payment_data.telegram_payment_charge_id
        provider_payment_charge_id = payment_data.provider_payment_charge_id
        query = '''INSERT INTO payments (user_id, currency, total_amount, product_id, deal_id, 
        telegram_payment_charge_id, provider_payment_charge_id, create_time) VALUES ($1, $2, $3, $4, $5, $6, $7, $8);'''
        return await self.update(query, user_id, currency, total_amount, product_id, deal_id,
                                 telegram_payment_charge_id, provider_payment_charge_id, time_now)

    async def update_table_products(self, products_list: List[dict]) -> None:
        products_cities = json.loads(config.products_cities.get_secret_value())
        products_cities = {int(key): value for key, value in products_cities.items()}

        truncate_query = '''TRUNCATE TABLE products;'''
        await self.update(truncate_query)
        for product in products_list:
            product_id = product.get('id')
            name = product.get('name')
            active_from = datetime.strptime(product.get('dateActiveFrom').split('+')[0], '%Y-%m-%dT%H:%M:%S')
            active_to = datetime.strptime(product.get('dateActiveTo').split('+')[0], '%Y-%m-%dT%H:%M:%S')
            price = float(product.get('PRICE'))
            currency_id = product.get('CURRENCY_ID')
            description = product.get('detailText')
            city_id = product.get('iblockSectionId')
            city = products_cities.get(city_id)

            activities = ','.join(active.get('value') for active in product.get('property102')) if product.get('property102') else ''
            topics = ','.join(topic.get('value') for topic in product.get('property104')) if product.get('property104') else ''
            sales_types = ','.join(sale_type.get('value') for sale_type in product.get('property106')) if product.get('property106') else ''

            insert_query = '''INSERT INTO products (id, name, active_from, active_to, price, currency_id, description, 
            city, activities, topics, sales_types) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11);'''
            await self.update(insert_query, product_id, name, active_from, active_to, price, currency_id,
                              description, city, activities, topics, sales_types)
        return

    async def get_products(self, city: str) -> List[Record]:
        query = 'SELECT * FROM products WHERE city = $1;'
        return await self.select(query, city)

    async def get_product_by_id(self, product_id: int) -> List[Record]:
        query = 'SELECT * FROM products WHERE id = $1;'
        return await self.select(query, product_id)

    async def add_button_count(self, user_id: int, button_name: str) -> None:
        time_now = datetime.now()
        query = '''INSERT INTO buttons_stat (user_id, button_name, count, last_press) VALUES ($1, $2, 1, $3) 
        ON CONFLICT (user_id, button_name) DO UPDATE SET count = buttons_stat.count + 1, last_press = $3 
        WHERE buttons_stat.user_id = $1 AND buttons_stat.button_name = $2;'''
        return await self.update(query, user_id, button_name, time_now)

    async def get_button_stat(self, user_id: int) -> List[Record]:
        query = '''SELECT * FROM buttons_stat WHERE user_id = $1 ORDER BY count DESC;'''
        return await self.select(query, user_id)

    async def get_start_message(self) -> str:
        query = '''SELECT start_message FROM admin_messages;'''
        result = await self.select(query)
        return result[0].get('start_message')

    async def set_start_message(self, start_message: str) -> None:
        query = '''UPDATE admin_messages SET start_message = $1;'''
        return await self.update(query, start_message)

    async def set_iml(self, user_id: int, iml: str) -> None:
        query = '''UPDATE users SET im_link_b24 = $2 WHERE user_id = $1;'''
        return await self.update(query, user_id, iml)

    async def set_b24_id(self, user_id: int, b24_id: int) -> None:
        query = '''UPDATE users SET b24_id = $2 WHERE user_id = $1;'''
        return await self.update(query, user_id, b24_id)

    async def set_lead_id(self, user_id: int, lead_id: int) -> None:
        query = '''UPDATE users SET lead_id = $2 WHERE user_id = $1;'''
        return await self.update(query, user_id, lead_id)

    async def set_bot_blocked(self, user_id: int, bot_blocked: bool) -> None:
        query = '''UPDATE users SET bot_blocked = $2 WHERE user_id = $1;'''
        return await self.update(query, user_id, bot_blocked)

    async def set_phone(self, user_id: int, phone: str) -> None:
        query = '''UPDATE users SET phone = $2 WHERE user_id = $1;'''
        return await self.update(query, user_id, phone)

    async def is_user_exist(self, user_id: int) -> bool:
        query = '''SELECT * FROM users WHERE user_id = $1;'''
        return bool(await self.select(query, user_id))

    async def is_b24_contact_exist(self, user_id: int) -> bool:
        query = '''SELECT b24_id FROM users WHERE user_id = $1;'''
        result = await self.select(query, user_id)
        return bool(result[0].get('b24_id'))

    async def get_user_deals(self, user_id: int) -> List[Record]:
        query = '''SELECT * FROM deals WHERE user_id = $1;'''
        return await self.select(query, user_id)

    async def get_user_deal_by_product_id(self, user_id: int, product_id: int) -> List[Record]:
        query = '''SELECT * FROM deals WHERE user_id = $1 AND product_id = $2 AND paid = FALSE;'''
        return await self.select(query, user_id, product_id)

    async def get_user_payed_deal_by_product_id(self, user_id: int, product_id: int) -> List[Record]:
        query = '''SELECT * FROM deals WHERE user_id = $1 AND product_id = $2 AND paid = TRUE;'''
        return await self.select(query, user_id, product_id)

    async def get_user_deal_by_deal_id(self, deal_id: int) -> List[Record]:
        query = '''SELECT * FROM deals WHERE deal_id = $1;'''
        return await self.select(query, deal_id)

    async def set_paid_deal(self, deal_id: int) -> None:
        """Отмечает сделку оплаченной"""
        query = '''UPDATE deals SET paid = True WHERE deal_id = $1;'''
        return await self.update(query, deal_id)

    async def add_new_user(self, user_id: int, username: Optional[str], full_name: str) -> None:
        query = '''INSERT INTO users (user_id, username, full_name) VALUES ($1, $2, $3)'''
        return await self.update(query, user_id, username, full_name)

    async def get_user_data(self, user_id: int) -> List[Record]:
        query = '''SELECT * FROM users WHERE user_id = $1;'''
        return await self.select(query, user_id)

    async def get_user_list_for_reminder(self) -> List[Record]:
        query = '''SELECT DISTINCT bs.user_id
                    FROM buttons_stat bs
                    WHERE bs.button_name ILIKE '%Купить%'
                        AND NOT EXISTS (
                            SELECT 1
                            FROM payments p
                            WHERE p.user_id = bs.user_id
                                AND p.create_time >= CURRENT_DATE - INTERVAL '1 month'
                        )
                        AND bs.last_press <= CURRENT_TIMESTAMP - INTERVAL '1 day'
                        AND NOT EXISTS (
                            SELECT 1
                            FROM newsletters n
                            WHERE n.user_id = bs.user_id
                                AND n.reminder >= CURRENT_DATE - INTERVAL '1 month'
                        );'''
        return await self.select(query)

    async def get_all_users(self) -> List[Record]:
        query = '''SELECT * FROM users;'''
        return await self.select(query)

    async def add_reminder_time(self, user_id: int) -> None:
        time_now = datetime.now()
        query = '''INSERT INTO newsletters (user_id, reminder) VALUES ($1, $2) 
        ON CONFLICT (user_id) DO UPDATE SET reminder = $2;'''
        return await self.update(query, user_id, time_now)

    async def is_filled_out_the_form(self, user_id: int) -> bool:
        query = '''SELECT * FROM users WHERE 
        activities IS NOT NULL 
        AND topics IS NOT NULL 
        AND sales_types IS NOT NULL 
        AND user_id = $1;'''
        result: List[Record] = await self.select(query, user_id)
        return bool(result)

    async def set_user_form_result(self, user_id: int, activities: str, topics: str, sales_types: str) -> None:
        query = 'UPDATE users SET activities = $2, topics = $3, sales_types = $4 WHERE user_id = $1;'
        return await self.update(query, user_id, activities, topics, sales_types)

    async def set_user_city(self, user_id: int, new_city: str) -> None:
        query = 'UPDATE users SET city = $2 WHERE user_id = $1;'
        return await self.update(query, user_id, new_city)

    async def personal_events_counter(self, user_id: int) -> int:
        user_data: List[Record] = await self.get_user_data(user_id)
        user_city = user_data[0].get('city')
        products: List[Record] = await self.get_products(user_city)
        personal_products_counter = 0
        user_activities = set(user_data[0].get('activities').split(','))
        user_topics = set(user_data[0].get('topics').split(','))
        user_sales_types = set(user_data[0].get('sales_types').split(','))
        for product in products:
            activities = set(product.get('activities').split(','))
            topics = set(product.get('topics').split(','))
            sales_types = set(product.get('sales_types').split(','))

            if user_activities.intersection(activities) and user_topics.intersection(topics) \
                    and user_sales_types.intersection(sales_types):
                personal_products_counter += 1
        return personal_products_counter


