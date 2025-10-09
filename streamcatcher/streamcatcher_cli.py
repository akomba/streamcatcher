#!/usr/bin/env python
import os
import sys
import glx.helper as helper
from glx.collection import Collection
import datetime
import time

APPNAME = "streamcatcher"
__version__ = "0.0.3"

def main():
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
    # TODO
    #
    # 1. implement config in community folder
    # 2. integrate asyncio
    # 3. 
    #
    if "--version" in sys.argv[1:]:
        print(__version__)
        exit(0)

    # check for config file
    # create if none
    config_template = {
        "streamcatcher_id":False,
        "reward_id":False,
        "reward_amount":False,
        "stream_folder": ".streamcatcher",
        "repeat": 1,
        "name": "streamcatcher"
    }
    config = helper.load_or_create_app_config(APPNAME,config_template)

    if len(sys.argv) == 2:
    
        # ok now we are in business
        collection = Collection(config["community_name"],config["collection_id"])
        
        if sys.argv[1] == "on":
            stname = datetime.datetime.now().isoformat().replace(":","_").replace(".","_")

            collection.add_attribute(config["streamcatcher_id"])
            os.makedirs(os.path.join(config["stream_folder"],stname),exist_ok=True)
       
            print("streamcatcher badge successfully deployed.")

        elif sys.argv[1] == "off":
            # get latest stream folder
            streamdir = sorted(os.listdir(config["stream_folder"]))[-1] 

            attribute = collection.attribute(config["streamcatcher_id"])
            instances = attribute.instances()
            clicked = []
            for inst in instances:
                if inst["interacted_at"]:
                    print(inst["card_id"],"has interacted.")
                    card = collection.card(inst["card_id"])
                    card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
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
        print("`streamcatcher on` -- switches on streamcatcher")
        print("`streamcatcher off` -- switches off streamcatcher and processes the results")

if __name__ == "__main__":
    main()
