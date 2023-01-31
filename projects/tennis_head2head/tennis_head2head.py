import selenium.common.exceptions
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import PySimpleGUI as pg
import pandas as pd
import numpy as np
from time import sleep
import re


def etl(player):
    # Prep variables
    player = player.title()
    player_concat = player.replace(' ', '')
    player_lname = re.search(r'[^\s]*$', player).group()
    url = f'http://www.tennisabstract.com/cgi-bin/player-classic.cgi?p={player_concat}&f=ACareerqqw1'

    try:
        # Scrape the data table, clean it, and process calculations
        driver.get(url)
        sleep(3)
        item = driver.find_element(By.CSS_SELECTOR, 'table#matches.tablesorter')
        html = item.get_attribute("outerHTML")
        content = pd.read_html(html)
        df = data_clean(content[0], player_lname)
        output = win_calcs(player, df)

        return output

    except selenium.common.exceptions.NoSuchElementException as e:
        e_win = pg.Window('Error', [[pg.Text(f'Error, please check the spelling of player: {player} and try again')]])
        e_win.Read(timeout=3000, close=True)

        return False


def data_clean(content, player_lname):
    # Convert to dataframe and remove last row
    df = pd.DataFrame(content)

    df.drop(df.tail(1).index, inplace=True)

    # Extract year. This will help us determine how many times a player has entered a tournament
    df['year'] = df['Date'].str.extract(r'(.{4}\s*$)')

    # Determine whether a match was won or lost by player
    df['wl'] = np.where((df['Unnamed: 6'].apply(lambda i: re.search(player_lname, i).start()) + 1) < 8, 'W', 'L')

    return df


def win_calcs(player, df):
    # This gets us the number of entries into tournaments so we can calculate title win percent
    entries = df[['Tournament', 'year']].drop_duplicates()

    # Run all category calculations
    tot_win_perc = round(
        (len(df[df['wl'] == 'W']) / len(df)) * 100, 2)
    win_perc_grass = round(
        (len(df[(df['wl'] == 'W') & (df['Surface'] == 'Grass')]) / len(df[df['Surface'] == 'Grass'])) * 100, 2)
    win_perc_hard = round(
        (len(df[(df['wl'] == 'W') & (df['Surface'] == 'Hard')]) / len(df[df['Surface'] == 'Hard'])) * 100, 2)
    win_perc_clay = round(
        (len(df[(df['wl'] == 'W') & (df['Surface'] == 'Clay')]) / len(df[df['Surface'] == 'Clay'])) * 100, 2)
    win_perc_top10 = round(
        (len(df[(df['wl'] == 'W') & (df['vRk'] > 11)]) / len(df[df['vRk'] > 11])) * 100, 2)
    win_perc_top50 = round(
        (len(df[(df['wl'] == 'W') & (df['vRk'] > 51)]) / len(df[df['vRk'] > 51])) * 100, 2)
    win_perc_top100 = round(
        (len(df[(df['wl'] == 'W') & (df['vRk'] > 101)]) / len(df[df['vRk'] > 101])) * 100, 2)
    gs_titles = round(
        len(df[(df['Tournament'].isin(tourna_class.get('Grand Slam'))) & (df['wl'] == 'W') & (df['Rd'] == 'F')]), 2)
    gs_title_perc = round(
        gs_titles / len(entries[entries['Tournament'].isin(tourna_class.get('Grand Slam'))]) * 100, 2)
    master_titles = round(
        len(df[(df['Tournament'].isin(tourna_class.get('Masters'))) & (df['wl'] == 'W') & (df['Rd'] == 'F')]), 2)
    master_title_perc = round(
        master_titles / len(entries[entries['Tournament'].isin(tourna_class.get('Masters'))]) * 100, 2)

    # Create player portfolio layout
    output = [
        pg.Text(player),
        pg.Text(f'Total win %: {tot_win_perc}'),
        pg.Text(f'Total win % on grass court: {win_perc_grass}'),
        pg.Text(f'Total win % on hard court: {win_perc_hard}'),
        pg.Text(f'Total win % on clay court: {win_perc_clay}'),
        pg.Text(f'Total win % against opponents ranked top 10: {win_perc_top10}'),
        pg.Text(f'Total win % against opponents ranked top 50: {win_perc_top50}'),
        pg.Text(f'Total win % against opponents ranked top 100: {win_perc_top100}'),
        pg.Text(f'Total Grand Slam titles: {gs_titles}'),
        pg.Text(f'Grand Slam entries to title win %: {gs_title_perc}'),
        pg.Text(f'Total Masters titles: {master_titles}'),
        pg.Text(f'Masters entries to title win %: {master_title_perc}')
    ]

    return output


def display(layout1, layout2):
    stat_layout = [
        [layout1[0], pg.Push(), layout2[0]],
        [layout1[1], pg.Push(), layout2[1]],
        [layout1[2], pg.Push(), layout2[2]],
        [layout1[3], pg.Push(), layout2[3]],
        [layout1[4], pg.Push(), layout2[4]],
        [layout1[5], pg.Push(), layout2[5]],
        [layout1[6], pg.Push(), layout2[6]],
        [layout1[7], pg.Push(), layout2[7]],
        [layout1[8], pg.Push(), layout2[8]],
        [layout1[9], pg.Push(), layout2[9]],
        [layout1[10], pg.Push(), layout2[10]],
        [layout1[11], pg.Push(), layout2[11]],
        [pg.Push(), pg.Button('Close')]
    ]
    stat_window = pg.Window('Stats', stat_layout)

    while True:
        stat_event, stat_values = stat_window.Read()
        if stat_event in (pg.WIN_CLOSED, 'Close'):
            break
    stat_window.close()


# Tournament classification
tourna_class = {'Grand Slam': ['Australian Open',
                               'US Open',
                               'Wimbledon',
                               'Roland Garros'],
                'Masters'   : ['Paris Masters',
                               'Cincinnati Masters',
                               'Madrid Masters',
                               'Rome Masters',
                               'Indian Wells Masters',
                               'Monte Carlo Masters',
                               'Canada Masters',
                               'Shanghai Masters',
                               'Miami Masters']
                }

# Create driver
driver = uc.Chrome(headless=True)

# Create UI layout
layout = [
    [pg.Text('Enter Player Name')],
    [pg.InputText(key='player1', do_not_clear=True)],
    [pg.Text('VS')],
    [pg.Text('Enter Player Name')],
    [pg.InputText(key='player2', do_not_clear=True)],
    [pg.Button('Submit')]
]
window = pg.Window('Player vs Player', layout)

# Loop the main window based on event outcome
while True:
    event, values = window.Read()
    if event == pg.WIN_CLOSED:
        break
    elif event == 'Submit':
        while True:
            # Exit early if query is malformed
            p1 = etl(values['player1'])
            if (not p1) or (len(p1) == 0):
                break
            p2 = etl(values['player2'])
            if (not p2) or (len(p2) == 0):
                break

            display(p1, p2)
            break

window.close()
