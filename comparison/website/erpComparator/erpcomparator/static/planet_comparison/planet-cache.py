#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Planet cache tool.

"""

__authors__ = [ "Scott James Remnant <scott@netsplit.com>",
                "Jeff Waugh <jdub@perkypants.org>" ]
__license__ = "Python"


import os
import sys
import time
import dbhash
import ConfigParser

import planet


def usage():
    logger.notifyChannel("Usage: planet-cache [options] CACHEFILE [ITEMID]...")
    logger.notifyChannel("Examine and modify information in the Planet cache.")
    logger.notifyChannel("Channel Commands:")
    logger.notifyChannel(" -C, --channel     Display known information on the channel")
    logger.notifyChannel(" -L, --list        List items in the channel")
    logger.notifyChannel(" -K, --keys        List all keys found in channel items")
    logger.notifyChannel("Item Commands (need ITEMID):")
    logger.notifyChannel(" -I, --item        Display known information about the item(s)")
    logger.notifyChannel(" -H, --hide        Mark the item(s) as hidden")
    logger.notifyChannel(" -U, --unhide      Mark the item(s) as not hidden")
    logger.notifyChannel("Other Options:")
    logger.notifyChannel(" -h, --help        Display this help message and exit")
    sys.exit(0)

def usage_error(msg, *args):
    sys.exit(1)

def print_keys(item, title):
    keys = item.keys()
    keys.sort()
    key_len = max([ len(k) for k in keys ])

    for key in keys:
        if item.key_type(key) == item.DATE:
            value = time.strftime(planet.TIMEFMT_ISO, item[key])
        else:
            value = str(item[key])

def fit_str(string, length):
    if len(string) <= length:
        return string
    else:
        return string[:length-4] + " ..."


if __name__ == "__main__":
    cache_file = None
    want_ids = 0
    ids = []

    command = None

    for arg in sys.argv[1:]:
        if arg == "-h" or arg == "--help":
            usage()
        elif arg == "-C" or arg == "--channel":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "channel"
        elif arg == "-L" or arg == "--list":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "list"
        elif arg == "-K" or arg == "--keys":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "keys"
        elif arg == "-I" or arg == "--item":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "item"
            want_ids = 1
        elif arg == "-H" or arg == "--hide":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "hide"
            want_ids = 1
        elif arg == "-U" or arg == "--unhide":
            if command is not None:
                usage_error("Only one command option may be supplied")
            command = "unhide"
            want_ids = 1
        elif arg.startswith("-"):
            usage_error("Unknown option:", arg)
        else:
            if cache_file is None:
                cache_file = arg
            elif want_ids:
                ids.append(arg)
            else:
                usage_error("Unexpected extra argument:", arg)

    if cache_file is None:
        usage_error("Missing expected cache filename")
    elif want_ids and not len(ids):
        usage_error("Missing expected entry ids")

    # Open the cache file directly to get the URL it represents
    try:
        db = dbhash.open(cache_file)
        url = db["url"]
        db.close()
    except dbhash.bsddb._db.DBError, e:
        sys.exit(1)
    except KeyError:
        sys.exit(1)

    # Now do it the right way :-)
    my_planet = planet.Planet(ConfigParser.ConfigParser())
    my_planet.cache_directory = os.path.dirname(cache_file)
    channel = planet.Channel(my_planet, url)

    for item_id in ids:
        if not channel.has_item(item_id):
            sys.exit(1)

    # Do the user's bidding
    if command == "channel":
        print_keys(channel, "Channel Keys")

    elif command == "item":
        for item_id in ids:
            item = channel.get_item(item_id)
            print_keys(item, "Item Keys for %s" % item_id)

     elif command == "list":
        for item in channel.items(hidden=1, sorted=1):
            if hasattr(item, "title"):
                logger.notifyChannel("         " + fit_str(item.title, 70))
            if hasattr(item, "hidden"):
                logger.notifyChannel("         (hidden)")

    elif command == "keys":
        keys = {}
        for item in channel.items():
            for key in item.keys():
                keys[key] = 1

        keys = keys.keys()
        keys.sort()

       for key in keys:
            logger.notifyChannel("    " + key)

    elif command == "hide":
        for item_id in ids:
            item = channel.get_item(item_id)
            if hasattr(item, "hidden"):
                logger.notifyChannel(item_id + ": Already hidden.")
            else:
                item.hidden = "yes"

        channel.cache_write()

    elif command == "unhide":
        for item_id in ids:
            item = channel.get_item(item_id)
            if hasattr(item, "hidden"):
                del(item.hidden)
            else:
                logger.notifyChannel(item_id + ": Not hidden.")

        channel.cache_write()
