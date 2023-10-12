import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from b24_models import B24
from config_reader import config
import error_handler

from agents import system_agents
from handlers import user, admin
from sql import Database


async def create_sql_tables() -> str:
    async with Database() as db:
        for method_name in dir(db):
            if method_name.startswith('create_table_'):
                create_table_method = getattr(db, method_name)
                await create_table_method()
    return 'SQL tables created successfully'


async def main():
    dp = Dispatcher(storage=MemoryStorage())
    bot = Bot(config.bot_token.get_secret_value(), parse_mode="HTML")

    start_command = BotCommand(command='start', description='📅 Календарь событий')
    await bot.set_my_commands(commands=[start_command])

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    logger = logging.getLogger('SQL')
    logger.info(await create_sql_tables())

    dp.include_routers(
        admin.router, user.router, error_handler.router
    )

    asyncio.create_task(system_agents.update_products())
    asyncio.create_task(system_agents.deactivate_products())
    asyncio.create_task(system_agents.reminder(bot))
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types(), close_bot_session=True)


if __name__ == "__main__":
    asyncio.run(main())
