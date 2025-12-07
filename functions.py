import json
import re
import pandas as pd
import cloudscraper
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
import os
from matplotlib import font_manager as fm
from PIL import Image
from io import BytesIO
import requests
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from datetime import datetime
from highlight_text import ax_text, fig_text
from matplotlib.colors import to_rgba
from matplotlib.patches import Ellipse
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import base64
import hashlib
from bs4 import BeautifulSoup
import streamlit as st
from mplsoccer import Pitch, VerticalPitch, add_image

current_dir = os.path.dirname(os.path.abspath(__file__))

# Poppins fontunu yükleme
font_path = os.path.join(current_dir, 'fonts', 'Poppins-Regular.ttf')
prop = fm.FontProperties(fname=font_path)

bold_font_path = os.path.join(current_dir, 'fonts', 'Poppins-SemiBold.ttf')
bold_prop = fm.FontProperties(fname=bold_font_path)

def get_version_number():
    headers = {
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=0, i',
        'referer': 'https://www.google.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
    }
    
    response = requests.get("https://www.fotmob.com/", headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')
    version_element = soup.find('span', class_=lambda cls: cls and 'VersionNumber' in cls)
    if version_element:
        return version_element.text.strip()
    else:
        return None
    
version_number = get_version_number()
    
def get_xmas_pass():
    url = 'https://raw.githubusercontent.com/bariscanyeksin/streamlit_radar/refs/heads/main/xmas_pass.txt'
    response = requests.get(url)
    if response.status_code == 200:
        file_content = response.text
        return file_content
    else:
        print(f"Failed to fetch the file: {response.status_code}")
        return None

xmas_pass = get_xmas_pass()
    
def create_xmas_header(url, password, version_number):
        try:
            timestamp = int(datetime.now().timestamp() * 1000)
            request_data = {
                "url": url,
                "code": timestamp,
                "foo": version_number
            }
            
            json_string = f"{json.dumps(request_data, separators=(',', ':'))}{password.strip()}"
            signature = hashlib.md5(json_string.encode('utf-8')).hexdigest().upper()
            body = {
                "body": request_data,
                "signature": signature
            }
            encoded = base64.b64encode(json.dumps(body, separators=(',', ':')).encode('utf-8')).decode('utf-8')
            return encoded
        except Exception as e:
            return f"Error generating signature: {e}"
        
def headers_matchDetails(match_id):
    api_url = "/api/matchDetails?matchId=" + str(match_id)
    xmas_value = create_xmas_header(api_url, xmas_pass, version_number)
    
    headers = {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.fotmob.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-mas': f'{xmas_value}',
    }
    
    return headers

def headers_team(team_id):
    api_url = "/api/teams?id=" + str(team_id)
    xmas_value = create_xmas_header(api_url, xmas_pass, version_number)
    
    headers = {
        'accept': '*/*',
        'accept-language': 'tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7',
        'cache-control': 'no-cache',
        'pragma': 'no-cache',
        'priority': 'u=1, i',
        'referer': f'https://www.fotmob.com/',
        'sec-ch-ua': '"Google Chrome";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
        'x-mas': f'{xmas_value}',
    }
    
    return headers

def getFotmobData(fotmob_match_id):
    try:
        fotmob_match_url = f"https://www.fotmob.com/api/matchDetails?matchId={fotmob_match_id}"
        fotmob_match_response = requests.get(fotmob_match_url, headers=headers_matchDetails(fotmob_match_id))
        fotmob_match_response.raise_for_status()  # HTTP hatalarını kontrol et
        fotmobData = fotmob_match_response.json()
        return fotmobData
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def getFotmobTeamData(fotmob_team_id):
    fotmob_match_url = f"https://www.fotmob.com/api/teams?id={fotmob_team_id}"
    fotmob_match_response = requests.get(fotmob_match_url, headers=headers_team(fotmob_team_id))
    fotmobData = fotmob_match_response.json()
    return fotmobData

def extract_json_from_html(response_text):
    if not response_text:
        return None
        
    try:
        # JSON formatını yakalamak için regex kalıbı
        regex_pattern = r'(?<=require\.config\.params\[\"args\"\].=.)[\s\S]*?;'
        match = re.search(regex_pattern, response_text)
        
        if not match:
            return None

        data_txt = match.group(0)
        
        # JSON parser için tırnak işaretlerini ekle
        replacements = {
            'matchId': '"matchId"',
            'matchCentreData': '"matchCentreData"',
            'matchCentreEventTypeJson': '"matchCentreEventTypeJson"',
            'formationIdNameMappings': '"formationIdNameMappings"',
            '};': '}'
        }
        
        for old, new in replacements.items():
            data_txt = data_txt.replace(old, new)
            
        return data_txt
        
    except Exception as e:
        print(f"Error extracting JSON: {e}")
        return None

def extract_data_from_dict(data):
    # load data from json
    event_types = data["matchCentreEventTypeJson"]
    formation_mappings = data["formationIdNameMappings"]
    events_dict = data["matchCentreData"]["events"]
    teams_dict = {data["matchCentreData"]['home']['teamId']: data["matchCentreData"]['home']['name'],
                  data["matchCentreData"]['away']['teamId']: data["matchCentreData"]['away']['name']}
    players_dict = data["matchCentreData"]["playerIdNameDictionary"]
    # create players dataframe
    players_home_df = pd.DataFrame(data["matchCentreData"]['home']['players'])
    players_home_df["teamId"] = data["matchCentreData"]['home']['teamId']
    players_away_df = pd.DataFrame(data["matchCentreData"]['away']['players'])
    players_away_df["teamId"] = data["matchCentreData"]['away']['teamId']
    players_df = pd.concat([players_home_df, players_away_df])
    players_ids = data["matchCentreData"]["playerIdNameDictionary"]
    return event_types, events_dict, players_df, teams_dict, players_ids

def df_manipulation(df):
    df['type'] = df['type'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['outcomeType'] = df['outcomeType'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)
    df['period'] = df['period'].apply(lambda x: x['displayName'] if isinstance(x, dict) else None)

    df['x'] = df['x']*1.05
    df['y'] = df['y']*0.68
    df['endX'] = df['endX']*1.05
    df['endY'] = df['endY']*0.68
    df['goalMouthY'] = df['goalMouthY']*0.68

    pd.set_option('future.no_silent_downcasting', True)

    # temprary use of typeId of period column
    df['period'] = df['period'].replace({'FirstHalf': 1, 'SecondHalf': 2, 'FirstPeriodOfExtraTime': 3, 'SecondPeriodOfExtraTime': 4, 
                                        'PenaltyShootout': 5, 'PostGame': 14, 'PreMatch': 16})

    # new column for cumulative minutes, This part is taken from the "jakeyk11.github.io" github repository and modified for my use
    def cumulative_match_mins(events_df):
        events_out = pd.DataFrame()
        # Add cumulative time to events data, resetting for each unique match
        match_events = events_df.copy()
        match_events['cumulative_mins'] = match_events['minute'] + (1/60) * match_events['second']
        # Add time increment to cumulative minutes based on period of game.
        for period in np.arange(1, match_events['period'].max() + 1, 1):
            if period > 1:
                t_delta = match_events[match_events['period'] == period - 1]['cumulative_mins'].max() - \
                                    match_events[match_events['period'] == period]['cumulative_mins'].min()
            elif period == 1 or period == 5:
                t_delta = 0
            else:
                t_delta = 0
            match_events.loc[match_events['period'] == period, 'cumulative_mins'] += t_delta
        # Rebuild events dataframe
        events_out = pd.concat([events_out, match_events])
        return events_out

    df = cumulative_match_mins(df)

    # Extracting the carry data and merge it with the main df, This part is also taken from the "jakeyk11.github.io" github repository and modified for my use
    def insert_ball_carries(events_df, min_carry_length=3, max_carry_length=60, min_carry_duration=1, max_carry_duration=10):
        events_out = pd.DataFrame()
        # Carry conditions (convert from metres to opta)
        min_carry_length = 7.0
        max_carry_length = 60.0
        min_carry_duration = 1.0
        max_carry_duration = 10.0
        # match_events = events_df[events_df['match_id'] == match_id].reset_index()
        match_events = events_df.reset_index()
        match_carries = pd.DataFrame()
        
        for idx, match_event in match_events.iterrows():

            if idx < len(match_events) - 1:
                prev_evt_team = match_event['teamId']
                next_evt_idx = idx + 1
                init_next_evt = match_events.loc[next_evt_idx]
                take_ons = 0
                incorrect_next_evt = True

                while incorrect_next_evt:

                    next_evt = match_events.loc[next_evt_idx]

                    if next_evt['type'] == 'TakeOn' and next_evt['outcomeType'] == 'Successful':
                        take_ons += 1
                        incorrect_next_evt = True

                    elif ((next_evt['type'] == 'TakeOn' and next_evt['outcomeType'] == 'Unsuccessful')
                        or (next_evt['teamId'] != prev_evt_team and next_evt['type'] == 'Challenge' and next_evt['outcomeType'] == 'Unsuccessful')
                        or (next_evt['type'] == 'Foul')):
                        incorrect_next_evt = True

                    else:
                        incorrect_next_evt = False

                    next_evt_idx += 1

                # Apply some conditioning to determine whether carry criteria is satisfied
                same_team = prev_evt_team == next_evt['teamId']
                not_ball_touch = match_event['type'] != 'BallTouch'
                dx = 105*(match_event['endX'] - next_evt['x'])/100
                dy = 68*(match_event['endY'] - next_evt['y'])/100
                far_enough = dx ** 2 + dy ** 2 >= min_carry_length ** 2
                not_too_far = dx ** 2 + dy ** 2 <= max_carry_length ** 2
                dt = 60 * (next_evt['cumulative_mins'] - match_event['cumulative_mins'])
                min_time = dt >= min_carry_duration
                same_phase = dt < max_carry_duration
                same_period = match_event['period'] == next_evt['period']

                valid_carry = same_team & not_ball_touch & far_enough & not_too_far & min_time & same_phase &same_period

                if valid_carry:
                    carry = pd.DataFrame()
                    prev = match_event
                    nex = next_evt

                    carry.loc[0, 'eventId'] = prev['eventId'] + 0.5
                    carry['minute'] = np.floor(((init_next_evt['minute'] * 60 + init_next_evt['second']) + (
                            prev['minute'] * 60 + prev['second'])) / (2 * 60))
                    carry['second'] = (((init_next_evt['minute'] * 60 + init_next_evt['second']) +
                                        (prev['minute'] * 60 + prev['second'])) / 2) - (carry['minute'] * 60)
                    carry['teamId'] = nex['teamId']
                    carry['x'] = prev['endX']
                    carry['y'] = prev['endY']
                    carry['expandedMinute'] = np.floor(((init_next_evt['expandedMinute'] * 60 + init_next_evt['second']) +
                                                        (prev['expandedMinute'] * 60 + prev['second'])) / (2 * 60))
                    carry['period'] = nex['period']
                    carry['type'] = carry.apply(lambda x: {'value': 99, 'displayName': 'Carry'}, axis=1)
                    carry['outcomeType'] = 'Successful'
                    carry['qualifiers'] = carry.apply(lambda x: {'type': {'value': 999, 'displayName': 'takeOns'}, 'value': str(take_ons)}, axis=1)
                    carry['satisfiedEventsTypes'] = carry.apply(lambda x: [], axis=1)
                    carry['isTouch'] = True
                    carry['playerId'] = nex['playerId']
                    carry['endX'] = nex['x']
                    carry['endY'] = nex['y']
                    carry['blockedX'] = np.nan
                    carry['blockedY'] = np.nan
                    carry['goalMouthZ'] = np.nan
                    carry['goalMouthY'] = np.nan
                    carry['isShot'] = np.nan
                    carry['relatedEventId'] = nex['eventId']
                    carry['relatedPlayerId'] = np.nan
                    carry['isGoal'] = np.nan
                    carry['cardType'] = np.nan
                    carry['isOwnGoal'] = np.nan
                    carry['type'] = 'Carry'
                    carry['cumulative_mins'] = (prev['cumulative_mins'] + init_next_evt['cumulative_mins']) / 2

                    match_carries = pd.concat([match_carries, carry], ignore_index=True, sort=False)

        match_events_and_carries = pd.concat([match_carries, match_events], ignore_index=True, sort=False)
        match_events_and_carries = match_events_and_carries.sort_values(['period', 'cumulative_mins']).reset_index(drop=True)

        # Rebuild events dataframe
        events_out = pd.concat([events_out, match_events_and_carries])

        return events_out

    df = insert_ball_carries(df, min_carry_length=3, max_carry_length=60, min_carry_duration=1, max_carry_duration=10)

    df = df.reset_index(drop=True)
    df['index'] = range(1, len(df) + 1)
    df = df[['index'] + [col for col in df.columns if col != 'index']]

    df['prog_pass'] = np.where((df['type'] == 'Pass'), 
                            np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2) - np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2), 0)
    df['prog_carry'] = np.where((df['type'] == 'Carry'), 
                                np.sqrt((105 - df['x'])**2 + (34 - df['y'])**2) - np.sqrt((105 - df['endX'])**2 + (34 - df['endY'])**2), 0)
    df['pass_or_carry_angle'] = np.degrees(np.arctan2(df['endY'] - df['y'], df['endX'] - df['x']))
    return df

