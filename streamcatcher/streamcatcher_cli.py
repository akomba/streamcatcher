#!/usr/bin/env python
import os
import sys
import glx.helper as helper
from glx.collection import Collection
import datetime
import time

APPNAME = "streamcatcher"
__version__ = "0.0.1"

def main():
    if "--version" in sys.argv[1:]:
        print(__version__)
        exit(0)

    # check for config file
    # create if none
    config = helper.load_app_config(APPNAME)
    if not config:
        config = {
                "streamcatcher_id":False,
                "reward_id":False,
                "reward_amount":False,
                "stream_folder": ".streamcatcher"
                }
        fn = helper.create_app_config(APPNAME,config)
        print("Config file created:",fn)
        print("Please fill it out carefully and run this app again")
        exit()



    if len(sys.argv) == 2:
    
        # confirm config
        print("Please confirm that config is correct:")
        print("-------")
        for k,v in config.items():
            print(k,":",v)

        print("-------")
        print("Pausing for 10 seconds")
        time.sleep(10)

        # ok now we are in business
        community_name = config["community"]
        collection = Collection(config["community"],config["collection"])
        
        if sys.argv[1] == "on":
            stname = datetime.datetime.now().isoformat().replace(":","_").replace(".","_")

            collection.add_attribute(config["streamcatcher_id"])
            os.makedirs(os.path.join(config["stream_folder"],stname),exist_ok=True)
       
            print("streamcatcher badge successfully deployed.")

        elif sys.argv[1] == "off":
            # get latest stream folder
            streamdir = sorted(os.listdir(config["stream_folder"]))[-1] 

            # these members clicked
            #members = community.members.attributes(stid,{"interacted_with":True})
            
            clicked = []
            for card in collection.cards():
                if card.attribute(config["streamcatcher_id"]).interacted_at():
                    print(card.id,"has interacted.")
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
