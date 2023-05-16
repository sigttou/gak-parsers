#!/usr/bin/env python3.11
import sys
import os
import sqlite3
import requests
import jinja2


def init_db(db_file):
    conn = sqlite3.connect(db_file)
    conn.execute('''
    CREATE TABLE IF NOT EXISTS EVENTS
    (
    ID          TEXT        PRIMARY KEY NOT NULL,
    TITLE       TEXT                    NOT NULL,
    DATETIME    DATETIME                NOT NULL,
    SELLFROM    DATETIME                NOT NULL,
    SELLTO      DATETIME                NOT NULL
    );''')

    conn.execute('''
    CREATE TABLE IF NOT EXISTS ENTRIES
    (
    MATCH       TEXT        NOT NULL,
    SOLD        INTEGER     NOT NULL,
    AVAILABLE   INTEGER     NOT NULL,
    TIMESTAMP   DATETIME    NOT NULL    DEFAULT CURRENT_TIMESTAMP
    );''')

    return conn


def update_db(conn, event, entry):
    conn.execute('''
    INSERT OR IGNORE INTO EVENTS
    (ID, TITLE, DATETIME, SELLFROM, SELLTO) VALUES
    (:id, :title, :dateTimeFrom, :publiclyAvailableFrom, :publiclyAvailableTo)
    ''', event)
    conn.execute('''
    INSERT INTO ENTRIES (MATCH, SOLD, AVAILABLE) VALUES
    (:id, :sold, :avail)''', entry)
    return


def main(db_file):
    conn = init_db(db_file)
    base_url = "https://ticket.grazerak.at/backend/events/"
    events_ep = "futurePublishedEvents"

    cur_path = os.path.dirname(os.path.abspath(__file__)) + '/'
    templ_path = cur_path + "templates/"
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(templ_path))
    ticket_tmpl = jenv.get_template("ticket-html.tmpl")

    events = []
    for event in requests.get(base_url + events_ep).json():
        event_url = base_url + event["id"] + "/"
        chk_url = event_url + "public-stadium-representation-config"
        content = requests.get(chk_url).json()
        sold_cnt = 0
        avail_cnt = 0
        for entry in content['sectorRepresentationConfigurations']:
            for e in entry['seatConfigurations']:
                if e['seatStatus'] == 'SOLD':
                    sold_cnt += 1
                if e['seatStatus'] == 'AVAILABLE':
                    avail_cnt += 1
        entry = {}
        entry["title"] = event["title"]
        entry["id"] = event["id"]
        entry["sold"] = sold_cnt
        entry["avail"] = avail_cnt

        update_db(conn, event, entry)
        events.append(entry)

    print(ticket_tmpl.render(events=events))
    conn.commit()

    conn.close()
    return

    # 5619 (sections 15-25)
    # 65 (VIP loge 1); likely sold out (?)
    # 60 (VIP loge 2); likely sold out (?)
    # 63 (VIP loge 3); likely sold out (?)
    # 65 (VIP loge 4); likely sold out (?)
    # 60 (VIP loge 5); likely sold out (?)
    # -581 (sector 24); usually not selling
    # -571 (sector 25); not selling
    # -416 (sector 15); not selling (Sponsors?)
    # -236 (sector 18); not selling (VIP?)
    # -156 (sector 18 VIP); sold out (?)
    # mx = 5619 - 581 - 571 - 416 - 236 - 156
    # vip_cnt = 65 + 60 + 63 + 65 + 60 + 156 + 236


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(sys.argv[0] + " <db_file>")
        sys.exit(-1)
    main(sys.argv[1])