def list_players_and_get_selection_from_df(team_players, teams_dict, selected_player_option, selected_team_id):
    if selected_player_option:
        try:
            # Seçilen oyuncunun bilgilerini parse et
            player_id = int(re.search(r'ID: (\d+)', selected_player_option).group(1))
            player_data = team_players[team_players['playerId'] == player_id].iloc[0]
            
            return (
                player_data['name'],
                player_data['playerId'],
                selected_team_id,
                teams_dict[selected_team_id],
                player_data['shirtNo']
            )
        except (AttributeError, IndexError) as e:
            print(f"Error parsing player data: {e}")
            return None, None, None, None, None
    
    return None, None, None, None, None

pitch_color = '#d6c39f'
line_color = '#0e1117'
second_line_color = '#38435c'
green = '#1e7818'
orange = '#ff5d44'
blue = '#3572A5'
red = '#ad1e11'
yellow = '#c2a51d'
dark_yellow = '#8a7512'
gray = '#808080'
dark_gray = '#626262'
purple = '#3a1878'
transparent_color = '#FFFFFF00'
white_blue = '#c7ebf0'
white_green = '#c7f0dd'
heatmap_orange = '#f57c00'

def match_details(ax, fotmob_player_id, team_name, player_name, selected_player_number, minutes, teamColor1, teamColor2, player_fontsize):
    player_logo_url = f"https://images.fotmob.com/image_resources/playerimages/{fotmob_player_id}.png"
    player_logo = Image.open(BytesIO(requests.get(player_logo_url).content)).convert("RGBA")

    imagebox = OffsetImage(player_logo, zoom=0.5)

    x_center = (ax.get_xlim()[0] + ax.get_xlim()[1]) / 2
    y_center = (ax.get_ylim()[0] + ax.get_ylim()[1]) / 1.35

    ab = AnnotationBbox(imagebox, (x_center, y_center), frameon=False)
    ax.add_artist(ab)

    card_width = 0.6
    card_height = 0.8
    card_x = x_center - card_width / 2
    card_y = y_center - card_height / 1.15

    card = FancyBboxPatch(
        (card_x, card_y), card_width, card_height,
        boxstyle="round,pad=0.02,rounding_size=0.08",  
        edgecolor="white", facecolor=teamColor1, linewidth=4, alpha=0.1, zorder=1
    )
    ax.add_patch(card)

    shadow = FancyBboxPatch(
        (card_x + 0.02, card_y - 0.02), card_width, card_height,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        edgecolor="white", facecolor="white", linewidth=0, alpha=0.05, zorder=0
    )
    ax.add_patch(shadow)

    ax.set_facecolor(pitch_color)
    ax.axis('off')

    ellipse = Ellipse((x_center, y_center - 0.407), width=0.12, height=0.14,
                      facecolor=teamColor1, edgecolor='white', fill=True, linewidth=3, zorder=3)
    ax.add_patch(ellipse)

    ax.text(x_center, y_center - 0.3, player_name, fontsize=player_fontsize, ha='center',
            color=line_color, fontproperties=bold_prop, zorder=3)
    ax.text(x_center, y_center - 0.417, str(selected_player_number), fontsize=25,
            ha='center', va='center', color=teamColor2, fontproperties=bold_prop, zorder=3)
    ax.text(x_center, y_center - 0.57, team_name, fontsize=18, ha='center',
            color=teamColor1, fontweight='bold', fontproperties=bold_prop, zorder=3)
    ax.text(x_center, y_center - 0.66, f"{minutes} dakika", fontsize=15,
            ha='center', color=second_line_color, fontproperties=prop, zorder=3)

    ab.zorder = 3
    
    # **Eksen limitlerini sabitle**
    ax.set_xlim(ax.get_xlim())  # X limitlerini sabitle
    ax.set_ylim(ax.get_ylim())  # Y limitlerini sabitle
    
    # Çizgiyi ekleyelim
    line_width = card_width * 0.75  
    line_x1 = x_center - line_width / 2
    line_x2 = x_center + line_width / 2
    line_y = y_center - 0.1775 

    ax.plot([line_x1, line_x2], [line_y, line_y], color="black", linewidth=2, zorder=2, alpha=0.5)

    # **Eksen limitlerini sabitle**
    ax.set_xlim(ax.get_xlim())  # X limitlerini sabitle
    ax.set_ylim(ax.get_ylim())  # Y limitlerini sabitle

    return

