import requests
import math
import json
import re
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, BaseFilter)
import telegram
import logging

chain = "bitcoin-sv"
updater = Updater(token="")
bot = telegram.Bot(token="")

dispatcher = updater.dispatcher

# uncomment for logging output:
logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

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

class Filter_tx(BaseFilter):
    def filter(self, message):
        return len(message.text) == 64

class Filter_rawhex(BaseFilter):
    def filter(self, message):
        # match broadcast hex minimum length 64
        regexTxhex = "^[a-fA-F0-9]{64,}$"
        pattern = re.compile(regexTxhex)
        if len(message.text) > 64:
            return bool(pattern.match(message.text))

def typing(bot, update):
        print(update.message)
        bot.send_chat_action(chat_id=update.message.chat_id, action=telegram.ChatAction.TYPING)

def start(bot, update):
    typing(bot, update)
    bot.send_message(chat_id=update.message.chat_id, text="Hello, I am a bot for the " + chain + " Blockchain Explorer. You can use these commands:\n"
                     "/check_address\n"
                     "/check_transaction\n"
                     "/send_rawhex\n"
                     "/blockchainstatus\n"
                     "/price\n"
                     "/start (this message)\n\n"

                     "<b>Support me: 1GpEXHB5d8tzKZR8XAkEqrUXNXfEaQDeky</b>", parse_mode=telegram.ParseMode.HTML)

def check_address(bot, update):
    typing(bot, update)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the Bitcoin address to check the balance")

def check_transaction(bot, update):
    typing(bot, update)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the transaction hash to get transaction information")

def send_rawhex(bot, update):
    typing(bot, update)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the raw hex and I will broadcast it for you.")

