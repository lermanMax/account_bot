from fastapi import FastAPI
from pydantic import BaseModel

from tg_bot import TGBot
from config import TG_ADMINS_ID


class SaleNotice(BaseModel):
    sale_id: str
    sale_time: str
    sale_sum: float
    vr_code: str
    saler: str


class ReturnNotice(BaseModel):
    sale_id: str
    sale_time: str
    sale_sum: float
    vr_code: str
    saler: str
    return_time: str
    reason_for_return: str
    description: str


bot_api = FastAPI(
    title='Личный Кабинет BotAPI',
    description='Эндпойтны для отправки уведомлений Промоутерам и Менеджерам'
)


@bot_api.get('/ping')
async def ping_admin():
    """Проверка работы апи. Отправляет уведомление админам бота"""
    for admin_id in TG_ADMINS_ID:
        TGBot.send_message(
            user_id=admin_id,
            message='api ping',
        )
    return


@bot_api.post('/notice-of-sale/{tg_id}')
async def notification_of_sale(tg_id: int, notice_msg: SaleNotice):
    """Отправляет уведомление о новой продаже"""
    message = (
        f'№{notice_msg.sale_id} от {notice_msg.sale_time} \n'
        f'оплачен на сумму {notice_msg.sale_sum} \n'
        f'через {notice_msg.vr_code} {notice_msg.saler}\n'
    )
    TGBot.send_message(
            user_id=tg_id,
            message=message,
        )
    return {"message": message}


@bot_api.post('/notice-of-return/{tg_id}')
async def notification_of_return(tg_id: int, notice_msg: ReturnNotice):
    """Отправляет уведомление о возврате"""
    message = (
        f'Отмена заказа:\n'
        f'№{notice_msg.sale_id} от {notice_msg.sale_time} \n'
        f'оплачен на сумму {notice_msg.sale_sum} \n'
        f'через {notice_msg.vr_code} {notice_msg.saler}\n'
        '\n'
        f'Время возврата: {notice_msg.return_time}\n'
        f'Причина: {notice_msg.reason_for_return}\n'
        f'Подробности: {notice_msg.description}\n'
    )
    TGBot.send_message(
            user_id=tg_id,
            message=message,
        )
    return {"message": message}