def passes_and_key_passes(ax, selected_player_id, df):
    pitch = Pitch(pitch_type='uefa', pitch_color=pitch_color, line_color=line_color, goal_type='box', corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5,105.5)
    ax.set_ylim(-0.5,68.5)
    plt.axis('off')
    
    playerdf = df[df['playerId'] == selected_player_id].copy()  # .copy() kullanarak uyarıyı önleriz
    
    if playerdf.empty:
        return
    
    playerdf.loc[:, 'qualifiers'] = playerdf['qualifiers'].fillna('')
    playerdf.loc[:, 'qualifiers'] = playerdf['qualifiers'].astype(str)
    pass_events = playerdf[playerdf['type']=='Pass'].copy()
    pass_events = pass_events[~pass_events['qualifiers'].str.contains('ThrowIn|OppositeRelatedEvent')]
    # DataFrame'e dönüştürelim
    df_passes = pd.DataFrame(pass_events)
    df_passes['distance'] = np.sqrt((df_passes['endX'] - df_passes['x'])**2 + (df_passes['endY'] - df_passes['y'])**2).round(2)
    shortest_pass = df_passes.loc[df_passes['distance'].idxmin()]
    acc_pass = df_passes[df_passes['outcomeType']=='Successful']
    inac_pass = df_passes[df_passes['outcomeType']=='Unsuccessful']
    long_pass = df_passes[df_passes['qualifiers'].str.contains('Longball')]
    long_pass_acc = long_pass[long_pass['outcomeType']=='Successful']
    # Savunma sahasının %40'ı: 105 metre uzunluğun %40'ı (42 metre)
    defending_zone_limit = 105 * 0.4  # 42 metre

    # Yarı saha sınırı
    halfway_line = 105 / 2  # 52.5 metre

    # Ceza sahasının sınırları
    penalty_area_x = 105 - 16.5
    penalty_area_y_min = (68 / 2) - 16.5
    penalty_area_y_max = (68 / 2) + 16.5

    # Progressive pas kriterleri
    pro_pass = acc_pass[
        # Kendi yarı sahasında: Pas kendi yarı sahasında başlayıp bitiyorsa en az 30 metre ilerlemesi gerekiyor
        (((acc_pass['x'] < halfway_line) & (acc_pass['endX'] < halfway_line)) & 
        ((acc_pass['endX'] - acc_pass['x']) >= 30)) |
        
        # Yarı sahalar arasında: Pas kendi yarı sahasında başlayıp rakip yarı sahasında bitiyorsa en az 15 metre ilerlemesi gerekiyor
        (((acc_pass['x'] < halfway_line) & (acc_pass['endX'] >= halfway_line)) & 
        ((acc_pass['endX'] - acc_pass['x']) >= 15)) |
        
        # Rakip yarı sahasında: Pas rakip yarı sahasında başlayıp bitiyorsa en az 10 metre ilerlemesi gerekiyor
        (((acc_pass['x'] >= halfway_line) & (acc_pass['endX'] >= halfway_line)) & 
        ((acc_pass['endX'] - acc_pass['x']) >= 10)) |
        
        # Ceza sahasına yapılan paslar (otomatik olarak progressive kabul edilir)
        ((acc_pass['endX'] >= penalty_area_x) & (acc_pass['endY'].between(penalty_area_y_min, penalty_area_y_max)))
    ]

    # Savunma sahasının %40'ından gelen pasları hariç tut (ilk 42 metre)
    pro_pass = pro_pass[acc_pass['x'] >= defending_zone_limit]

    # Korner ve serbest vuruş paslarını hariç tut
    pro_pass = pro_pass[~pro_pass['qualifiers'].str.contains('CornerTaken|Freekick')]
    
    if len(df_passes) != 0:
        accurate_pass_perc = round((len(acc_pass)/len(df_passes))*100, 2)
    else:
        accurate_pass_perc = 0
        
    # KeyPass olanları filtrele
    df_key_passes = df_passes[df_passes['qualifiers'].str.contains('KeyPass')]
    df_big_chances_created = df_passes[df_passes['qualifiers'].str.contains('BigChanceCreated')]
    df_assists = df_passes[df_passes['qualifiers'].str.contains('IntentionalGoalAssist')]

    player_passes_df = df_passes.copy()
    player_passes_df['pass_or_carry_angle'] = player_passes_df['pass_or_carry_angle'].abs()
    player_passes_df = player_passes_df[(player_passes_df['pass_or_carry_angle']>=0) & (player_passes_df['pass_or_carry_angle']<=90)]
    med_ang = player_passes_df['pass_or_carry_angle'].median()
    verticality = round((1 - med_ang/90)*100, 2)

    pass_1 = pitch.lines(df_passes["x"], df_passes["y"], df_passes["endX"], df_passes["endY"],
                            ax=ax, lw=1, transparent=True, comet=True,
                            label='Key Passes', color=dark_gray, zorder=0)
    #pass_2 = ax.scatter(df_passes["endX"], df_passes["endY"], marker='o', s=50, c='blue')
    long_pass_1 = pitch.lines(long_pass["x"], long_pass["y"], long_pass["endX"], long_pass["endY"],
                            ax=ax, lw=1.5, transparent=True, comet=True,
                            label='Long Passes', color=green, zorder=1)
    progressive_pass_1 = pitch.lines(pro_pass["x"], pro_pass["y"], pro_pass["endX"], pro_pass["endY"],
                            ax=ax, lw=2.5, transparent=True, comet=True,
                            label='Progressive Passes',color=dark_yellow, zorder=2)
    progressive_pass_2 = pitch.scatter(pro_pass["endX"], pro_pass["endY"], marker='o', s=20, c=pitch_color, edgecolor=dark_yellow,linewidth=1,zorder=2, ax=ax)
    key_pass_1 = pitch.lines(df_key_passes["x"], df_key_passes["y"], df_key_passes["endX"], df_key_passes["endY"],
                            ax=ax, lw=2.5, transparent=True, comet=True,
                            label='Key Passes',color=blue, zorder=3)
    key_pass_2 = pitch.scatter(df_key_passes["endX"], df_key_passes["endY"], marker='o', s=20, c=pitch_color, edgecolor=blue,linewidth=1,zorder=3, ax=ax)
    big_chances_created_1 = pitch.lines(df_big_chances_created["x"], df_big_chances_created["y"], df_big_chances_created["endX"], df_big_chances_created["endY"],
                            ax=ax, lw=2.5, transparent=True, comet=True,
                            label='Big Chances Created Passes',color=orange, zorder=4)
    big_chances_created_2 = pitch.scatter(df_big_chances_created["endX"], df_big_chances_created["endY"], marker='o', s=20, c=pitch_color, edgecolor=orange,linewidth=1,zorder=4, ax=ax)
    assists_1 = pitch.lines(df_assists["x"], df_assists["y"], df_assists["endX"], df_assists["endY"],
                            ax=ax, lw=2.5, transparent=True, comet=True,
                            label='Assists',color=purple, zorder=5)
    assists_2 = pitch.scatter(df_assists["endX"], df_assists["endY"], marker='o', s=20, c=pitch_color, edgecolor=purple,linewidth=1,zorder=5, ax=ax)
    
    ax.set_title(f"Pas Haritası", color=line_color, fontproperties=bold_prop, fontweight='bold', y=1.05)
    
    verticality_text = f"%{verticality:.2f}"
    verticality_color = '#1E88E5'
    
    ax_text(
        0, -3,
        f'''<İsabetli Pas: {len(acc_pass)}/{len(df_passes)} ({accurate_pass_perc}%)> | <İsabetli Uzun Pas: {len(long_pass_acc)}/{len(long_pass)}>\n
        <Dikey Pas Oranı: {verticality_text}> | <Progresif Pas: {len(pro_pass)}>\n
        <Kilit Pas: {len(df_key_passes)}> | <Yaratılan Büyük Şans: {len(df_big_chances_created)}>\n
        <Asist: {len(df_assists)}>''',
    
        color=line_color,
    
        highlight_textprops=[
            {'color': dark_gray},        # Accurate Passes
            {'color': green},            # Acc. Long Passes
            {'color': verticality_color},# Dikey Pas Oranı (yeni yeri)
            {'color': dark_yellow},      # Progresif Pas
            {'color': blue},             # Key Passes
            {'color': orange},           # Big Chances Created
            {'color': purple}            # Assists
        ],
    
        fontsize=12, ha='left', va='top', ax=ax, fontproperties=prop
    )

    return

