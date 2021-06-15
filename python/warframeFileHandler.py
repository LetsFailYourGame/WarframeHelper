###### VERRY EARLY IN DEVELOPMENT | QUITE BUGGY HANDLING A LOT OF REQUESTS AT THIS STAGE ######

import requests
uri_base = "https://api.warframe.market/v1/items/"


# WARFRAME_MARKET VALIDATE A ITEM
def validate(itemName):
    # request if the given item exists in WarframeMarket
    item = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    status_code = item.status_code
    # check for status code OK
    if status_code == 200:
        return True
    else:
        return False


def wmGetIcon(itemName):
    icon = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    if validate(itemName):
        icon = icon.json()['payload']['item']
        for item in icon['items_in_set']:
            if item['url_name'] == itemName:
                if "blueprint" in itemName:
                    return item['icon']
                elif "sub_icon" in item and item['sub_icon'] is not None:
                    return item['sub_icon']
                else:
                    return item['icon']
    else:
        return "404"


# WARFRAME_MARKET GET DUCATS FOR A ITEM
def wmGetDucats(itemName):
    # request the given item in WarframeMarket
    item = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    # if search string contains prime assume a Warframe was searched
    # check for validity
    if validate(itemName):
        # search the ducat price for given item in json response
        item = item.json()['payload']['item']
        for itemInSet in item['items_in_set']:
            if itemInSet['url_name'] == itemName:
                if "ducats" in itemInSet:
                    return int(itemInSet['ducats'])
    # else set ducats = false
    return 0


# WARFRAME_MARKET GET ORDERS FOR A ITEM
def wmGetOrders(itemName):
    # request orders from WarframeMarket
    orders = requests.get(url=f"{uri_base}{itemName}/orders", headers={"accept": "application/json"})
    # check for validity
    if validate(itemName):
        orderList = []
        # get the response as json
        orders = orders.json()['payload']
        # put all received orders in a list and return only valuable information as a dict
        for order in orders['orders']:
            if not order['user']['status'] == 'offline' and not order['visible'] == 'true' and order['region'] == 'en':
                orderList.append({
                    'platinum': order['platinum'],
                    'quantity': order['quantity'],
                    'order_type': order['order_type'],
                    'ingame_name': order['user']['ingame_name'],
                })
        return orderList
    return False


# WARFRAME_MARKET GET ORDERS FOR A ITEM
def wmMaxWtbPrice(itemName):
    # request orders from WarframeMarket
    orders = requests.get(url=f"{uri_base}{itemName}/orders", headers={"accept": "application/json"})
    # check for validity
    if validate(itemName):
        orderList = []
        # get the response as json
        orders = orders.json()['payload']
        # put all received orders in a list and return only valuable information as a dict
        for order in orders['orders']:
            if not order['user']['status'] == 'offline' and not order['visible'] == 'true' and order['region'] == 'en' \
                    and order['order_type'] == "buy":
                orderList.append({
                    'platinum': order['platinum'],
                    'quantity': order['quantity'],
                    'order_type': order['order_type'],
                    'ingame_name': order['user']['ingame_name'],
                })
        return orderList
    return None


# WARFRAME_MARKET GET ALL SUB_ITEMS FROM A SET
def wmGetSubItems(itemName):
    # request the given item in WarframeMarket
    item = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    # if search string contains prime assume a Warframe was searched
    subString = ""
    if validate(itemName) and "set" in itemName:
        item = item.json()['payload']['item']
        for itemInSet in item['items_in_set']:
            # retrieve information and skip if name is <itemName_prime_set>
            if itemInSet['url_name'] == itemName:
                continue

            subString += itemInSet['url_name'] + ","

        subString = subString.replace(subString[len(subString) - 1], ",")

        return subString[:len(subString) - 1]
    return None


#  WARFRAME_MARKET GET WIKI LINK
def wmGetWiki(itemName):
    # request the given item in WarframeMarket
    item = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    if validate(itemName):
        item = item.json()['payload']['item']
        for itemInSet in item['items_in_set']:
            return itemInSet['en']['wiki_link']
    return False


#  WARFRAME_MARKET GET RARITY
def wmGetRarity(itemName):
    # request the given item in WarframeMarket
    item = requests.get(url=f"{uri_base}{itemName}", headers={"accept": "application/json"})
    dropList = []
    if validate(itemName):
        item = item.json()['payload']['item']
        for itemInSet in item['items_in_set']:
            if itemInSet['url_name'] == itemName:
                for drop in itemInSet['en']['drop']:
                    dropList.append(drop['name'])
                if dropList:
                    if "Uncommon" in dropList[0]:
                        return "Uncommon"
                    if "Common" in dropList[0]:
                        return "Common"
                    if "Rare" in dropList[0]:
                        return "Rare"
    return "None"