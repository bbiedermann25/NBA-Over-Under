import requests
import datetime
from bs4 import BeautifulSoup
import pandas as pd

data = pd.DataFrame()
start_date = datetime.datetime(2020, 12, 22)
end_date = datetime.datetime(2021, 7, 20)
url = 'https://www.covers.com/sports/NBA/matchups?selectedDate={}'.format(start_date.strftime('%Y-%m-%d'))
pts_plyd = {}

def getDate(content):
    index =  content.index(' data-game-date=')
    return datetime.datetime.strptime(content[index + 1][:10], '%Y-%m-%d')

def getHome(content):
    index =  content.index(' data-home-team-fullname-search=')
    return content[index + 1]

def getAway(content):
    index =  content.index(' data-away-team-fullname-search=')
    return content[index + 1]

def getHPoints(content):
    index =  content.index(' data-home-score=')
    return int(content[index + 1])

def getAPoints(content):
    index =  content.index(' data-away-score=')
    return int(content[index + 1])

def getLine(content):
    index =  content.index(' data-game-total=')
    return float(content[index + 1])

def checkOverUnder(home_points, away_points, line):
    if (home_points + away_points) > line:
        return 'Over'
    else:
        return 'Under'

while start_date <= end_date:

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'xml').find_all(class_= 'cmg_matchup_game_box cmg_game_data')

    for i in soup:
        row = {}
        content = str(i)
        x = content.find(';')
        content = content[:x]
        content = content.split('"')

        start_date = max(start_date, getDate(content))
        home = getHome(content)
        away = getAway(content)

        if ' data-away-score=' in content:
            home_points = getHPoints(content)
            away_points = getAPoints(content)

            if (home not in pts_plyd) or (away not in pts_plyd):

                if home in pts_plyd:
                    pts_plyd[home][0] += home_points
                    pts_plyd[home][1] += 1
                    pts_plyd[away] = [away_points, 1]

                else:
                    pts_plyd[home] = [home_points, 1]

                    if away in pts_plyd:
                        pts_plyd[away][0] += away_points
                        pts_plyd[away][1] += 1
                    else:
                        pts_plyd[away] = [away_points, 1]
            else:
                row['Home'] = home
                row['Away'] = away
                row['Home Points'] = home_points
                row['Away Points'] = away_points
                row['Avg Home Points'] = round(pts_plyd[home][0] / pts_plyd[home][1], 2)
                row['Avg Away Points'] = round(pts_plyd[away][0] / pts_plyd[away][1], 2)
                row['Line'] = getLine(content)
                row['Over/Under'] = checkOverUnder(home_points, away_points, getLine(content))
                
                data = data.append(row, ignore_index=True)
    start_date += datetime.timedelta(days=1)
    url = 'https://www.covers.com/sports/NBA/matchups?selectedDate={}'.format(start_date.strftime('%Y-%m-%d'))

print(data)



