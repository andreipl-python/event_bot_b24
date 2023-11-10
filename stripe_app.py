from aiogram import Bot
from flask import Flask, request

app = Flask(__name__)


class StripeMessage:
    @staticmethod
    def payment_message(stripe_event_data: dict) -> str:
        return ('Получены денежки на Stripe 💰\n\n'
                'Мероприятие: ')


@app.route("/stripe", methods=['POST'])
async def stripe_webhook_event():
    data = request.get_json()
    bot = Bot(token='')
    await bot.send_message(chat_id=6008255128, text=str(data))
    await bot.session.close()
    return "OK", 200

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=7272)
