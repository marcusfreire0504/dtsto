#
# dtsto: day trade and swing trade operate
# ==========================================
#
# Este código faz parte de um algoritmo construído com o objetivo de atuar no mercado financeiro
# de forma independente
#
# @author      Isak Ruas <isakruas@gmail.com>
#
# @license     Este código é disponibilizado sobre a Licença Pública Geral (GNU) V3.0
#              Mais detalhes em: https://github.com/isakruas/dtsto/blob/master/LICENSE
#
# @link        Homepage:     http://nrolabs.com/dtsto/
#              GitHub Repo:  https://github.com/isakruas/dtsto/
#              README:       https://github.com/isakruas/dtsto/blob/master/README.md
#
# @version     1.0.00
#

from interpolation import interpolation

try:
    import thread
except ImportError:
    import _thread as thread

import time
import requests
import json
import statistics

high = []
last = []
low = []
lastVariation = []
vol = []
buyPrice = []
sellPrice = []


def watcher(pair):
    global high
    global last
    global low
    global lastVariation
    global vol
    global buyPrice
    global sellPrice

    if len(high) > 29:
        high.pop(0)

    if len(low) > 29:
        low.pop(0)

    if len(lastVariation) > 29:
        lastVariation.pop(0)

    if len(last) > 29:
        last.pop(0)

    if len(vol) > 29:
        vol.pop(0)

    if len(buyPrice) > 29:
        buyPrice.pop(0)

    if len(sellPrice) > 29:
        sellPrice.pop(0)

    request = requests.get('https://watcher.foxbit.com.br/api/Ticker?exchange=Foxbit&Pair=' + str(pair)).content

    data = json.loads(request.decode('utf-8'))

    if data['high'] not in high:
        high.append(data['high'])

    if data['low'] not in low:
        low.append(data['low'])

    if data['lastVariation'] not in lastVariation:
        lastVariation.append(data['lastVariation'])

    if data['last'] not in last:
        last.append(data['last'])

    if data['vol'] not in vol:
        vol.append(data['vol'])

    if data['buyPrice'] not in buyPrice:
        buyPrice.append(data['buyPrice'])

    if data['sellPrice'] not in sellPrice:
        sellPrice.append(data['sellPrice'])


def app():
    global high
    global last
    global low
    global lastVariation
    global vol
    global buyPrice
    global sellPrice

    print(
        "| high {high} | last {last} | low {low} | lastVariation {lastVariation} | vol {vol} | buyPrice {buyPrice} | "
        "sellPrice {sellPrice} |".format(
            high=high[-1], last=last[-1], low=low[-1], lastVariation=lastVariation[-1], vol=vol[-1],
            buyPrice=buyPrice[-1], sellPrice=sellPrice[-1]))

    coefficients = interpolation(image=last)
    polynomial = 'p(x) = '
    for a in range(0, len(coefficients)):
        polynomial += '+(' + str(coefficients[a]) + '*x**' + str(a) + ')'

    print('    ', polynomial)


def start_watcher():
    while True:
        try:
            # BRLXBTC / BRLXLTC / LTCXBTC / BRLXETH / ETHXBTC / TUSDXBRL / BTCXTUSD / ETHXTUSD / LTCXTUSD
            watcher('BRLXBTC')
        except Exception as e:
            print('    Exception watcher() - ', e)
        time.sleep(5)


def start_app():
    while True:
        try:
            app()
        except Exception as e:
            print('    Exception app() - ', e)
        time.sleep(5)


def main():
    thread.start_new_thread(start_watcher, ())
    thread.start_new_thread(start_app, ())
    while True:
        time.sleep(3600)
        pass


if __name__ == '__main__':
    main()
