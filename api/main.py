from fastapi import FastAPI, status
from pydantic import BaseModel

from tg_bot import TGBot
from config import TG_ADMINS_ID


class Notification(BaseModel):
    sale_id: int
    sale_time: str
    sale_sum: float
    vr_code: str
    saler: str


bot_api = FastAPI()


@bot_api.get('/ping')
async def ping_admin():
    for admin_id in TG_ADMINS_ID:
        TGBot.send_message(
            user_id=admin_id,
            message='api ping',
        )
    return


@bot_api.post('/notification/{tg_id}')
async def notification(notifi_msg: Notification):
    return {"message": notifi_msg}
