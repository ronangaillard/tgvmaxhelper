#!/usr/bin/python
# -*- coding: UTF-8 -*-

import urllib, json
import smtplib
import argparse
from datetime import timedelta, datetime
import sys
import time
import locale

toSend = "Trains disponibles ce mois-ci : \n\n"

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

def parse_arguments():
    parser = argparse.ArgumentParser(description="TGV_Max_Alert")
    parser.add_argument('--hour', type=str, required=True, help="hour format : 11:18. Monitor between 11h00 to 18h00")
    parser.add_argument('--origine', type=str, required=True, help="train station origine")
    parser.add_argument('--destination', type=str, required=True, help="train station destination")
    parser.parse_args()
    args = parser.parse_args()
    return args

def is_args_valid(args):
    hour = args.hour.split(':', 1)
    if (int(hour[0]) > 0 and int(hour[0]) < 24 and int(hour[1]) > 0 and int(hour[1]) < 24):
        return hour
    print ("\033[31mHour bad formatted\033[0m")
    sys.exit(-1)

def prepare_url(args, searchDate):
    url = "https://ressources.data.sncf.com/api/records/1.0/search/?dataset=tgvmax&sort=date&facet=date&facet=origine&facet=destination"
    url += "&refine.origine=" + args.origine
    url += "&refine.destination=" + args.destination
    url += "&refine.date=" + searchDate
    return url

def send_email(args, message):
    credential = json.load(open("./secret.json"))
    fromaddr = credential["EMAIL"]["my_email"]
    toaddrs = credential["EMAIL"]["toaddrs"]
    subject = "TGV MAX [" + args.origine + " -> " + args.destination +  "]"

    msg = """From: %s\nTo: %s\nSubject: %s\n\n%s
        """ % (fromaddr, ", ".join(toaddrs), subject, message)

    server = smtplib.SMTP('smtp.gmail.com:587')
    server.starttls()
    server.login(credential["EMAIL"]["my_email"], credential["EMAIL"]["my_password"])
    server.sendmail(fromaddr, toaddrs, msg)
    server.quit()


def send_alert(data, args):
    global toSend

    message = "  - " + datetime.strptime(data["fields"]["date"], "%Y-%m-%d").strftime("%A %d %B") + " \t" +\
    data["fields"]["heure_depart"] +\
    " \t>>\t " + data["fields"]["heure_arrivee"] +\
    "\n"
    print "\033[32m" + message + "\033[0m\n"

    toSend += message

def search_train(data, my_hour, args):
    alert = False
    
    nb_train = len(data["records"])
    for i in range(0, nb_train):
        if (data["records"][i]["fields"]["od_happy_card"] == "OUI"):
            hour = data["records"][i]["fields"]["heure_depart"]
            hourIn = int(hour.split(':', 1)[0])
            if (int(my_hour[0]) <= hourIn and int(my_hour[1]) >= hourIn):
                send_alert(data["records"][i], args)
                alert = True
    if (alert == True):
        return True
    return False

def main():
    locale.setlocale(locale.LC_ALL, 'fr_FR')

    start_date = datetime.now()
    end_date = start_date + timedelta(days=31)

    for single_date in daterange(start_date, end_date):
        print single_date.strftime("Working on %Y-%m-%d")

        args = parse_arguments()
        hour = is_args_valid(args)
        url = prepare_url(args, single_date.strftime("%Y-%m-%d"))
        
        response = urllib.urlopen(url)
        data = json.loads(response.read())
        if search_train(data, hour, args) != True:
            print "Aucun train disponible ..."

    send_email(args, toSend)

if __name__ == '__main__':
    main()

