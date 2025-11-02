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
__version__ = "0.7"
CONFIG_TEMPLATE = "config_template.toml"

def cli():
    parser = glx.apphelper.setup_parser()
    # this app's specific arguments
    parser.add_argument("--on", action="store_true") # should check if mcq+solution set
    parser.add_argument("--off", action="store_true")
    parser.add_argument("--solution") # the winning choice
    parser.add_argument("-s","--status", action="store_true") # status of streamcatcher
    args = parser.parse_args()
    community_name = glx.apphelper.process_common_args(args,__version__,APPNAME)
    print("Community:",community_name)
    
    config_template = os.path.join(os.path.dirname(os.path.abspath(__file__)),CONFIG_TEMPLATE)
    config = helper.load_app_config(community_name,APPNAME,config_template)
    if not config:
        return False

    collection = Collection(community_name,config["collection_id"])
    
    if args.on:
        deploy_stamp = datetime.datetime.now().isoformat()
        stname = deploy_stamp.replace(":","_").replace(".","_")
        struct = {"status":"deployed","deployed_at":deploy_stamp}
        
        # check sc attribute interactivity type
        scatt = collection.attribute(config["streamcatcher_id"],raw=True)
        print("Streamcatcher badge:",scatt["name"])
        if not scatt["enabled"]:
            print("Error: Selected Streamcatcher attribute is disabled. Enable it first. Exiting.")
            exit(0)
        if not scatt["is_interactive"]:
            # if not interactive, exit with error
            print("Error: Selected Stremacatcher attribute is not interactive.")
            print("Either update it to be interactive or select another attribute in the config.")
            exit(0)
        
        struct["interactive_config"]=scatt["interactive_config"]
        print("Intercativity type:",scatt["interactive_config"]["type"])
        if scatt["interactive_config"]["type"] == "multiple_choice":
            choices = [c["value"] for c in scatt["interactive_config"]["choices"]]
            print("Choices:")
            for counter,choice in enumerate(choices):
                print(counter+1,choice)
            print(" ")
            # if multiple selection, check for --solution and that it matches one of the selections
            if not args.solution:
                print("Error: you must specify a --solution that corresponds to one of the choices above.")
                exit(0)
            if not args.solution in choices:
                print("Error: The solution ("+str(args.solution)+") must be one of",",".join(choices))
                exit(0)
       
            struct["interactive_config"]["solution"]=args.solution

        helper.save_app_data(community_name,APPNAME,stname,struct)
        collection.add_attribute(config["streamcatcher_id"])
        print("streamcatcher badge successfully deployed.")

    elif args.off:
        # get latest stream folder
        open_stream,stname = helper.load_latest_app_data(community_name,APPNAME)
        if open_stream["status"] != "deployed":
            print("Can't find open stream, exiting.")
            exit()

        attribute = collection.attribute(config["streamcatcher_id"])
        instances = attribute.instances()
        clicked = []
        for inst in instances:
            if inst["interacted_at"]:
                print(inst["card_id"],"has interacted.")
                card = collection.card(inst["card_id"])
                #card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
                clicked.append(inst)
                
        # save the list who clicked
        print("Number of interactions:",len(clicked))
        open_stream["closed_at"] = datetime.datetime.now().isoformat()
        open_stream["clicked"] = clicked
        open_stream["status"] = "closed"
        fname = helper.save_app_data(community_name,APPNAME,stname,open_stream)
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
    print("data:",data)
    # {'interacted_value': 'dragons'} 
    if data and "interacted_value" in data and data["interacted_value"] == "dragons":
        config = helper.load_app_config(community_name,APPNAME)
        collection = Collection(community_name,config["collection_id"])
        card = collection.card(card_id)
        card.increase_attribute_value(config["reward_id"],config["reward_amount"]) # deploy reward
        print("Streamcatcher click on card "+str(card_id)+" detected, added +"+str(config["reward_amount"])+" to reward attribute ("+str(config["reward_id"])+")")
    print("--------")
    #card.remove_attribute(config["streamcatcher_id"])
