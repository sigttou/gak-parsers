#!/usr/bin/env python3.11
import requests


def main():
    base_url = "https://ticket.grazerak.at/backend/events/"
    events_ep = "futurePublishedEvents"

    print("<!DOCTYPE html>")
    print("<html>")
    print("<body>")
    for event in requests.get(base_url + events_ep).json():
        print("<h1>" + event["title"] + "</h1>")

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

        print("<p>Available: " + str(avail_cnt) + "</p>")
        print("<p>Sold (w/o Sponsors, VIP): " + str(sold_cnt) + "</p>")
        est_vip = 896  # from SKN home game, not verified
        print("<p>Sold (w est. 896 Sponsors, VIP): " +
              str(sold_cnt + est_vip) + "</p>")
        print("<br>")

    print("</body>")
    print("</html>")
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
    main()
