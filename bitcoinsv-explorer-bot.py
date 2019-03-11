import requests
import math
import json
from telegram.ext import (Updater, CommandHandler,
                          MessageHandler, Filters, BaseFilter)
import telegram
import logging

chain = "bitcoin-sv"
updater = Updater(token="")
bot = telegram.Bot(token="")
dispatcher = updater.dispatcher

# logging.basicConfig( format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

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

class Filter_address_no(BaseFilter):
    def filter(self, message):
        return len(message.text) != 34, 64

class Filter_tx(BaseFilter):
    def filter(self, message):
        return len(message.text) == 64

def start(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="Hello, I am a bot for the Bitcoin SV Blockchain Explorer. You can use these command:\n"
                     "/check_address\n"
                     "/check_transactions\n"
                     "/blockchainstatus\n"
                     "/price\n"
                     "/start (this message)\n"
                     "\n"
                     "<b>If you add this bot in a chat group, do not give him permission to read the messages</b>\n", parse_mode=telegram.ParseMode.HTML)

def check_address(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the Bitcoin address to check the balance")

def check_transactions(bot, update):
    bot.send_message(chat_id=update.message.chat_id,
                     text="Send me the transaction hash to get transaction information")

def addr(bot, update):
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
    tx = (update.message.text)

    # print(update.message.from.first_name + ": ")
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
    coinb = str(date["data"][tx]["transaction"]["is_coinbase"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Total Input Value BSV:</b> <code>{tivbsv}</code>" + "\n"
                     f"<b>Total Input Value USD:</b> <code>{tivusd}</code>" + "\n"
                     f"<b>Total Output Value BSV:</b> <code>{tovbsv}</code>" + "\n"
                     f"<b>Total Output Valie USD:</b> <code>{tovusd}</code>" + "\n"
                     f"<b>Size (byte):</b> <code>{sb}</code>" + "\n"
                     f"<b>Confirmations:</b> <code>{confi}</code>" + "\n"
                     f"<b>Fees:</b> <code>{fees} satoshi</code>" + "\n"
                     f"<b>Coinbase:</b> <code>{coinb}</code>", parse_mode=telegram.ParseMode.HTML)


def blockchainstatus(bot, update):
    status = "https://api.blockchair.com/" + chain + "/stats"
    status_get = requests.get(status)
    date = status_get.json()
    b = str(date["data"]["blocks"])
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
    link = "https://api.blockchair.com/" + chain + "/stats"
    link_get = requests.get(link)
    date = link_get.json()
    p = str(round(date["data"]["market_price_usd"], 2))
    vh = str("{:,}".format(date["data"]["volume_24h"]))
    pch = str(round(date["data"]["market_price_usd_change_24h_percentage"], 2))
    mcusd = str("{:,}".format(date["data"]["market_cap_usd"]))
    qu = str(date["data"]["market_dominance_percentage"])
    bot.send_message(chat_id=update.message.chat_id, text=f"<b>Price USD:</b> <code>{p}</code>" + "\n"
                     f"<b>Volume 24h:</b> <code>{vh}</code>" + "\n"
                     f"<b>Percent change 24h:</b> <code>{pch}%</code>" + "\n"
                     f"<b>Market cap USD:</b> <code>{mcusd}</code>" + "\n"
                     f"<b>Market Dominance: </b> <code>{qu}%</code>", parse_mode=telegram.ParseMode.HTML)

def addrno(bot, update):
    bot.send_message(chat_id=update.message.chat_id, text="This is not a valid Bitcoin address or transaction hash, check if it's correct.")

if __name__ == "__main__":
    filter_address = Filter_address()
    filter_tx = Filter_tx()
    filter_address_no = Filter_address_no()

    updater.dispatcher.add_handler(CommandHandler("start", start))

    updater.dispatcher.add_handler(
        CommandHandler("check_address", check_address))
    updater.dispatcher.add_handler(MessageHandler(filter_address, addr))

    updater.dispatcher.add_handler(CommandHandler(
        "check_transactions", check_transactions))
    updater.dispatcher.add_handler(MessageHandler(filter_tx, tx))

    updater.dispatcher.add_handler(CommandHandler(
        "blockchainstatus", blockchainstatus))
    updater.dispatcher.add_handler(CommandHandler("price", price))

    # updater.dispatcher.add_handler(MessageHandler(filter_address_no, addrno))

    # def echo(bot, update):
    #     # print(update.message.text)
    #     print(update.message.chat.first_name + ": ")
    #     print(update.message.text)
    #     # bot.send_message(chat_id=update.message.chat_id, text=update.message.text)
    #     # print(update.message.text)
    #
    # echo_handler = MessageHandler(Filters.text, echo)
    # updater.dispatcher.add_handler(echo_handler)

    # updater.start_polling()
    updater.start_polling(timeout=60)
    updater.idle()