def touches_and_heatmap(ax, selected_player_id, df):
    pitch = Pitch(pitch_type='uefa', pitch_color=pitch_color, line_color=line_color, goal_type='box', corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5,105.5)
    ax.set_ylim(-0.5,68.5)
    plt.axis('off')
    
    playerdf = df[df['playerId'] == selected_player_id]
    df_player = playerdf[~playerdf['type'].str.contains('SubstitutionOff|SubstitutionOn|Card|Carry')]
    new_data = pd.DataFrame({'x': [-5, -5, 110, 110], 'y': [-5, 73, 73, -5]})
    df_player = pd.concat([df_player, new_data], ignore_index=True)
    flamingo_cmap = LinearSegmentedColormap.from_list("Flamingo - 100 colors", [to_rgba(heatmap_orange, alpha=0), to_rgba(heatmap_orange, alpha=0.25), to_rgba(heatmap_orange, alpha=0.5), to_rgba(heatmap_orange, alpha=0.75), to_rgba(heatmap_orange, alpha=1)], N=500)
    
    heatmap, xedges, yedges = np.histogram2d(df_player['x'], df_player['y'], bins=(12,12))
    extent = [xedges[0], xedges[-1], yedges[-1], yedges[0]]
    #extent = [0,105,68,0]
    ax.imshow(heatmap.T, extent=extent, cmap=flamingo_cmap, interpolation="bilinear", alpha=0.7)
    
    df_player.loc[:, 'qualifiers'] = df_player['qualifiers'].fillna('')
    df_player.loc[:, 'qualifiers'] = df_player['qualifiers'].astype(str)
    df_player_touches = df_player[~df_player['qualifiers'].str.contains('ThrowIn|CornerTaken|FreekickTaken')]
    touches = df_player_touches[df_player_touches['isTouch'] == True]
    final_third = touches[touches['x']>=70]
    ax.scatter(touches['x'], touches['y'], marker='o',s=25,c=blue,edgecolor='white',linewidth=0.35,alpha=0.9,zorder=5)
    
    ax.set_title(f"Isı Haritası ve Topla Buluşma", color=line_color, fontproperties=bold_prop, fontweight='bold', y=1.05)
    
    ax_text(0, -3, f'''<Akan Oyunda Topla Buluşma: {len(touches)}>\n<Üçüncü Bölgede Topla Buluşma: {len(final_third)}>
        ''', color=line_color, highlight_textprops=[{'color':line_color}, {'color':line_color}], fontsize=12, ha='left', va='top', ax=ax, fontproperties=prop)

    return

