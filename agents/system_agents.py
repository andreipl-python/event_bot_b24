import asyncio
import logging
from datetime import datetime, timedelta

from b24_models import B24
from sql import Database

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
)


async def update_products():
    while True:
        async with Database() as db:
            product_list = await B24().get_product_list()
            await db.update_table_products(product_list)
        logger = logging.getLogger('update_products')
        logger.info('Update table products successfully')
        await asyncio.sleep(900)


async def deactivate_products():
    while True:
        current_time = datetime.now()
        target_time = current_time.replace(hour=0, minute=0, second=0, microsecond=0)
        if current_time >= target_time:
            target_time += timedelta(days=1)
        delay = (target_time - current_time).total_seconds()
        await asyncio.sleep(delay)

        logger = logging.getLogger('deactivate_products')
        product_list = await B24().get_product_list()
        for product in product_list:
            time_now = datetime.now()
            active_to = datetime.strptime(product.get('dateActiveTo').split('+')[0], '%Y-%m-%dT%H:%M:%S')
            if time_now > active_to:
                await B24().deactivate_product(product.get('id'))
                logger.info(f'Deactivate product ID {product.get("id")}, {product.get("name")}')
            logger.info('Deactivate products successfully')


