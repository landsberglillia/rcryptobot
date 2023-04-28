from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from .models import Threadlist
from threading import Thread, Event
import ccxt
import random
import urllib.parse
from time import sleep
import json
# Create your views here.


thread_list = []


class MyThread(Thread):
    def __init__(self, min_val, max_val, interval_val, symbol_val, api_key, secret_key, password, exchange):
        super().__init__()
        self.min_val = min_val
        self.max_val = max_val
        self.interval_val = interval_val
        self.symbol_val = symbol_val
        self.api_key = api_key
        self.secret_key = secret_key
        self.password = password
        self.exchange = exchange
        self.remain = 0
        self._stop_event = Event()
        self.th_index = len(thread_list)

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            try:
                e_rate = self.exchange.fetch_ticker(self.symbol_val)

                rand_amount = random.randint(
                    int(self.min_val), int(self.max_val))
                sell_amount = rand_amount / e_rate['close']

                self.exchange.create_order(
                    self.symbol_val, 'market', 'sell', 0.01)

                balance = self.exchange.fetch_balance()

                remaining_eth = balance[self.symbol_val.split("/")[0]]['free']
                print(str(remaining_eth))
                Threadlist.objects.filter(
                    api_key=self.api_key).update(crypto_remain=str(remaining_eth))
                self.remain = remaining_eth
                # if remaining_eth < 0.05:
                #     # if remaining_eth < sell_amount*2:
                #     self._stop_event.set()
                #     thread_list.pop(self.th_index)
                #     Threadlist.objects.filter(
                #         api_key=self.api_key).delete()
                #     return
            except:

                self._stop_event.set()
                thread_list.pop(0)
                return

            sleep(int(self.interval_val))


def set_exchange(api_key, secret_key, password):
    exchange = ccxt.kucoin({
        'apiKey': api_key,
        'secret': secret_key,
        'password': password,
        'enableRateLimit': True,
    })

    exchange.set_sandbox_mode(True)

    return exchange


def init_thread():

    db_array = Threadlist.objects.all().values()
    for s_th in db_array:

        init_exchange = set_exchange(
            s_th['api_key'], s_th['secret_key'], s_th['password'])

        global thread_list
        thread_list.append(MyThread(api_key=s_th['api_key'], secret_key=s_th['secret_key'], password=s_th['password'],
                                    min_val=s_th['min_val'], max_val=s_th['max_val'], interval_val=s_th['interval_time'],
                                    symbol_val=s_th['marketing_symbol'], exchange=init_exchange))
        thread_list[-1].start()


# init_thread()


class Botthread(Thread):
    def __init__(self):
        super().__init__()
        self._stop_event = Event()

    def stop(self):
        self._stop_event.set()

    def run(self):
        while not self._stop_event.is_set():
            if len(Threadlist.objects.all().values()) != len(thread_list):
                for s_thread in thread_list:
                    s_thread.stop()
                    s_thread.join()

                init_thread()

            sleep(15)


botth = Botthread()
botth.start()


def index(request):

    context = {"selling_process": Threadlist.objects.all(), "exist": 2}

    return render(request, "fbot/index.html", context)


def register(request):

    ss = request.body
    input_string = ss.decode("utf-8")

    ss = urllib.parse.parse_qs(input_string)

    for key in ss:
        ss[key] = ss[key][0]

    exchange = set_exchange(
        ss['api_key'], ss['secret_key'], ss['api_password'])

    try:
        exchange.fetch_balance()
    except:
        return HttpResponse("incorrect")

    global thread_list
    thread_list.append(MyThread(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                                min_val=ss['min_val'], max_val=ss['max_val'], interval_val=ss['interval_time'],
                                symbol_val=ss['marketing_symbol'], exchange=exchange))
    thread_list[-1].start()
    new_record = Threadlist(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                            min_val=ss['min_val'], max_val=ss['max_val'], interval_time=ss['interval_time'],
                            marketing_symbol=ss['marketing_symbol'], crypto_remain="0")
    new_record.save()

    return HttpResponse("success")


def registerapp(request):

    ss = json.loads(request.body)

    exchange = set_exchange(
        ss['api_key'], ss['secret_key'], ss['api_password'])

    try:
        exchange.fetch_balance()
    except:
        return HttpResponse("incorrect")

    global thread_list
    thread_list.append(MyThread(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                                min_val=ss['min_val'], max_val=ss['max_val'], interval_val=ss['interval_time'],
                                symbol_val=ss['marketing_symbol'], exchange=exchange))
    thread_list[-1].start()
    new_record = Threadlist(api_key=ss['api_key'], secret_key=ss['secret_key'], password=ss['api_password'],
                            min_val=ss['min_val'], max_val=ss['max_val'], interval_time=ss['interval_time'],
                            marketing_symbol=ss['marketing_symbol'], crypto_remain="0")
    new_record.save()

    return HttpResponse("success")


def stopprocess(request):

    for s_thread in thread_list:
        s_thread.stop()
        s_thread.join()

    Threadlist.objects.all().delete()

    return HttpResponse("success")


def getremain(request):

    remain_data = Threadlist.objects.all().values()
    if len(remain_data) == 0:
        return HttpResponse('dsfsd')

    return JsonResponse({'foo': list(remain_data)})


def test(request):
    exchange = set_exchange("643d1a04f78d7100016f105b",
                            "fbedccf2-de24-47c5-8231-13bce4d9410d", "TRADEbest123!")
    sss = exchange.fetch_balance()
    t1 = sss["ETH"]['free']
    return HttpResponse(str(t1))
