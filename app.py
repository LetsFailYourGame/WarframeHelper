from time import sleep

import flask
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, url_for
from requests.sessions import session
import python.warframeFileHandler as Wf
import python.warframeStatsAPI as Stats
from python.warframeData import *

# CONFIG
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///items.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.jinja_env.cache = {}

# DATABASE SETUP
db = SQLAlchemy(app, session_options={"autoflush": False})


# DB ITEM
class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    ducats = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(300), nullable=False)
    wtsMaxPrice = db.Column(db.Integer, default=0)
    rarity = db.Column(db.String(10), default="Rarity : Error")
    sub_items = db.relationship('SubItems', backref='mainItem', lazy=True)

    def __repr__(self):
        return f"Item('{self.name}', '{self.icon}', '{self.quantity}', " \
               f"'{self.ducats}' , '{self.wtsMaxPrice}', '{self.rarity}')"


# DB SUB_ITEM
class SubItems(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    icon = db.Column(db.String(300), nullable=False)
    wtsMaxPrice = db.Column(db.Integer, default=0)
    rarity = db.Column(db.String(10), default="Rarity : Error")
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), nullable=False)

    def __repr__(self):
        return f"Item('{self.name}', '{self.icon}', '{self.quantity}', " \
               f"'{self.ducats}', '{self.wtsMaxPrice}', '{self.rarity}')"


# DB BARO
class Baro(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    ducats = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(300), nullable=False)
    wtsMaxPrice = db.Column(db.Integer, default=0)
    rarity = db.Column(db.String(10), default="Rarity : Error")

    def __repr__(self):
        return f"Item('{self.name}', '{self.icon}', '{self.quantity}', " \
               f"'{self.ducats}' , '{self.wtsMaxPrice}', '{self.rarity}')"


# DB BARO
class BaroList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    quantity = db.Column(db.Integer, default=1)
    ducats = db.Column(db.Integer, default=0)
    icon = db.Column(db.String(300), nullable=False)
    wtsMaxPrice = db.Column(db.Integer, default=0)
    rarity = db.Column(db.String(10), default="Rarity : Error")

    def __repr__(self):
        return f"Item('{self.name}', '{self.icon}', '{self.quantity}', " \
               f"'{self.ducats}' , '{self.wtsMaxPrice}', '{self.rarity}')"


@app.route('/')
@app.route('/home')
def home():
    cTime, cIsDay = Stats.getCetusTime()
    eTime, eIsDay = Stats.getEarthTime()
    vTime, vIsHot = Stats.getVallisTime()
    cambTime, cambActive = Stats.getCambionTime()
    sortieRemaining, missions, boss = Stats.getCurrentSortie()
    event = Stats.getCurrentEvent()
    return render_template("home.html",
                           cTime=cTime, cIsDay=cIsDay, eTime=eTime, eIsDay=eIsDay, vTime=vTime,
                           vIsHot=vIsHot, cambTime=cambTime, cambActive=cambActive,
                           sortieRemaining=sortieRemaining, missions=missions, boss=boss, event=event)


@app.route('/delete/all')
def dropDatabase():
    db.drop_all()
    db.create_all()
    return flask.redirect(url_for("inv"))


# inventory handler
@app.route('/inventory', methods=["POST", "GET"])
def inv():
    # cards to render std: all db entries
    cardsToRender = Item.query.order_by(Item.wtsMaxPrice.desc()).all()

    # retrieve forms
    itemAdd = request.form.get("add", None)
    searchItems = request.form.get("search", None)

    if itemAdd:
        return flask.redirect(url_for("addItem", itemAdd=itemAdd))

    if searchItems:
        return flask.redirect(url_for("searchItem", searchItems=searchItems))

    return render_template("inventory.html", items=cardsToRender)