def defensive_actions(ax, selected_player_id, df):
    pitch = Pitch(pitch_type='uefa', pitch_color=pitch_color, line_color=line_color, goal_type='box', corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5,105.5)
    ax.set_ylim(-0.5,68.5)
    plt.axis('off')
    
    playerdf = df[df['playerId'] == selected_player_id].copy()
    ball_wins = playerdf[(playerdf['type']=='Interception') | (playerdf['type']=='BallRecovery')]
    f_third = ball_wins[ball_wins['x']>=70]
    m_third = ball_wins[(ball_wins['x']>35) & (ball_wins['x']<70)]
    d_third = ball_wins[ball_wins['x']<=35]
    
    tackle = playerdf[(playerdf['type']=='Tackle')]
    interception = playerdf[(playerdf['type']=='Interception')]
    ballRecovery = playerdf[playerdf['type']=='BallRecovery']
    clearance = playerdf[(playerdf['type']=='Clearance') & (playerdf['endX']>0)]
    foul = playerdf[(playerdf['type']=='Foul') & (playerdf['outcomeType']=='Unsuccessful')]
    aerial = playerdf[(playerdf['type']=='Aerial')]
    
    pitch.scatter(tackle['x'], tackle['y'], s=150, c=orange, lw=2.5, edgecolor=blue, marker='+', hatch='/////', ax=ax)
    pitch.scatter(interception['x'], interception['y'], s=100, c='None', lw=2.5, edgecolor=blue, marker='s', hatch='/////', ax=ax)
    pitch.scatter(ballRecovery['x'], ballRecovery['y'], s=150, c='None', lw=2.5, edgecolor=green, marker='o', hatch='/////', ax=ax)
    pitch.scatter(clearance['x'], clearance['y'], s=100, c='None', lw=2.5, edgecolor=gray, marker='d', hatch='/////', ax=ax)
    pitch.scatter(foul['x'], foul['y'], s=100, c=red, lw=2.5, edgecolor=red, marker='x', hatch='/////', ax=ax)
    pitch.scatter(aerial['x'], aerial['y'], s=100, c='None', lw=2.5, edgecolor=purple, marker='^', hatch='/////', ax=ax)
    
    ax.set_title(f"Defansif Aksiyonlar", color=line_color, fontproperties=bold_prop, fontweight='bold', y=1.05)
    
    ax_text(0, -3, f'''<Top Çalma: {len(tackle)}> | <Pas Arası: {len(interception)}> | <Top Kazanma: {len(ballRecovery)}>\n<Top Uzaklaştırma: {len(clearance)}> | <Hava Topu: {len(aerial)}> | <Faul: {len(foul)}>
        ''', color=line_color, highlight_textprops=[{'color':orange}, {'color':blue}, {'color':green},
                                                    {'color':gray}, {'color':purple}, {'color':red}], fontsize=12, ha='left', va='top', ax=ax, fontproperties=prop)
    
    return

