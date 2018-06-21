import urllib.request
import time
import json
import datetime
import market
from market import CryptoMarket

cm = CryptoMarket()
myMoney = cm.buying_power
print(myMoney)
lookingToBuy = True;
ethBought = 0
boughtValue = 0
sellValue = 0
interestGain = 1.003
interestGainAfterSell = .008
sellValueIncreasePercent = 1.00002
noSellYet = True

def apiCall(callType):
    if(callType == 'history'):
        return json.load(urllib.request.urlopen('https://min-api.cryptocompare.com/data/histominute?fsym=ETH&tsym=USD&limit=1439'))['Data']
    else:
        if(lookingToBuy == True):
            return cm.get_buy_price()
        else:
            return cm.get_sell_price()

while True:
    now = datetime.datetime.now()

    try:
        currentValue = apiCall('price')
        pastValues = apiCall('history')
    except:
        print("API call failed, restarting loop")
        continue

    total = 0
    for value in pastValues:
        total += value['low']

    ceiling = total/len(pastValues)

    #print('Ceiling: ' + str(ceiling) + ' Current Value: ' + str(currentValue) +' time - '+ str(now.hour) +':' + str(now.minute)+':'+str(now.second))

    if currentValue < ceiling and lookingToBuy == True and (currentValue < sellValue - (sellValue * interestGainAfterSell) or noSellYet == True):
        print('Time to buy')
        newCurrentValue = 0
        while True:
            try:
                currentValue = apiCall('price')
                time.sleep(5)
                newCurrentValue = apiCall('price')
            except:
                print("API call failed in buy loop, restarting loop")
                continue

            if currentValue < newCurrentValue:
                break

        ethBought = cm.buying_power * 0.98 / currentValue
        cm.buy(amount=ethBought, price=newCurrentValue)
        print('Buying ' +str(ethBought) +' ethereum at ' + str(newCurrentValue)+' time - '+ str(now.hour) +':' + str(now.minute)+':'+str(now.second))
        lookingToBuy = False
        boughtValue = newCurrentValue

    if boughtValue > 0 and currentValue >= (boughtValue * interestGain):
        while True:
            try:
                currentValue = apiCall('price')
                time.sleep(5)
                newCurrentValue = apiCall('price')
            except:
                print("API call failed in sell loop, restarting loop")
                continue

            print('Looping until ' + str(newCurrentValue) + ' is less than ' + str(currentValue))
            if newCurrentValue  < currentValue:
                break

        cm.sell(amount=ethBought, price=currentValue)
        print('Selling ' + str(ethBought) + ' ethereum worth ' + str(boughtValue) + ' for ' + str(currentValue) +' time - '+ str(now.hour) +':' + str(now.minute)+':'+str(now.second))
        boughtValue = 0
        sellValue = currentValue
        lookingToBuy = True
        noSellYet = False


    sellValue = sellValue * sellValueIncreasePercent
    time.sleep(5)