# add item function
def addItemToDB(itemAdd):
    # ADDING ITEMS TO INVENTORY | form data not empty
    if itemAdd:
        # extract quantity
        quantity = [int(s) for s in str(itemAdd).split() if s.isdigit()]
        # if it has quantity
        if quantity:
            # remove the quantity from string | name_sub-name_type
            itemAdd = itemAdd.replace(f' {str(quantity[0])}', '')
        itemAdd = itemAdd.replace(" ", "_").lower()

        if not Wf.validate(itemAdd):
            return flask.redirect(url_for("inv"))

        # check if item exists in db
        found_item = Item.query.filter_by(name=itemAdd).first()
        if found_item:
            return flask.redirect(url_for("inv"))
        else:
            # retrieve the icon
            icon = Wf.wmGetIcon(itemAdd)
            # retrieve all subItems
            subItems = Wf.wmGetSubItems(itemAdd)
            # check if string is not empty
            if subItems is not None:
                subItems = subItems.split(",")
            else:
                subItems = ""
            # max wts price
            orderList = Wf.wmMaxWtbPrice(itemAdd)
            if orderList:
                maxi = int(max(orderList, key=lambda ev: ev['platinum'])['platinum'])
            else:
                maxi = 0
            # retrieve ducats
            ducats = int(Wf.wmGetDucats(itemAdd))
            # retrieve rarity
            rarity = Wf.wmGetRarity(itemAdd)

            # save item in db with quantity
            if quantity:
                newItem = Item(name=itemAdd, icon=icon, ducats=ducats, wtsMaxPrice=maxi, quantity=quantity[0],
                               rarity=rarity)
                db.session.add(newItem)
            else:
                newItem = Item(name=itemAdd, icon=icon, ducats=ducats, wtsMaxPrice=maxi, rarity=rarity)
                db.session.add(newItem)
            db.session.commit()

            # save sub item info in db
            if subItems:
                item_id = Item.query.filter_by(name=itemAdd).first().id
                for subItemName in subItems:
                    sub_icon = Wf.wmGetIcon(subItemName)
                    orderList = Wf.wmMaxWtbPrice(subItemName)
                    sleep(1)
                    rarity = Wf.wmGetRarity(subItemName)
                    if orderList:
                        maxi = int(max(orderList, key=lambda ev: ev['platinum'])['platinum'])
                    else:
                        maxi = 0
                    if len(quantity) > 0:
                        newSubItem = SubItems(name=subItemName, icon=sub_icon, wtsMaxPrice=maxi,
                                              quantity=quantity[0], rarity=rarity, item_id=item_id)
                        db.session.add(newSubItem)
                    else:
                        newSubItem = SubItems(name=subItemName, icon=sub_icon, rarity=rarity, wtsMaxPrice=maxi,
                                              item_id=item_id)
                        db.session.add(newSubItem)

            db.session.commit()


# add item web handle
@app.route('/inventory/add/<itemAdd>', methods=["POST", "GET"])
def addItem(itemAdd):
    addItemToDB(itemAdd)
    return flask.redirect(url_for("inv"))


# search form function
@app.route('/inventory/search/<searchItems>', methods=["POST", "GET"])
def searchItem(searchItems):
    # SEARCHING ITEMS WITH FORM
    cardsToRender = []
    if searchItems:
        for item in Item.query.all():
            if searchItems in item.name:
                cardsToRender.append(item)
    return render_template("inventory.html", items=cardsToRender)


# sort item cards by name
@app.route('/inventory/sort/alphabetical')
def sortAlph():
    cardsToRender = Item.query.order_by(Item.name).all()
    return render_template("inventory.html", items=cardsToRender)


# sort item cards by value
@app.route('/inventory/sort/stonks')
def sortStonks():
    cardsToRender = Item.query.order_by(Item.wtsMaxPrice.desc()).all()
    return render_template("inventory.html", items=cardsToRender)


# delete function
def deleteItemFromDB(deleteItem):
    itemToDelete = Item.query.filter_by(name=deleteItem).first()
    if itemToDelete.sub_items:
        for item in itemToDelete.sub_items:
            db.session.delete(item)
    db.session.delete(itemToDelete)
    db.session.commit()


# update item in db
def updateItemInDB(itemName):
    item = Item.query.filter_by(name=itemName).first()
    orderList = Wf.wmMaxWtbPrice(item.name)

    if orderList:
        maxi = int(max(orderList, key=lambda ev: ev['platinum'])['platinum'])
    else:
        maxi = 0
    # update new price
    item.wtsMaxPrice = maxi

    for subItem in item.sub_items:
        orderList = Wf.wmMaxWtbPrice(subItem.name)
        if orderList:
            maxi = int(max(orderList, key=lambda ev: ev['platinum'])['platinum'])
        else:
            maxi = 0
        subItem.wtsMaxPrice = maxi

    db.session.commit()
    return item, orderList


## EDIT PAGE index
@app.route('/inventory/<itemName>', methods=["POST", "GET"])
def cardInfo(itemName):
    item, orderList = updateItemInDB(itemName)
    nameList = itemName.split("_")
    name = nameList[0].title() + " " + nameList[1].title()
    wObj = Warframe(name)
    return render_template("edit.html", item=item, orders=orderList, wObj=wObj)



