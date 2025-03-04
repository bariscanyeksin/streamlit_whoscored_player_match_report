import streamlit as st
import json
import pandas as pd
import cloudscraper
from mplsoccer import add_image
import matplotlib.pyplot as plt
import os
from matplotlib import font_manager as fm
from PIL import Image
from io import BytesIO
import requests
from datetime import datetime
from matplotlib.patches import FancyArrowPatch
from functions import *
import io
import time
from playwright.sync_api import sync_playwright

st.set_page_config(
    page_title="Match Analysis",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar'ı otomatik açık başlat
)

current_dir = os.path.dirname(os.path.abspath(__file__))

# Poppins fontunu yükleme
font_path = os.path.join(current_dir, 'fonts', 'Poppins-Regular.ttf')
prop = fm.FontProperties(fname=font_path)

bold_font_path = os.path.join(current_dir, 'fonts', 'Poppins-SemiBold.ttf')
bold_prop = fm.FontProperties(fname=bold_font_path)

def install_playwright():
    try:
        subprocess.run(["playwright", "install", "chromium"], check=True)
    except subprocess.CalledProcessError:
        print("Playwright yükleme başarısız oldu.")

install_playwright()

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

html, body, [class*="cache"], [class*="st-"]  {
    font-family: 'Poppins', sans-serif;
}
</style>
""", unsafe_allow_html=True
)

st.markdown(
"""
<style>
    /* Bilgisayarlar için */
    @media (min-width: 1024px) {
        .block-container {
            width: 900px;
            max-width: 900px;
            padding-top: 50px;
            padding-bottom: 0px;
        }
    }

    /* Tabletler için (genellikle 768px - 1024px arası ekran genişliği) */
    @media (min-width: 768px) and (max-width: 1023px) {
        .block-container.st-emotion-cache-13ln4jf.ea3mdgi5 {
            width: 700px;
            max-width: 700px;
        }
    }

    /* Telefonlar için (genellikle 768px ve altı ekran genişliği) */
    @media (max-width: 767px) {
        .block-container.st-emotion-cache-13ln4jf.ea3mdgi5 {
            width: 100%;
            max-width: 100%;
            padding-left: 10px;
            padding-right: 10px;
        }
    }
    .stDownloadButton {
        display: flex;
        justify-content: center;
        text-align: center;
    }
    .stDownloadButton button {
        background-color: rgba(51, 51, 51, 0.17);
        color: gray;  /* Text color */
        border: 0.5px solid gray;  /* Thin gray border */
        transition: background-color 0.5s ease;
    }
    .stDownloadButton button:hover {
        background-color: rgba(51, 51, 51, 0.65);
        border: 1px solid gray;  /* Thin gray border */
        color: gray;  /* Text color */
    }
    .stDownloadButton button:active {
        background-color: rgba(51, 51, 51, 0.17);
        color: gray;  /* Text color */
        border: 0.5px solid gray;  /* Thin gray border */
        transition: background-color 0.5s ease;
    }