def addr(bot, update):
    typing(bot, update)
    addr = (update.message.text)

    # print(update.message.from.first_name + ": ")
    print(update.message.text)

    link = "https://api.blockchair.com/" + chain + "/dashboards/address/"
    get_address = requests.get(link+addr)
    date = get_address.json()
    satoshi = 0.00000001
    conv = date["data"][addr]["address"]["balance"]
    final = satoshi*float(conv)
    tbbsv = str(final)
    tbusd = str(date["data"][addr]["address"]["balance_usd"])
    t = str(date["data"][addr]["address"]["transaction_count"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Total Balance BSV:</b> <code>{tbbsv}</code>" + "\n"
                     f"<b>Total Balance USD:</b> <code>{tbusd}</code>" + "\n"
                     f"<b>Transactions:</b> <code>{t}</code>", parse_mode=telegram.ParseMode.HTML)

def tx(bot, update):
    typing(bot, update)
    tx = (update.message.text)

    print(update.message.text)

    link = "https://api.blockchair.com/" + chain + "/dashboards/transaction/"
    get_tx = requests.get(link+tx)
    date = get_tx.json()
    satoshi = 0.00000001
    conv = date["data"][tx]["transaction"]["input_total"]
    final = satoshi*float(conv)
    conv_two = date["data"][tx]["transaction"]["output_total"]
    final_two = satoshi*float(conv_two)
    current_block = date["context"]["state"]
    init_block = date["data"][tx]["transaction"]["block_id"]
    conf = current_block - init_block
    tivbsv = str(final)
    tivusd = str(date["data"][tx]["transaction"]["input_total_usd"])
    tovbsv = str(final_two)
    tovusd = str(date["data"][tx]["transaction"]["output_total_usd"])
    sb = str(date["data"][tx]["transaction"]["size"])
    confi = str(conf)
    fees = str(date["data"][tx]["transaction"]["fee"])
    feeUsd = str(float(tivusd) - float(tovusd))
    coinb = str(date["data"][tx]["transaction"]["is_coinbase"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Total Input Value BSV:</b> <code>{tivbsv}</code>" + "\n"
                     f"<b>Total Input Value USD:</b> <code>{tivusd}</code>" + "\n"
                     f"<b>Total Output Value BSV:</b> <code>{tovbsv}</code>" + "\n"
                     f"<b>Total Output Value USD:</b> <code>{tovusd}</code>" + "\n"
                     f"<b>Size (byte):</b> <code>{sb}</code>" + "\n"
                     f"<b>Confirmations:</b> <code>{confi}</code>" + "\n"
                     f"<b>Fee in Satoshi:</b> <code>{fees}</code>" + "\n"
                     f"<b>Fee in USD:</b> <code>{feeUsd}</code>" + "\n"
                     f"<b>Coinbase:</b> <code>{coinb}</code>", parse_mode=telegram.ParseMode.HTML)

def blockchainstatus(bot, update):
    typing(bot, update)
    status = "https://api.blockchair.com/" + chain + "/stats"
    status_get = requests.get(status)
    date = status_get.json()
    b = str(date["data"]["blocks"])
    bestBlockTime = str(date["data"]["best_block_time"])
    bh = str(date["data"]["blocks_24h"])
    th = str("{:,}".format(date["data"]["transactions_24h"]))
    md = str("{:,}".format(date["data"]["difficulty"]))
    hr = str(date["data"]["hashrate_24h"])
    t = str("{:,}".format(date["data"]["transactions"]))
    o = str("{:,}".format(date["data"]["outputs"]))
    mt = str(date["data"]["mempool_transactions"])
    tfimusd = str(date["data"]["mempool_total_fee_usd"])
    tpsm = str(round(date["data"]["mempool_tps"], 2))
    mempoolSize = str(date["data"]["mempool_size"])
    cs = str("{:,}".format(round(date["data"]["circulation"] / 21000000000000, 3)))
    blockchainSize = convert_size(date["data"]["blockchain_size"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Block Height:</b> <code>{b}</code>" + "\n"
                     f"<b>Last Block (UTC):</b> <code>{bestBlockTime}</code>" + "\n"
                     f"<b>Blocks in 24h:</b> <code>{bh}</code>" + "\n"
                     f"<b>Transactions in 24h:</b> <code>{th}</code>" + "\n"
                     f"<b>Mining Difficulty:</b> <code>{md}</code>" + "\n"
                     f"<b>Hashrate 24h:</b> <code>{hr}</code>" + "\n"
                     f"<b>Transactions:</b> <code>{t}</code>" + "\n"
                     f"<b>Outputs:</b> <code>{o}</code>" + "\n"
                     f"<b>Mempool transactions:</b> <code>{mt}</code>" + "\n"
                     f"<b>Mempool Total fees (USD):</b> <code>{tfimusd}</code>" + "\n"
                     f"<b>Mempool Transactions per second:</b> <code>{tpsm}</code>" + "\n"
                     f"<b>Mempool Size:</b> <code>{mempoolSize}</code>" + "\n"
                     f"<b>Blockchain Size:</b> <code>{blockchainSize}</code>" + "\n"
                     f"<b>Circulation supply percentage:</b> <code>{cs}</code>", parse_mode=telegram.ParseMode.HTML)

def price(bot, update):
    typing(bot, update)
    link = "https://api.blockchair.com/" + chain + "/stats"
    link_get = requests.get(link)
    date = link_get.json()
    p = str(round(date["data"]["market_price_usd"], 2))
    vh = str("{:,}".format(date["data"]["volume_24h"]))
    pch = str(round(date["data"]["market_price_usd_change_24h_percentage"], 2))
    mcusd = str("{:,}".format(round(date["data"]["market_cap_usd"], 2)))
    qu = str(date["data"]["market_dominance_percentage"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Price USD:</b> <code>{p}</code>" + "\n"
                     f"<b>Percent change 24h:</b> <code>{pch}%</code>" + "\n"
                     f"<b>Market Dominance: </b> <code>{qu}%</code>" + "\n"
                     f"<b>Market cap USD:</b> <code>{mcusd}</code>" + "\n"
                     f"<b>Volume 24h:</b> <code>{vh}</code>", parse_mode=telegram.ParseMode.HTML)

def send_transaction(bot, update):
    typing(bot, update)
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the (signed) transaction Hex")

def sendTransaction(bot, update):
    typing(bot, update)
    values = {
        'rawtx': update.message.text
    }
    values = json.dumps(values)
    headers = {

      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
    request = requests.post('https://api.bitindex.network/api/tx/send', data=values, headers=headers)

    print(request.text)

    bot.send_message(chat_id=update.message.chat_id, text=f"<code>{request.text}</code>", parse_mode=telegram.ParseMode.HTML)

if __name__ == "__main__":

    filter_address = Filter_address()
    filter_tx = Filter_tx()
    Filter_rawhex = Filter_rawhex()

    updater.dispatcher.add_handler(CommandHandler("start", start))

    updater.dispatcher.add_handler(
        CommandHandler("check_address", check_address))
    updater.dispatcher.add_handler(MessageHandler(filter_address, addr))

    updater.dispatcher.add_handler(CommandHandler(
        "check_transaction", check_transaction))
    updater.dispatcher.add_handler(MessageHandler(filter_tx, tx))

    updater.dispatcher.add_handler(
        CommandHandler("send_rawhex", send_rawhex))

    updater.dispatcher.add_handler(CommandHandler(
        "blockchainstatus", blockchainstatus))
    updater.dispatcher.add_handler(CommandHandler("price", price))

    updater.dispatcher.add_handler(
        CommandHandler("sendtransaction", send_transaction))
    updater.dispatcher.add_handler(MessageHandler(Filter_rawhex, sendTransaction))

    updater.start_polling()
    updater.idle()
