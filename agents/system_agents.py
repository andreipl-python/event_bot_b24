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
        logger = logging.getLogger('deactivate_products')
        product_list = await B24().get_product_list()
        for product in product_list:
            time_now = datetime.now()+timedelta(hours=2)
            active_to = datetime.strptime(product.get('dateActiveTo').split('+')[0], '%Y-%m-%dT%H:%M:%S')
            if time_now > active_to:
                await B24().deactivate_product(product.get('id'))
                logger.info(f'Deactivate product ID {product.get("id")}, {product.get("name")}')
                deal_list = await B24().get_deal_list_by_stage('FINAL_INVOICE')
                for deal_data in deal_list['result']:
                    deal_productrow = await B24().get_product_by_deal_id(deal_data['ID'])
                    try: deal_product_id = deal_productrow['result'][0]['PRODUCT_ID']
                    except Exception: continue
                    if deal_product_id == product.get('id'):
                        await B24().update_deal_stage(int(deal_data['ID']), 'LOSE')
                        logger.info(f'Lose deal ID {deal_data["ID"]}')
                        await asyncio.sleep(2)
            logger.info('Deactivate products successfully')
        await asyncio.sleep(1800)
