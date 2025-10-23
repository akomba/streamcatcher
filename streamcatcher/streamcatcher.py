#!/usr/bin/env python
import os
import sys
import glx.helper as helper
from glx.collection import Collection
import datetime
import time
#import glx.app.arghandler
import argparse
import glx.apphelper

APPNAME = "streamcatcher"
__version__ = "0.5"
    
# app default config
CONFIG_TEMPLATE = {
    "streamcatcher_id":False,
    "reward_id":False,
    "reward_amount":False,
    "stream_folder": ".streamcatcher",
    "name": "streamcatcher"
}

def main():
    parser = glx.apphelper.setup_parser(__version__,APPNAME)

    # this app's specific arguments
    parser.add_argument("--on", action="store_true")
    parser.add_argument("--off", action="store_true")
    args = parser.parse_args()

    glx.apphelper.process_common_args(args,__version__,APPNAME)

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
    print("Streamcatcher interact start!")
    config = helper.load_app_config(community_name,APPNAME)
    collection = Collection(community_name,config["collection_id"])
    card = collection.card(card_id)
    card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
    print("Streamcatcher click on card "+str(card_id)+" detected, added +"+str(config["reward_amount"])+" to reward attribute ("+str(config["reward_id"])+")")
    #card.remove_attribute(config["streamcatcher_id"])
if __name__ == "__main__":
    main()
