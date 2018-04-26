import threading, time
from django.conf import settings
import logging
import telegram

from ..models import WhoisTbotModel
from .whois import Whois

logging.basicConfig(level=logging.DEBUG if settings.DEBUG else logging.INFO)

class TBot:
    updater_thread = None
    scheduler_thread = None
    storage = None
    token = ""
    await = dict()
    DEFAULT_KEYBOARD = [["/add", "/remove"], ["/whois", "/stop"], ["/list"]]

    # Class for return result from cmd dispatcher
    class CmdResponse:
        def __init__(self, text, buttons=None):
            self.text = text
            self.buttons = buttons

    def __init__(self, token):
        self.token = token
        self.bot = telegram.Bot(token=token)

        self.scheduler_thread = threading.Thread(target=self._scheduler, daemon=True)
        self.scheduler_thread.start()

    #
    #   Dispatch webhook url to telegram server
    def set_webhook_url(self, url, cert_file_path=""):
        try:
            with open(cert_file_path, "rb") as cert_file:
                self.bot.setWebhook(url, cert_file)
                logging.debug("Cert is send")
        except FileNotFoundError:
            self.bot.setWebhook(url)

    #   Remove binded webhook
    def delete_webhook_url(self):
        self.bot.deleteWebhook()

    def _scheduler(self):
        logging.info("Start scheduler")
        while True:
            try:
                logging.debug("Sheduler call update")
                r = WhoisTbotModel.list_notif()

                # Update exp date in db
                for key, value in r.items():
                    for item in value:
                        try:
                            wh = Whois.query(item["domain"])
                            WhoisTbotModel.update_domain(key, item["domain"], exp_date=wh.exp_date)
                        except Exception:
                            logging.exception("Scheduler")
                            pass

                r = WhoisTbotModel.list_notif()
                for key, value in r.items():
                    try:
                        text = "Уведомление о скорой окончании регистрации:"

                        for item in value:
                            text += "<code>Домен: {}</code>\n<code>Дата окончания регистрации: {}</code>".format(
                            item["domain"],
                            item["exp_date"]
                        )
                        # Send updates to user
                        self.bot.send_message(chat_id=key, text=text, parse_mode="html")

                        # update last notif date
                        for item in value:
                            WhoisTbotModel.domain_notif(key, item["domain"])

                    except Exception:
                        logging.exception("Sheduler user exception")
            except Exception:
                logging.exception("Scheduler error:")

            time.sleep(60 * 60) #60 minutes interval

    #   Webhook update data handler
    def put_update(self, update):
        if "message" in update:
            text = update["message"]["text"]
            res = ""
            user_id = int(update["message"]["from"]["id"])

            if user_id in self.await:
                if self.await[user_id] == "whois":
                    del self.await[user_id]
                    res = self._dispatch_cmd_whois(user_id, *text.split(" "))
                elif self.await[user_id] == "add":
                    del self.await[user_id]
                    res = self._dispatch_cmd_add(user_id, *text.split(" "))
                elif self.await[user_id] == "remove":
                    del self.await[user_id]
                    res = self._dispatch_cmd_remove(user_id, *text.split(" "))
            else:
                cmd, *args = text.split(" ")
                if cmd == "/help":
                    res = self._dispatch_cmd_help()
                elif cmd == "/start":
                    res = self._dispatch_cmd_start(user_id)
                elif cmd == "/stop":
                    res = self._dispatch_cmd_stop(user_id)
                elif cmd == "/add":
                    res = self._dispatch_cmd_add(user_id, *args)
                elif cmd == "/remove":
                    res = self._dispatch_cmd_remove(user_id, *args)
                elif cmd == "/whois":
                    res = self._dispatch_cmd_whois(user_id, *args)
                elif cmd =="/list":
                    res = self._dispatch_cmd_list(user_id)
                else:
                    res = self._dispatch_cmd_unknown(user_id)

            if res:
                self.bot.send_message(chat_id=user_id,
                                      text=res.text,
                                      parse_mode=telegram.ParseMode.HTML,
                                      reply_markup=telegram.ReplyKeyboardMarkup(res.buttons, one_time_keyboard=True) if res.buttons else None)

    def _dispatch_cmd_list(self, user_id):
        text = "\n".join(
            ["<code>Домен: {}</code>\n<code>Дата окончания регистрации: {}</code>\n".format(
                item["domain"], item["exp_date"]
            ) for item in WhoisTbotModel.list_domains(user_id)]
        )
        if not text:
            text = "Вы еще не зарегестрировали ни одного домена."
        return self.CmdResponse(text, self.DEFAULT_KEYBOARD)

    def _dispatch_cmd_add(self, user_id, *domains):
        text = ""
        if not domains:
            self.await[user_id] = "add"
            return self.CmdResponse("Введите доменное имя:")
        else:
            for item in domains:
                try:
                    wh = Whois.query(item)
                    if not wh.exp_date:
                        raise Exception
                    WhoisTbotModel.update_domain(user_id, domain=wh.name, exp_date=wh.exp_date)
                    text += "Домен {} добавлен.\n".format(item)
                except Exception:
                    text += "Домен {} не найден.\n".format(item)
        return self.CmdResponse(text, self.DEFAULT_KEYBOARD)

    def _dispatch_cmd_remove(self, user_id, *domains):
        text = ""
        if not domains:
            self.await[user_id] = "remove"
            domains = [item["domain"] for item in WhoisTbotModel.list_domains(user_id)]
            col = 3
            buttons = [domains[n:n+col] for n in range(0, len(domains), col)]
            return self.CmdResponse("Введите доменное имя:", buttons)
        else:
            for item in domains:
                try:
                    WhoisTbotModel.remove_domain(user_id, item)
                    text += "Домен {} удалён.\n".format(item)
                except Exception:
                    pass
        return self.CmdResponse(text, self.DEFAULT_KEYBOARD)

    def _dispatch_cmd_whois(self, user_id, *domains):
        text = ""
        if not domains:
            self.await[user_id] = "whois"
            return self.CmdResponse("Введите доменное имя:")
        else:
            try:
                wh = Whois.query(domains[0])
                text = "<code>Домен: {}</code>\n".format(wh.name)
                text += "<code>Registrar: {}</code>\n".format(wh.registrar)
                text += "<code>Дата создания: {}</code>\n".format(wh.create_date.strftime("%d.%m.%Y %H:%M:%S"))
                text += "<code>Дата обновления: {}</code>\n".format(wh.update_date.strftime("%d.%m.%Y %H:%M:%S"))
                text += "<code>Дата окончания регистрации: {}</code>\n".format(wh.exp_date.strftime("%d.%m.%Y %H:%M:%S"))
            except Exception:
                text = "<b>Доменное имя не найдено.</b>"

        return self.CmdResponse(text, self.DEFAULT_KEYBOARD)

    def _dispatch_cmd_help(self):
        return self.CmdResponse("/add [domain] - Отслеживать домен\n"
               "/remove [domain] - Убрать домен из отслеживаемых\n"
               "/whois [domain] - Информация о домене\n"
               "/stop - Прекратить работу\n"
               "/list - Список отслеживаемых доменов\n"
               "/help - показать подсказку", self.DEFAULT_KEYBOARD)

    def _dispatch_cmd_start(self, chat_id):
        r = self._dispatch_cmd_help()
        r.text = "<b>Уведомления окончания регистрации доменов *.ua</b>\n" + r.text
        return r

    def _dispatch_cmd_stop(self, chat_id):
        try:
            WhoisTbotModel.remove_user(chat_id)
            return self.CmdResponse("Все ваши отслеживаемые домены удалены!")
        except Exception:
            logging.exception("Error cmd stop")

    def _dispatch_cmd_unknown(self, chat_id):
        r = self._dispatch_cmd_help()
        r.text = "<b>Используйте следующие команды:</b>\n" + r.text
        return r
