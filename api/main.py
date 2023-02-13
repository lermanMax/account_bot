from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel

from broadcast import send_messages, send_photo, send_messages_to_admins


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
    await send_messages_to_admins(
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
    await send_messages(
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
    await send_messages(
            user_id=tg_id,
            message=message,
        )
    return {"message": message}


@bot_api.post('/notice-of-activation/{tg_id}')
async def notification_of_activation(tg_id: int):
    """Отправляет уведомление о активации"""
    message = (
        f'Ваш аккаунт активирован',
    )
    await send_messages(
            user_id=tg_id,
            message=message,
        )
    return {"message": message}


@bot_api.post('/send-qr/{tg_id}')
async def send_qr(tg_id: int, photo: UploadFile = File(...)):
    """Отправляет изображение"""
    await send_photo(
            users_id=tg_id,
            message=f'Ваш QR-код',
            photo=await file.read(),
        )
    return {"message": f'Отправлено изображение {file.filename}'}