def dribbling_carrying(ax, selected_player_id, df):
    pitch = Pitch(pitch_type='uefa', pitch_color=pitch_color, line_color=line_color, goal_type='box', corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5,105.5)
    ax.set_ylim(-0.5,68.5)
    plt.axis('off')
    
    playerdf = df[df['playerId'] == selected_player_id].copy()
    df_carry = playerdf[(playerdf['type']=='Carry')]
    pro_carry = df_carry[(df_carry['prog_carry']>=9.11) & (df_carry['x']>=35)]
    led_shot1 = playerdf[(playerdf['type']=='Carry') & (playerdf['qualifiers'].shift(-1).str.contains('KeyPass'))]
    led_shot2 = playerdf[(playerdf['type']=='Carry') & (playerdf['type'].shift(-1).str.contains('Shot'))]
    led_shot = pd.concat([led_shot1, led_shot2])
    led_goal1 = playerdf[(playerdf['type']=='Carry') & (playerdf['qualifiers'].shift(-1).str.contains('IntentionalGoalAssist'))]
    led_goal2 = playerdf[(playerdf['type']=='Carry') & (playerdf['type'].shift(-1)=='Goal')]
    led_goal = pd.concat([led_goal1, led_goal2])
    df_dribbling_succ = playerdf[(playerdf['type']=='TakeOn') & (playerdf['outcomeType']=='Successful')]
    df_dribbling_unsucc = playerdf[(playerdf['type']=='TakeOn') & (playerdf['outcomeType']=='Unsuccessful')]
    
     # carry (top sürme) için yeşil oklar
    for index, row in df_carry.iterrows():
        arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), color=dark_gray, alpha=0.6, arrowstyle='->', linestyle='--', 
                                   linewidth=1, mutation_scale=15, zorder=2)
        ax.add_patch(arrow)
    
    for index, row in pro_carry.iterrows():
        arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), color=blue, alpha=0.8, arrowstyle='->', linestyle='--', 
                                   linewidth=1.5, mutation_scale=15, zorder=2)
        ax.add_patch(arrow)
        
    for index, row in led_shot.iterrows():
        arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), color=dark_yellow, alpha=1, arrowstyle='->', linestyle='--', linewidth=2, 
                                   mutation_scale=20, zorder=4)
        ax.add_patch(arrow)
    for index, row in led_goal.iterrows():
        arrow = patches.FancyArrowPatch((row['x'], row['y']), (row['endX'], row['endY']), color=orange, alpha=1, arrowstyle='->', linestyle='--', linewidth=2, 
                                   mutation_scale=20, zorder=4)
        ax.add_patch(arrow)
        
    pitch.scatter(df_dribbling_succ['x'], df_dribbling_succ['y'], s=200, c=green, lw=1.5, edgecolor=white_green, marker='o', hatch='/////', ax=ax)
    pitch.scatter(df_dribbling_unsucc['x'], df_dribbling_unsucc['y'], s=150, c=red, lw=2.5, edgecolor='red', marker='x', ax=ax)
    
    ax.set_title(f"Top Sürme ve Çalım", color=line_color, fontproperties=bold_prop, fontweight='bold', y=1.05)
    
    ax_text(0, -3, f'''<Başarılı Çalım: {len(df_dribbling_succ)}> | <Başarısız Çalım: {len(df_dribbling_unsucc)}>\n<Top Sürme: {len(df_carry)}> | <Atak Geliştiren Top Sürme: {len(pro_carry)}>\n<Şut ile Sonuçlanan TS: {len(led_shot)}> | <Gol ile Sonuçlanan TS: {len(led_goal)}>
        ''', color=line_color, highlight_textprops=[{'color':green}, {'color':red}, {'color':dark_gray}, {'color':blue}, {'color':dark_yellow}, {'color':orange}], fontsize=12, ha='left', va='top', ax=ax, fontproperties=prop)
    
    return

