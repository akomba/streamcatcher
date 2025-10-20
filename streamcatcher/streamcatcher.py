#!/usr/bin/env python
import os
import sys
import glx.helper as helper
from glx.collection import Collection
import datetime
import time
#import glx.app.arghandler
import argparse

APPNAME = "streamcatcher"
__version__ = "0.1"
    
# app default config
CONFIG_TEMPLATE = {
    "streamcatcher_id":False,
    "reward_id":False,
    "reward_amount":False,
    "stream_folder": ".streamcatcher",
    "name": "streamcatcher"
}

def main():
    # TODO
    #
    # can be executed with params
    # or works automatically when called without params
    # it checks 2 things:
    # 1. if the first card of the collection has the control attribute
    # 2. if there is an open stream
    #
    # if True  & False: opens streamcatcher
    # if True  & True:  does nothing
    # if False & False: does nothing
    # if False & True:  closes streamcatcher and distributes rewards
    # 
    # New version
    #
    # streamcatcher on: adds streamcatcher to all cards.
    # Watches for events.
    #
    # steramcatcher off: removes streamcatcher from all cards.
    #
    # 1. implement config in community folder
    # 2. integrate asyncio

    # check for config file
    # create if none

    # common stuff

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--version", action="store_true")
    parser.add_argument("-c", "--community")
    parser.add_argument("--on", action="store_true")
    parser.add_argument("--off", action="store_true")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        exit(0)

    # find community
    if args.community:
        # community is explicitly given
        community_name = args.community
    else:
        # get it from environment
        local_config = helper.load_local_config()
        if local_config:
            community_name = local_config["community_name"]
        else:
            print("No community name is given, exiting.")
            exit()
    
    print("Community:",community_name)

    
    config = helper.load_or_create_app_config(community_name,APPNAME,CONFIG_TEMPLATE)


    collection = Collection(community_name,config["collection_id"])
    
    if args.on:
        stname = datetime.datetime.now().isoformat().replace(":","_").replace(".","_")

        collection.add_attribute(config["streamcatcher_id"])
        os.makedirs(os.path.join(config["stream_folder"],stname),exist_ok=True)
       
        print("streamcatcher badge successfully deployed.")

    elif args.off:
        # get latest stream folder
        streamdir = sorted(os.listdir(config["stream_folder"]))[-1] 

        attribute = collection.attribute(config["streamcatcher_id"])
        instances = attribute.instances()
        clicked = []
        for inst in instances:
            if inst["interacted_at"]:
                print(inst["card_id"],"has interacted.")
                card = collection.card(inst["card_id"])
                #card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
                clicked.append(card.id)
                
        # save the list who clicked
        print("Number of interactions:",len(clicked))
        fname = os.path.join(config["stream_folder"],streamdir,"results.json")
        helper.save_as_json(fname,clicked)
        print("Interactions saved to",fname)

        # remove badges
        collection.remove_attribute(config["streamcatcher_id"])
        print("removed streamcatcher from cards")

    else:
        print("usage:")
        print("`streamcatcher --on` -- switches on streamcatcher")
        print("`streamcatcher --off` -- switches off streamcatcher and processes the results")

def interact(community_name, app_name, card_id, data=None):
    config = helper.load_app_config(community_name,APPNAME)
    collection = Collection(community_name,config["collection_id"])
    card = collection.card(card_id)
    card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
    print("Streamcatcher click on card "+str(card_id)+" detected, added +"+str(config["reward_amount"])+" to reward attribute ("+str(config["reward_id"])+")")
    #card.remove_attribute(config["streamcatcher_id"])
if __name__ == "__main__":
    main()
