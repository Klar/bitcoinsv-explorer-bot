import requests
import math
import json
import re
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, BaseFilter)
import telegram
import logging

import qrcode
from io import BytesIO

token = ""
bot = telegram.Bot(token=token)

# uncomment for logging output:
logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

logger = logging.getLogger(__name__)

network = "main"
apilink = "https://api.whatsonchain.com/v1/bsv/" + network

def convert_size(size_bytes):
   if size_bytes == 0:
       return "0B"
   size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
   i = int(math.floor(math.log(size_bytes, 1024)))
   p = math.pow(1024, i)
   s = round(size_bytes / p, 2)
   return "%s %s" % (s, size_name[i])

class Filter_address(BaseFilter):
    def filter(self, message):
        return len(message.text) == 34

class Filter_blockhash(BaseFilter):
    def filter(self, message):
        # print(message)
        return len(message.text) == 64 and message.text.startswith("000")

class Filter_txhash(BaseFilter):
    def filter(self, message):
        return len(message.text) == 64 and not message.text.startswith("000")

class Filter_rawhex(BaseFilter):
    def filter(self, message):
        # match broadcast hex minimum length 64
        regexTxhex = "^[a-fA-F0-9]{64,}$"
        pattern = re.compile(regexTxhex)
        if len(message.text) > 64:
            return bool(pattern.match(message.text))

def typing(update, context):
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

def help(update, context):
    address = "1GpEXHB5d8tzKZR8XAkEqrUXNXfEaQDeky"

    typing(update, context)
    update.message.reply_text("Hello, I am a bot for Bitcoin SV. You can use these commands:\n"
                     "/address\n"
                     "/sendhash\n"
                     "/broadcasthex\n"
                     "/mempool\n"
                     # "/blockchainstatus\n"
                     "/price\n"
                     "/supply\n"
                     "/start (this message)\n\n"
                     "/help (this message)\n\n"

                     f"<b>Support me: {address}</b>", parse_mode=telegram.ParseMode.HTML)

    qr = qrcode.QRCode(box_size=5)
    qr.add_data(address)
    qr.make()
    img = qr.make_image()
    bio = BytesIO()
    bio.name = address + '.jpeg'
    img.save(bio, 'JPEG')
    bio.seek(0)
    bot.send_photo(update.message.chat_id, photo=bio)

def check_address(update, context):
    typing(update, context)
    update.message.reply_text("Send me the Bitcoin address to check the balance")

def check_transaction(update, context):
    typing(update, context)
    update.message.reply_text("Send me the transaction hash to get transaction information")

def send_rawhex(update, context):
    typing(update, context)
    update.message.reply_text("Send me the raw hex and I will broadcast it for you.")

def mempool(update, context):
    typing(update, context)

    mempoolLink = apilink + "/mempool/info"
    response = requests.get(mempoolLink)
    response = response.json()
    mempoolSize = convert_size(response["bytes"])
    mempoolTXs = response["size"]
    mempoolUsage = convert_size(response["usage"])
    update.message.reply_text(f"<b>Mempool</b>\n"
                              f"<b>Size: </b> <code>{mempoolSize}</code>\n"
                              f"<b>Transactions: </b> <code>{mempoolTXs}</code>\n"
                              f"<b>Memory usage: </b> <code>{mempoolUsage}</code>\n", parse_mode=telegram.ParseMode.HTML)

def send_hash(update, context):
    typing(update, context)
    update.message.reply_text("Send me a TX or Block hash")

def supply(update, context):
    typing(update, context)

    supplyLink = "https://api.whatsonchain.com/v1/bsv/" + network + "/circulatingsupply"
    supply = requests.get(supplyLink).json()
    calcSupply = "{0:.2f}".format(supply / 21000000 * 100)
    supply = "{:,}".format(supply)

    update.message.reply_text(f"BSV Coin supply is: <b>{supply}</b> which is around <b>{calcSupply}%</b>\n", parse_mode=telegram.ParseMode.HTML)

def addr(update, context):
    typing(update, context)
    addr = (update.message.text)

    # print(update.message.from.first_name + ": ")
    # print(addr)
    link = apilink + "/address/" + addr + "/balance"
    addressLink = "https://whatsonchain.com/address/" + addr
    receipt = "https://" + network + ".whatsonchain.com/statement/" + addr

    balance = requests.get(link).json()
    satoshi = 0.00000001
    confirmed = '{0:.8f}'.format(satoshi*float(balance['confirmed']))
    unconfirmed = '{0:.8f}'.format(satoshi*float(balance['unconfirmed']))
    update.message.reply_text(f"<b>confirmed:</b> <code>{confirmed} BSV</code>\n"
                              f"<b>unonfirmed:</b> <code>{unconfirmed} BSV</code>\n"
                              f" * Explorer: <a href='{addressLink}'>{addr}</a>\n"
                              f" * Receipt: <a href='{receipt}'>Receipt</a>\n", parse_mode=telegram.ParseMode.HTML)

def txHash(update, context):
    typing(update, context)
    tx = (update.message.text)

    txlink = "https://whatsonchain.com/tx/" + tx

    update.message.reply_text(f"<a href='{txlink}'>{tx}</a>\n", parse_mode=telegram.ParseMode.HTML)

def blockHash(update, context):
    typing(update, context)
    blockhash = (update.message.text)

    blockhashlink = "https://whatsonchain.com/block/" + blockhash

    update.message.reply_text(f"<a href='{blockhashlink}'>{blockhash}</a>\n", parse_mode=telegram.ParseMode.HTML)

