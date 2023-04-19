#!/usr/bin/env python3
import requests
import jinja2
import praw
from datetime import datetime
from bs4 import BeautifulSoup


def get_datasets(url):
    html = requests.get(url).text
    soup = BeautifulSoup(html, features="lxml")
    html_table = soup.find("table")

    headings = [th.get_text() for th in
                html_table.find("tr").find_all("th")]
    datasets = []
    for row in html_table.find_all("tr")[1:]:
        dataset = zip(headings,
                      (td.get_text() for td in row.find_all("td")))
        datasets.append(tuple(dataset))

    return datasets


def get_table(url):
    datasets = get_datasets(url)
    table = []
    for ds in datasets:
        entry = {}
        entry['name'] = \
            ds[2][1].split('<')[0].encode().decode("unicode_escape")
        entry['points'] = \
            int(ds[9][1].split('<')[0].encode().decode("unicode_escape"))
        table.append(entry)

    return table


def get_gameplan(url):
    datasets = get_datasets(url)
    gameplan = []
    for ds in datasets:
        if not ds:
            # just fetch current season
            break
        entry = {}
        entry['date'] = ds[2][1].split('<')[0]
        entry['time'] = ds[3][1].split('<')[0]
        entry['home'] = \
            ds[4][1].split('<')[0].encode().decode("unicode_escape")
        entry['away'] = \
            ds[5][1].split('<')[0].encode().decode("unicode_escape")
        entry['res'] = ds[6][1].split('\\n')[0].split(' ')[0]
        entry['league'] = bool(ds[7][1][-1].strip())

        if not entry['res']:
            entry['res'] = "-:-"
        else:
            a = int(entry['res'].split(':')[0])
            b = int(entry['res'].split(':')[1])
            res = ''
            if a == b:
                res = 'D'
            elif entry['home'] == 'Grazer AK 1902':
                res = 'W' if a > b else 'L'
            else:
                res = 'L' if a > b else 'W'
            entry['res'] = res + ' (' + entry['res'] + ')'

        gameplan.append(entry)
    return gameplan


def get_next_games(gameplan):
    next_games = []
    for e in gameplan:
        dt = datetime.strptime(e['date'], "%d.%m.%Y").date()
        now = datetime.now().date()
        if dt >= now:
            # show todays game too
            next_games.append(e)
        if len(next_games) >= 2:
            break

    return next_games


def pub_sidebar(content):
    reddit = praw.Reddit(user_agent="GAK mod")
    subreddit = reddit.subreddit("grazerak")
    subreddit.wiki["config/sidebar"].edit(content=content)


def main():
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader("templates/"))
    sidebar_tmpl = jenv.get_template("sidebar.tmpl")
    gameplan_tmpl = jenv.get_template("gameplan.tmpl")
    table_url = "https://www.2liga.at/ajax.php?contelPageId=8686" + \
                "&file=/?proxy=daten/BL2/20222023/tabellen/tabelle" + \
                "_gesamt_1-23.html"
    table = get_table(table_url)

    gameplan_url = "https://www.2liga.at/ajax.php?contelPageId=8686" + \
                   "&file=/?proxy=daten/team/html/6457/spielplan.html"
    gameplan = get_gameplan(gameplan_url)
    next_games = get_next_games(gameplan)

    content = sidebar_tmpl.render(table=table, next_games=next_games)
    with open("output/sidebar.txt", 'w') as f:
        f.write(content)
    pub_sidebar(content)

    content = gameplan_tmpl.render(gameplan=gameplan)
    with open("output/gameplan.txt", 'w') as f:
        f.write(content)

    return


if __name__ == "__main__":
    main()