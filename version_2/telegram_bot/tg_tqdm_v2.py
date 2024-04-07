import telepot
from tqdm import tqdm


class _TelegramIO():
    def __init__(self, token, chat_id):
        self.bot = telepot.Bot(token)
        self.chat_id = chat_id
        self.text = self.prev_text = '<< Starting... >>'
        self.message_id = self.bot.sendMessage(chat_id, self.text)['message_id']

    def write(self, s):
        new_text = s.strip().replace('\r', '')
        if len(new_text) != 0:
            self.text = new_text

    def flush(self):
        if self.prev_text != self.text:
            if '%' in self.text:
                self.bot.editMessageText((self.chat_id, self.message_id), self.text)
                self.prev_text = self.text
                if '100%' in self.text:
                    self.bot.deleteMessage((self.chat_id, self.message_id))

def tg_tqdm(iterable, token, chat_id,
            desc=None, total=None, leave=True, ncols=None, mininterval=1.0, maxinterval=10.0,
            miniters=None, ascii=False, disable=False, unit='it',
            unit_scale=False, dynamic_ncols=False, smoothing=0.3,
            bar_format=None, initial=0, position=None, postfix=None,
            unit_divisor=1000, gui=False, **kwargs):

    tg_io = _TelegramIO(token, chat_id)
    return tqdm(iterable=iterable,
                desc=desc,
                total=total,
                leave=leave,
                file=tg_io,
                ncols=ncols,
                mininterval=mininterval,
                maxinterval=maxinterval,
                miniters=miniters,
                ascii=ascii,
                disable=disable,
                unit=unit,
                unit_scale=unit_scale,
                dynamic_ncols=dynamic_ncols,
                smoothing=smoothing,
                bar_format=bar_format,
                initial=initial,
                position=position,
                postfix=postfix,
                unit_divisor=unit_divisor,
                gui=gui,
                **kwargs)