</style>
""",
unsafe_allow_html=True
)

# Sidebar'da ID'leri al
with st.sidebar:
    st.title("Match Settings")
    st.info("Enter the match IDs from WhoScored and Fotmob to analyze the match.")
    whoscored_match_id = st.text_input("WhoScored Match ID", help="Enter the match ID from WhoScored URL")
    fotmob_match_id = st.text_input("Fotmob Match ID", help="Enter the match ID from Fotmob URL")

# Fotmob verilerini çekmek için fonksiyon
def fetch_fotmob_data(fotmob_match_id):
    try:
        fotmobData = getFotmobData(fotmob_match_id)
        return fotmobData
    except Exception as e:
        st.error(f"Error fetching Fotmob data: {e}")
        return None

def fetch_fotmob_team_data(fotmob_team_id):
    fotmobTeamData = getFotmobTeamData(fotmob_team_id)
    return fotmobTeamData

@st.cache_data(ttl=600)

def load_match_data(whoscored_match_id):
    url = f'https://www.whoscored.com/matches/{whoscored_match_id}/live'
    try:
        with sync_playwright() as p:
            # Tarayıcıyı başlat
            browser = p.chromium.launch(headless=True)  # Headless modda tarayıcıyı başlat
            
            # User-Agent'ı ayarlamak için yeni bir sayfa oluştur
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()

            # Tarayıcı boyutunu ayarla
            page.set_viewport_size({"width": 1920, "height": 1080})

            # Sayfa yüklenmeden önce 2 saniye bekle
            page.wait_for_timeout(2000)

            # Sayfayı aç
            page.goto(url, wait_until='domcontentloaded')  # Sayfa yüklendiğinde bekle

            # Sayfa içeriğini al
            page_content = page.content()
            browser.close()
            return page_content
    except Exception as e:
        st.error(f"Unexpected error: {e}")
        return None
    
if whoscored_match_id!="" and fotmob_match_id!="":
    # JSON verisini yükleme ve kontrol mekanizması
    response_text = load_match_data(whoscored_match_id)

    if response_text:  # Check if response_text is not None
        json_data_txt = extract_json_from_html(response_text)

        # Eğer JSON verisi None ise, tekrar deneme
        retries = 3
        while json_data_txt is None and retries > 0:
            st.warning("JSON verisi alınamadı. Yeniden deniyorum...")
            response_text = load_match_data(whoscored_match_id)
            if response_text:  # Check if response_text is valid
                st.write("Response text received on retry:")
                st.code(response_text)  # Log the response text for debugging
                json_data_txt = extract_json_from_html(response_text)
            retries -= 1

        if json_data_txt is None:
            st.error("Maksimum deneme sayısına ulaşıldı. JSON verisi alınamadı.")
        else:
            try:
                data = json.loads(json_data_txt)
                event_types, events_dict, players_df, teams_dict, players_ids = extract_data_from_dict(data)
                df = pd.DataFrame(events_dict)
                df = df_manipulation(df)
            except Exception as e:
                st.error(f"Error processing JSON data: {e}")
    else:
        st.error("Failed to fetch match data. Please check the match ID and try again.")

    # Kullanıcıdan alınan ID'lere göre verileri çek
    fotmobData = fetch_fotmob_data(fotmob_match_id)

    team_player_map = {}  # Takım ID'leri ve oyuncu numaraları için bir harita
            
    # Oyuncuları takımlara göre ayırıyoruz
    teams = players_df['teamId'].unique()
    global_index = 1  # Global numaralandırıcı

    for team_id in teams:
        team_name = teams_dict.get(team_id, "Bilinmeyen Takım")
        team_players = players_df[players_df['teamId'] == team_id]
        
        # Oyuncuları numaralandırarak listeliyoruz
        team_player_map[team_id] = []
        for idx, row in team_players.iterrows():
            team_player_map[team_id].append((row['playerId'], row['name'], row['shirtNo']))

    # Takım seçimi için container
    team_select_container = st.container()

    selected_team_id = team_select_container.selectbox(
        "Select Team",
        options=list(teams_dict.keys()),
        format_func=lambda x: teams_dict[x]
    )

    # Seçilen takımın oyuncularını filtrele
    team_players = players_df[players_df['teamId'] == selected_team_id]

    # Oyuncu seçimi için container
    player_select_container = st.container()

    # Oyuncu seçeneklerini oluştur
    player_options = [
        f"{row['name']} (ID: {row['playerId']}, Number: {row['shirtNo']})" 
        for _, row in team_players.iterrows()
    ]

    # Oyuncu seçimi
    selected_player_option = player_select_container.selectbox(
        "Select Player",
        options=player_options
    )

    if fotmobData:
        fotmobPlayerStats = fotmobData['content']['playerStats']
        player_options = [(player['name'], player_id) for player_id, player in fotmobPlayerStats.items()]

        # İlk oyuncuyu varsayılan olarak seç
        with st.sidebar:
            selected_fotmob_player_name, selected_fotmob_player_id = st.selectbox("Select Player", player_options, format_func=lambda x: x[0], index=0)
            # Fotmob verilerini tekrar çek
        fotmobData = fetch_fotmob_data(fotmob_match_id)
        
        if fotmobData:
            fotmobPlayerStats = fotmobData['content']['playerStats']
            fotmobPlayerDf =  fotmobPlayerStats[str(selected_fotmob_player_id)]
            player_name = fotmobPlayerDf['name']
            minutes = fotmobPlayerDf['stats'][0]['stats']['Minutes played']['stat']['value']
            shots_data = fotmobData['content']['shotmap']['shots']
            
            def get_team_id_by_player_id(lineup_data, player_id):
                for team_key in ["homeTeam", "awayTeam"]:
                    if team_key in lineup_data:
                        team = lineup_data[team_key]
                        all_players = team.get("starters", []) + team.get("substitutes", [])
                        for player in all_players:
                            if int(player['id']) == int(player_id):
                                return team['id']
                return None  # Oyuncu bulunamazsa None döndür
            
            lineup_data = fotmobData['content']['lineup']
            team_id = get_team_id_by_player_id(lineup_data, selected_fotmob_player_id)
            
            if team_id is not None:
                fotmobTeamData = fetch_fotmob_team_data(team_id)
                team_name = fotmobTeamData['details']['name']
                teamColor1 = fotmobTeamData['overview']['teamColors']['lightMode']
                teamColor2 = 'white'  #fotmobTeamData['overview']['teamColors']['darkMode']

                general_data = fotmobData['general']
                week = general_data['matchRound']
                matchDay = general_data['matchTimeUTCDate']
                parsed_date = datetime.fromisoformat(matchDay[:-1])
                formatted_date = parsed_date.strftime("%d.%m.%Y")
                leagueName = general_data['leagueName']
                leagueId = general_data['parentLeagueId']
                leagueSeason = general_data['parentLeagueSeason']
                leagueString = f"{leagueName} - {leagueSeason}"
                if "/" in week:
                    weekString = f"{week}  |  {formatted_date}"
                else:
                    weekString = f"{week}. Hafta  |  {formatted_date}"
                homeTeamName = general_data['homeTeam']['name']
                homeTeamId = general_data['homeTeam']['id']
                awayTeamName = general_data['awayTeam']['name']
                awayTeamId = general_data['awayTeam']['id']
                result = fotmobData['header']['status']['scoreStr']
                result_string = f"{homeTeamName} {result} {awayTeamName}"
                matchDetailString = f"{leagueString}  |  {weekString}"

                team_logo_image_url = f"https://images.fotmob.com/image_resources/logo/teamlogo/{team_id}.png"

                # Ana uygulama
                st.title("Match Analysis")

                # Renk tanımlamaları
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

                if selected_player_option:
                    # Oyuncu bilgilerini al
                    selected_player_name, selected_player_id, selected_team_id, selected_team_name, selected_player_number = list_players_and_get_selection_from_df(
                        team_players, 
                        teams_dict, 
                        selected_player_option, 
                        selected_team_id
                    )
                    
                    with st.sidebar:
                        player_fontsize = st.slider("Player Font Size", 10, 35, 25)
                    
                    # Hata kontrolü
                    if selected_player_id is not None and selected_team_id is not None and selected_fotmob_player_name is not None:
                        # Görselleştirmeleri oluştur
                        def generate_visualizations():
                            # Görselleştirmeleri oluştur
                            fig, axs = plt.subplots(2, 3, figsize=(20, 11), facecolor=pitch_color, edgecolor=line_color)
                            
                            # Grafiklerin her biri için uygun boyut ve font ayarları
                            match_details(axs[0, 0], selected_fotmob_player_id, team_name, player_name, selected_player_number, minutes, teamColor1, teamColor2, player_fontsize)

                            # df'nin boş olup olmadığını kontrol et
                            if df.empty:
                                axs[0, 1].text(0.5, 0.5, 'No data available for this player.', fontsize=12, ha='center', va='center')
                            else:
                                passes_and_key_passes(axs[0, 1], selected_player_id, df)
                            
                            touches_and_heatmap(axs[0, 2], selected_player_id, df)
                            defensive_actions(axs[1, 0], selected_player_id, df)
                            dribbling_carrying(axs[1, 1], selected_player_id, df)
                            shotmap(axs[1, 2], selected_player_id, df, shots_data, selected_fotmob_player_id)
                                                        
                            # Yazı boyutları için genel ayarlar
                            for ax in axs.flat:
                                ax.title.set_fontsize(18)  # Başlık yazı boyutu
                                ax.xaxis.label.set_fontsize(14)  # X ekseni etiket yazı boyutu
                                ax.yaxis.label.set_fontsize(14)  # Y ekseni etiket yazı boyutu
                                
                            # Add text and images to the figure
                            fig.text(0.2, 0.96, result_string, fontsize=34, fontweight='bold', ha='left', va='center', fontproperties=bold_prop, color=line_color)
                            fig.text(0.2, 0.92, matchDetailString, fontsize=18, ha='left', va='center', fontproperties=prop, color=line_color)
                            
                            league_logo_url = f"https://images.fotmob.com/image_resources/logo/leaguelogo/{leagueId}.png"
                            league_logo = Image.open(BytesIO(requests.get(league_logo_url).content)).convert("RGBA")

                            add_image(league_logo, fig, left=0.12, bottom=0.9, width=0.075, height=0.10)
                            
                            # Atak yönü okunu eklemek
                            ax = fig.add_subplot(111)  # Ana figüre eksen ekleyelim
                            ax.set_axis_off()  # Eksenleri gizleyelim

                            # FancyArrowPatch ile ok oluşturma
                            arrow = FancyArrowPatch((0.8075, 0.015), (0.91, 0.015), mutation_scale=20, color=line_color, lw=2.5, arrowstyle='->', transform=ax.transAxes)
                            ax.add_patch(arrow)  # Oku figüre ekle
                            
                            # Atak yönü yazısını eklemek
                            fig.text(0.788, 0.1, 'Atak Yönü', fontsize=15, ha='center', va='center', fontproperties=prop, color=line_color)
                            
                            endnote_ax = plt.axes([0.8, 0.93, 0.1, 0.05])
                            endnote_ax.text(0.98,0.5,'Veri: WhoScored ve FotMob\n@bariscanyeksin', color=line_color, fontsize=14, ha='right', va='center', fontproperties=prop, transform=endnote_ax.transAxes)
                            endnote_ax.axis('off')
                                                    
                            # Görselleştirmeleri göster
                            st.pyplot(fig)
                            
                            # Download button
                            buf = io.BytesIO()
                            fig.savefig(buf, format="png", dpi = 300, bbox_inches = "tight")
                            buf.seek(0)
                            
                            st.download_button(
                                label="Grafiği İndir",
                                data=buf,
                                file_name=f"{player_name}-{team_name}-{leagueName}-{weekString}.png",
                                mime="image/png"
                            )
                        
                        # Görselleştirmeleri oluştur
                        generate_visualizations()
                    else:
                        st.error("Seçilen oyuncunun bilgileri alınamadı. Lütfen tekrar deneyin.")
                else:
                    st.info("Lütfen bir oyuncu seçin.")
        else:
            st.error("Failed to fetch match data. Please check the match ID and try again.")
    else:
        st.error("Failed to fetch Fotmob data. Please check the IDs and try again.")