def shotmap(ax, selected_player_id, df, shots_data, fotmob_player_id):
    pitch = Pitch(pitch_type='uefa', pitch_color=pitch_color, line_color=line_color, goal_type='box', corner_arcs=True)
    pitch.draw(ax=ax)
    ax.set_xlim(-0.5,105.5)
    ax.set_ylim(-0.5,68.5)
    plt.axis('off')
    
    goal_color = green
    saved_color = blue
    blocked_color = '#40427a'
    miss_color = 'red'
    post_color = gray  # Direkten dönen şutlar koyu gri
        
    player_shots = [shot for shot in shots_data if shot['playerId'] == int(fotmob_player_id)]
    
    if player_shots:
        # Seçilen oyuncunun şut haritasını çiz
        for shot in player_shots:
            if shot['eventType'] == 'Goal':  # Gol olan şut
                shot_color = goal_color
                pitch.lines(shot['x'], shot['y'], 105, shot['goalCrossedY'], ax=ax, color=to_rgba(shot_color, alpha=0.5), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c='None', s=round(shot['expectedGoals'], 2)*2000, edgecolors=goal_color, marker='football', alpha=0.8)
            
            elif shot['eventType'] == 'AttemptSaved' and shot['isBlocked'] == True and shot['expectedGoalsOnTarget'] == 0:  # Bloklanan şut
                shot_color = blocked_color
                pitch.lines(shot['x'], shot['y'], shot['blockedX'], shot['blockedY'], ax=ax, color=to_rgba(shot_color, alpha=0.5), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c=shot_color, s=round(shot['expectedGoals'], 2)*2000, edgecolors='white', marker='D', alpha=0.8, lw=0.7, hatch='|||||')
            
            elif shot['eventType'] == 'AttemptSaved' and shot['isBlocked'] == False and shot['expectedGoalsOnTarget'] > 0:  # İsabetli Şut | Kurtarılan şut
                shot_color = saved_color
                pitch.lines(shot['x'], shot['y'], shot['blockedX'], shot['blockedY'], ax=ax, color=to_rgba(shot_color, alpha=0.5), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c=shot_color, s=round(shot['expectedGoals'], 2)*2000, edgecolors='white', marker='o', alpha=0.8, lw=1, hatch='/////')
            
            elif shot['eventType'] == 'Miss':  # İsabetsiz şut
                shot_color = miss_color
                pitch.lines(shot['x'], shot['y'], 105, shot['goalCrossedY'], ax=ax, color=to_rgba(shot_color, alpha=0.25), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c=shot_color, s=round(shot['expectedGoals'], 2)*2000, edgecolors='black', marker='x', alpha=0.8, lw=1)
            
            elif shot['eventType'] == 'Post':  # Direkten dönen şut
                shot_color = post_color
                pitch.lines(shot['x'], shot['y'], 105, shot['goalCrossedY'], ax=ax, color=to_rgba(shot_color, alpha=0.25), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c=shot_color, s=round(shot['expectedGoals'], 2)*2000, edgecolors='black', marker='+', alpha=0.8, lw=1, hatch='|')
            
            else:  # Bloklanan diğer şutlar
                shot_color = blocked_color
                pitch.lines(shot['x'], shot['y'], shot['blockedX'], shot['blockedY'], ax=ax, color=to_rgba(shot_color, alpha=0.5), lw=1)
                pitch.scatter(shot['x'], shot['y'], ax=ax, c=shot_color, s=round(shot['expectedGoals'], 2)*2000, edgecolors='black', marker='o', alpha=0.8, lw=1, hatch='/')
                
        player_shots_df = pd.DataFrame(player_shots)
                
        goal = player_shots_df[player_shots_df['eventType'] == 'Goal']
        openPlay = player_shots_df[player_shots_df['situation']=='RegularPlay']
        block = player_shots_df[(player_shots_df['eventType'] == 'AttemptSaved') & 
                            (player_shots_df['isBlocked'] == True) & 
                            (player_shots_df['expectedGoalsOnTarget'] == 0)]

        saved = player_shots_df[(player_shots_df['eventType'] == 'AttemptSaved') & 
                                (player_shots_df['isBlocked'] == False) & 
                                (player_shots_df['expectedGoalsOnTarget'] > 0)]
        miss = player_shots_df[player_shots_df['eventType'] == 'Miss']
        post = player_shots_df[player_shots_df['eventType'] == 'Post']
        xG = player_shots_df['expectedGoals'].sum().round(2)
        xGOT = player_shots_df['expectedGoalsOnTarget'].sum().round(2)
        
        playerdf = df[df['playerId'] == selected_player_id].copy()
        
        playerdf.loc[:, 'qualifiers'] = playerdf['qualifiers'].fillna('')
        playerdf.loc[:, 'qualifiers'] = playerdf['qualifiers'].astype(str)
        
        goal_bc = playerdf[(playerdf['type']=='Goal') & (playerdf['qualifiers'].str.contains('BigChance'))]
        miss_bc = playerdf[(playerdf['type']=='MissedShots') & (playerdf['qualifiers'].str.contains('BigChance'))]
        save_bc = playerdf[(playerdf['type']=='SavedShot') & (playerdf['qualifiers'].str.contains('BigChance'))]
        post_bc = playerdf[(playerdf['type']=='ShotOnPost') & (playerdf['qualifiers'].str.contains('BigChance'))]
        
        spacing = 6  # Satırlar arası boşluk
        
        pitch.scatter(2,52.25-(0*spacing), s=150, marker='football', c='None', edgecolors=green, zorder=5, ax=ax)
        pitch.scatter(2,52.25-(1*spacing), s=130, marker='o', c=saved_color, edgecolors='white', hatch='/////', zorder=4, ax=ax) # İsabetli Şut | Kurtarılan Şut
        pitch.scatter(2,52.25-(2*spacing), s=100, marker='x', c=miss_color, edgecolors='black', zorder=3, ax=ax) # İsabetsiz Şut
        pitch.scatter(2,52.25-(3*spacing), s=130, marker='+', c=post_color, edgecolors='black', hatch='|', zorder=2, ax=ax) # Direkten Dönen Şut
        pitch.scatter(2,52.25-(4*spacing), s=100, marker='D', c=blocked_color, edgecolors='white', hatch='|||||', zorder=2, ax=ax) # Bloklanan Şut
        
        ax.text(7,64-(0*spacing), f'Toplam Şut: {len(player_shots_df)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(1*spacing), f'Akan Oyunda Şut: {len(openPlay)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(2*spacing), f'Gol: {len(goal)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(3*spacing), f'İsabetli Şut: {(len(saved))+(len(goal))}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(4*spacing), f'İsabetsiz Şut: {len(miss)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(5*spacing), f'Direkten Dönen Şut: {len(post)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(6*spacing), f'Engellenen Şut: {len(block)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(7*spacing), f'Net Gol Fırsatı: {len(goal_bc)+len(miss_bc)+len(save_bc)+len(post_bc)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(8*spacing), f'Kaçan Net Gol Fırsatı: {len(miss_bc)+len(save_bc)+len(post_bc)}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(9*spacing), f'xG: {xG}', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(10*spacing), f'xGOT: {xGOT}', fontsize=12, ha='left', va='center', fontproperties=prop)
        
    else:
        spacing = 6  # Satırlar arası boşluk
        
        pitch.scatter(2,52.25-(0*spacing), s=150, marker='football', c='None', edgecolors=green, zorder=5, ax=ax)
        pitch.scatter(2,52.25-(1*spacing), s=130, marker='o', c=saved_color, edgecolors='white', hatch='/////', zorder=4, ax=ax) # İsabetli Şut | Kurtarılan Şut
        pitch.scatter(2,52.25-(2*spacing), s=100, marker='x', c=miss_color, edgecolors='black', zorder=3, ax=ax) # İsabetsiz Şut
        pitch.scatter(2,52.25-(3*spacing), s=130, marker='+', c=post_color, edgecolors='black', hatch='|', zorder=2, ax=ax) # Direkten Dönen Şut
        pitch.scatter(2,52.25-(4*spacing), s=100, marker='D', c=blocked_color, edgecolors='white', hatch='|||||', zorder=2, ax=ax) # Bloklanan Şut
        
        ax.text(7,64-(0*spacing), f'Toplam Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(1*spacing), f'Akan Oyunda Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(2*spacing), f'Gol: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(3*spacing), f'İsabetli Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(4*spacing), f'İsabetsiz Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(5*spacing), f'Direkten Dönen Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(6*spacing), f'Engellenen Şut: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(7*spacing), f'Net Gol Fırsatı: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(8*spacing), f'Kaçan Net Gol Fırsatı: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(9*spacing), f'xG: 0', fontsize=12, ha='left', va='center', fontproperties=prop)
        ax.text(7,64-(10*spacing), f'xGOT: 0', fontsize=12, ha='left', va='center', fontproperties=prop)

    yhalf = [-0.5, -0.5, 68.5, 68.5]
    xhalf = [-0.5, 52.5, 52.5, -0.5]
    ax.fill(xhalf, yhalf, pitch_color, alpha=1)
    
    ax.set_title(f"Şut Haritası", color=line_color, fontproperties=bold_prop, fontweight='bold', y=1.05)
    
    return



