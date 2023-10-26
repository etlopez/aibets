from player_stats import PlayerStats

player = PlayerStats("Lebron James")
data = player.get_data_for_prediction("BOS")
for key, value in data.items():
    print(f"{key}: {value}")

from bs4 import BeautifulSoup
import requests
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from datetime import datetime
import undetected_chromedriver as uc
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


# Retrieve the ratings from WEBSITE #1
# https://hashtagbasketball.com/nba-defense-vs-position
# Output: A dataframe with the appropriate rankings for each team's stat
# Features ratings from for each of 5 positions
# team, pts, fg%, ft%, 3pm, reb, ast, stl, blk
def retrieve_ratings():
    team_names = {
        "NOP": "NO",
        "UTA": "UTAH",
        "SAS": "SA",
        "WAS" : "WSH",
        "NYK" : "NY",
        "BRO": "BKN",
        "OKL" : "OKC",
        "GSW" : "GS"
    }
    url = "https://hashtagbasketball.com/nba-defense-vs-position"
    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")
    data = []
    all_rows = doc.find_all('tr')
    for table in all_rows:
        cells = table.find_all("td")
        record = []
        for cell in cells:
            tokens = cell.text.replace("\n","").split(" ")
            if tokens[0] in team_names:
                tokens[0] = team_names[tokens[0]]
            record.append(tokens[0])
            if len(tokens) > 1:
                record.append(tokens[1])
        data.append(record)
    columns = ["POS", "TEAM", "TEAM RATING", "PTS", "PTS RATING", "FG%", "FG% RATING",
               "FT%", "FT% RATING", "3PM", "3PM RATING", "REB", "REB RATING",
               "AST", "AST RATING", "STL", "STL RATING", "BLK", "BLK RATING",
               "TO", "TO RATING"]
    df = pd.DataFrame(data, columns=columns)
    df = df.drop(index=0)
    return df


def retrieve_picks():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
    driver.get("https://app.prizepicks.com")
    time.sleep(20)
    # Check for a pop-up and close it
    try:
        popup =  driver.find_element(By.XPATH, '/html/body/div[2]/div[3]/div/div/div[1]/button')
        popup.click()
    except:
        print("Didn't find it.")
        pass

    try:
        nba_btn =  driver.find_element(By.XPATH, '//*[@id="board"]/div[1]/div/div/div[3]')
        nba_btn.click()
    except:
        print("Didn't find it.")
        pass

    try:
        projections = driver.find_elements(By.XPATH, '//*[@id="projections"]/div/div/div/div')
        print(len(projections))
        ret_projections = []
        ret_projections_imgs = []
        for projection in projections:
            img_element = projection.find_element(By.TAG_NAME,'img')
            ret_projections_imgs.append(img_element.get_attribute('src'))
            ret_projections.append(projection.text.split("\n"))

    except:
        print("Failed scraping.")
        pass
    return ret_projections, ret_projections_imgs


pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

##### MAIN ####
#determine_accuracy_of_model()
prize_picks, prize_picks_imgs = retrieve_picks()
ratings_df = retrieve_ratings()

print(prize_picks)