# def blockchainstatus(update, context):
#     typing(update, context)
#     status = "https://api.blockchair.com/" + chain + "/stats"
#     status_get = requests.get(status)
#     date = status_get.json()
#     b = str(date["data"]["blocks"])
#     bestBlockTime = str(date["data"]["best_block_time"])
#     bh = str(date["data"]["blocks_24h"])
#     th = str("{:,}".format(date["data"]["transactions_24h"]))
#     md = str("{:,}".format(date["data"]["difficulty"]))
#     hr = str(date["data"]["hashrate_24h"])
#     t = str("{:,}".format(date["data"]["transactions"]))
#     o = str("{:,}".format(date["data"]["outputs"]))
#     mt = str(date["data"]["mempool_transactions"])
#     tfimusd = str(date["data"]["mempool_total_fee_usd"])
#     tpsm = str(round(date["data"]["mempool_tps"], 2))
#     mempoolSize = str(date["data"]["mempool_size"])
#     cs = str("{:,}".format(round(date["data"]["circulation"] / 21000000000000, 3)))
#     blockchainSize = convert_size(date["data"]["blockchain_size"])
#     update.message.reply_text(f"<b>Block Height:</b> <code>{b}</code>" + "\n"
#                      f"<b>Last Block (UTC):</b> <code>{bestBlockTime}</code>" + "\n"
#                      f"<b>Blocks in 24h:</b> <code>{bh}</code>" + "\n"
#                      f"<b>Transactions in 24h:</b> <code>{th}</code>" + "\n"
#                      f"<b>Mining Difficulty:</b> <code>{md}</code>" + "\n"
#                      f"<b>Hashrate 24h:</b> <code>{hr}</code>" + "\n"
#                      f"<b>Transactions:</b> <code>{t}</code>" + "\n"
#                      f"<b>Outputs:</b> <code>{o}</code>" + "\n"
#                      f"<b>Mempool transactions:</b> <code>{mt}</code>" + "\n"
#                      f"<b>Mempool Total fees (USD):</b> <code>{tfimusd}</code>" + "\n"
#                      f"<b>Mempool Transactions per second:</b> <code>{tpsm}</code>" + "\n"
#                      f"<b>Mempool Size:</b> <code>{mempoolSize}</code>" + "\n"
#                      f"<b>Blockchain Size:</b> <code>{blockchainSize}</code>" + "\n"
#                      f"<b>Circulation supply percentage:</b> <code>{cs}</code>", parse_mode=telegram.ParseMode.HTML)

def price(update, context):
    typing(update, context)

    url = "https://genesis.bitdb.network/q/1FnauZ9aUH2Bex6JzdcV4eNX7oLSSEbxtN/ewogICJ2IjogMywKICAiZGIiOiBbInUiXSwKICAicSI6IHsKICAgICJmaW5kIjogeyAKICAgICAgIm91dC5zMSI6ICIxOWRiek1ERGc0alo0cHZZekxiMjkxblQ4dUNxRGE2MXpIIiwKICAgICAgImluLmUuYSI6ICIxMmVMVHh2MXZ5VWVKdHA1enFXYnFwZFd2ZkxkWjdkR2Y4IgogICAgfSwKICAgICJwcm9qZWN0IjogewogICAgICAiaW4uZS5hIjogMSwgIm91dC5zMSI6IDEsICJvdXQuczMiOiAxLCAib3V0LnM0IjogMSwgIm91dC5zNSI6IDEKICAgIH0sCiAgICAibGltaXQiIDogMQogIH0sCiAgInIiOiB7CiAgICAiZiI6ICJbLltdIHwgLm91dFswXSB8IHsgcHJlZml4OiAuczEsIGpzb246IC5zMywgY3VycmVuY3lfYWRkcjogLnM0LCBkYXRldGltZTogLnM1fSBdIgogIH0KfQo="
    api_token = '147GjmCAREtYv7FdfDivthzcmQLmdEhSYe'
    headers = {'key': api_token}
    response = requests.get(url, headers=headers)
    response = response.json()

    if response["u"]:
        response = response["u"]
    else:
        response = response["c"]

    response = json.loads(response[0]["json"])

    exchangeList = ""
    for exchangeName in response:
        exchangeList += exchangeName + " : " + str(response[exchangeName]["l"]) + "\n"

    update.message.reply_text(f"<code>{exchangeList}</code>", parse_mode=telegram.ParseMode.HTML)

def send_transaction(update, context):
    typing(update, context)
    update.message.reply_text("Send me the (signed) transaction Hex")

def broadcasthex(update, context):
    typing(update, context)
    values = {
        'rawtx': update.message.text
    }
    values = json.dumps(values)
    headers = {

      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    request = requests.post('https://api.bitindex.network/api/tx/send', data=values, headers=headers)

    # print(request.text)

    update.message.reply_text(f"<code>{request.text}</code>", parse_mode=telegram.ParseMode.HTML)

def main():
    updater = Updater(token=token, use_context=True)

    # initialize filters
    filter_address = Filter_address()
    filter_txhash = Filter_txhash()
    filter_blockhash = Filter_blockhash()
    filter_rawhex = Filter_rawhex()

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", help))
    dp.add_handler(CommandHandler("price", price))
    dp.add_handler(CommandHandler("address", check_address))
    dp.add_handler(CommandHandler("sendhash", send_hash))
    dp.add_handler(CommandHandler("broadcasthex", send_rawhex))
    dp.add_handler(CommandHandler("mempool", mempool))
    dp.add_handler(CommandHandler("supply", supply))

    # dp.add_handler(CommandHandler("blockchainstatus", blockchainstatus))

    dp.add_handler(MessageHandler(filter_address, addr))
    dp.add_handler(MessageHandler(filter_txhash, txHash))
    dp.add_handler(MessageHandler(filter_blockhash, blockHash))
    dp.add_handler(MessageHandler(filter_rawhex, broadcasthex))


    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Block until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    main()