## EDIT PAGE delete
@app.route('/delete/<deleteItem>', methods=["POST", "GET"])
def delete(deleteItem):
    deleteItemFromDB(deleteItem)
    return flask.redirect(url_for("inv"))


## EDIT PAGE save
@app.route('/save/<saveItem>', methods=["POST", "GET"])
def save(saveItem):
    changeQuantityAmount = request.form.get(saveItem, None)
    itemToChange = Item.query.filter_by(name=saveItem).first_or_404()

    if itemToChange:
        itemToChange.quantity = changeQuantityAmount
        db.session.commit()

    return flask.redirect(f"/inventory/{saveItem}")


@app.route('/selling')
def sell():
    return render_template("index.html")


@app.route('/buying')
def buy():
    return render_template("index.html")


# DEFAULT PAGE RESET
@app.route('/baro')
def baro():
    for item in Baro.query.all():
        db.session.delete(item)
    db.session.commit()

    for item in BaroList.query.all():
        db.session.delete(item)
    db.session.commit()

    for item in Item.query.all():
        baroItem = Baro.query.filter_by(name=item.name).first()
        if "set" not in item.name and "prime" in item.name:
            if baroItem:
                baroItem.wtsMaxPrice = item.wtsMaxPrice
                db.session.commit()
            else:
                itemDB = Item.query.filter_by(name=item.name).first()
                newBaroItem = Baro(name=item.name, icon=itemDB.icon, wtsMaxPrice=itemDB.wtsMaxPrice,
                                   quantity=itemDB.quantity, ducats=itemDB.ducats, rarity=itemDB.rarity)
                db.session.add(newBaroItem)

    db.session.commit()
    return render_template("baro.html", BaroItems=Baro.query.order_by(Baro.ducats.desc()).all(),
                           BaroList=BaroList.query.order_by(BaroList.ducats.desc()).all(), ducats=0, platin=0)


# SELL ITEMS TEMPORARY SITE
@app.route('/baro/sell/<item>')
def baroSell(item):
    # check for refresh/already existing item and display correct ducat, platin price
    if BaroList.query.filter_by(name=item).first():
        ducats = 0
        platin = 0
        for item in BaroList.query.all():
            ducats += item.quantity * item.ducats
            platin -= item.quantity * item.wtsMaxPrice
        return render_template("baro.html", BaroItems=Baro.query.order_by(Baro.ducats.desc()).all(),
                               BaroList=BaroList.query.order_by(BaroList.ducats.desc()).all(), ducats=ducats,
                               platin=platin)

    # save item
    savedBaroItem = Baro.query.filter_by(name=item).first()
    # add item to DB_BARO_LIST
    newBaroListItem = BaroList(name=savedBaroItem.name, icon=savedBaroItem.icon, wtsMaxPrice=savedBaroItem.wtsMaxPrice,
                               quantity=savedBaroItem.quantity, ducats=savedBaroItem.ducats,
                               rarity=savedBaroItem.rarity)
    # sessoin add new BaroListItem
    db.session.add(newBaroListItem)
    # remove item from DB_BARO
    db.session.delete(savedBaroItem)
    # commit & redirect
    db.session.commit()

    ducats = 0
    platin = 0
    for item in BaroList.query.all():
        ducats += item.quantity * item.ducats
        platin -= item.quantity * item.wtsMaxPrice

    return render_template("baro.html", BaroItems=Baro.query.order_by(Baro.ducats.desc()).all(),
                           BaroList=BaroList.query.order_by(BaroList.ducats.desc()).all(), ducats=ducats, platin=platin)


@app.route('/baro/delete/<item>')
def baroDelete(item):
    itemToDelete = BaroList.query.filter_by(name=item).first()
    ducats = 0
    platin = 0
    if itemToDelete:
        # add back to avalible items
        newBaroItem = Baro(name=itemToDelete.name, icon=itemToDelete.icon, wtsMaxPrice=itemToDelete.wtsMaxPrice,
                           quantity=itemToDelete.quantity, ducats=itemToDelete.ducats, rarity=itemToDelete.rarity)
        # remove from list
        db.session.add(newBaroItem)
        db.session.delete(itemToDelete)
        db.session.commit()

        for item in BaroList.query.all():
            ducats += item.quantity * item.ducats
            platin -= item.quantity * item.wtsMaxPrice
    return render_template("baro.html", BaroItems=Baro.query.order_by(Baro.ducats.desc()).all(),
                           BaroList=BaroList.query.order_by(BaroList.ducats.desc()).all(), ducats=ducats, platin=platin)


if __name__ == '__main__':
    app.run(debug=True)
