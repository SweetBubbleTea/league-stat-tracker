import random
import re
import json
import math
import requests
import valorant

from config import *
from utilities import *
from bs4 import BeautifulSoup
from valorant.query import exp
from urllib.request import urlopen
from riotwatcher import LolWatcher, ApiError
from streamlit_option_menu import option_menu
import hydralit_components as hc
import streamlit as st
import altair as alt
import pandas as pd

# League constants
GAME_CHAMP_IMG_WIDTH = 40
GAME_ITEM_SUM_WIDTH = 30
MAX_TEAM_MEM = 5
MAX_MASTERY_SHOWCASE = 5
MINUTE = 60
MIN_NUM_MATCHES = 1
MAX_NUM_MATCHES = 15

# Valorant constants
LEADERBOARD_SIZE = 100

kills = 0
deaths = 0
assists = 0
cs = 0
total_wins = 0
total_losses = 0
surrender = False
win = False
firstBlood = False
summoner1 = ""
summoner2 = ""
role = ""
mode = ""
items = []
captions = []
mastery_list = {}


st.set_page_config(
    page_title="League Stats",
    page_icon="🧊",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': "https://github.com/SweetBubbleTea/league-stat-tracker",
        'Report a bug': "https://github.com/SweetBubbleTea/league-stat-tracker/issues",
        'About': "# A League of Legends Stat Tracker"
    }
)

hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden; }
        footer {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)

st.markdown("<h1 style='text-align: center;'>LoL Statistics</h1>", unsafe_allow_html=True)

st.sidebar.title("Configurations")
st.sidebar.write("")

personal_key = st.sidebar.text_input("Personal API Key", placeholder="Optional")

if personal_key:
    lol_watcher = LolWatcher(str(personal_key))
else:
    lol_watcher = LolWatcher(getKey())

with st.sidebar.expander("League of Legends"):
    st.write("---")
    summoner_name = st.text_input("Summoner Name", "")
    lol_region = st.selectbox('Region',
                              ("North America", "Europe West", "Europe Nordic & East", "Oceania", "Korea", "Japan",
                               "Brazil", "LAS", "LAN", "Russia", "Turkey"))

    max_matches = st.number_input("Number of Matches to Display", min_value=MIN_NUM_MATCHES, max_value=MAX_NUM_MATCHES,
                                  step=1)
    st.write("")

with st.sidebar.expander("Valorant"):
    st.write("---")
    val_region = st.selectbox("Region", ("North America", "Asia Pacific", "Brazil", "Europe", "Korea", "Latam"))
    st.write("")

selected = option_menu(
    menu_title=None,
    options=["League of Legends", "Valorant"],
    default_index=0,
    orientation="horizontal",
    styles={
        "container": {"padding": "0!important", "background-color": "#262730", "font-family": "sans serif"},
        "icon": {"color": "orange", "font-size": "25px"},
        "nav-link": {"font-size": "25px", "text-align": "left", "margin":"0px", "--hover-color": "#696565"},
    }
)

if selected == "League of Legends":
    st.write("")
    lol_match_region = matchIdentifier(lol_region)
    lol_region = leagueRegionIdentifier(lol_region)

    with st.expander("Champion Win Rate"):

        dataset = {
            "patch": [],
            "win_percent": []
        }

        current_wr = 0

        st.write("")
        champion = st.text_input("Champion Name")
        current_version = str(lol_watcher.data_dragon.versions_all()[0])
        current_version_url = current_version[:-2].replace(".", "_")
        st.write("")

        with hc.HyLoader('', hc.Loaders.standard_loaders, index=5):
            try:
                if champion != "":
                    for index, patches in enumerate(lol_watcher.data_dragon.versions_all()):
                        if index < 5:
                            url = "https://u.gg/lol/champions/{champ}/build?patch={patch}".format(champ=champion,
                                                                                                  patch=patches[
                                                                                                        :-2].replace(
                                                                                                      ".", "_"))
                            result = requests.get(url)
                            doc = BeautifulSoup(result.text, "lxml")

                            ranking_stats = doc.find("div", {"class": "content-section champion-ranking-stats-normal"})
                            label = ranking_stats.find_all("div", {"class": "label"})
                            tier = str(label[1].find_parent()["class"][1])
                            win_rate = doc.find("div", {"class": "win-rate " + tier}).next.text
                            dataset["patch"].insert(0, float(patches[:-2]))
                            dataset["win_percent"].insert(0, float(win_rate[:-1]))
                            if str(patches[:-2]) == str(current_version[:-2]):
                                current_wr = win_rate

                    df = pd.DataFrame(dataset)

                    line_chart = alt.Chart(df).mark_line(tooltip=True, point=True, strokeWidth=5).encode(
                        x=alt.X("patch:O", title="Patch", sort=dataset["patch"]),
                        y=alt.Y("win_percent:Q", title="Win Rate [%]", scale=alt.Scale(domain=[40, 60])),
                    ).properties(
                        title="{champ} Win Rate ({wr})".format(champ=champion.title(), wr=current_wr)
                    ).configure_point(
                        size=180
                    ).interactive()

                    st.altair_chart(line_chart, use_container_width=True)
            except AttributeError:
                st.error("No data available")

    with st.expander("Champion Randomizer"):

        st.markdown(
            """
            <style>
                .stButton > button {
                    width: 100%;
                }
            </style>
            """,
            unsafe_allow_html = True
        )
        col1, col2, col3 = st.columns(3)
        if col2.button('Roll'):
            max_num_champs = len(lol_watcher.data_dragon.champions(version=current_version)["data"])
            champ_num = random.randint(1, max_num_champs)

            for champ_count, champ_name in enumerate(lol_watcher.data_dragon.champions(version=current_version)["data"]):
                if champ_count == champ_num:
                    st.markdown(
                        """
                            <style>
                                .css-13sdm1b p {
                                    text-align: center;
                                    font-size: larger;
                                }
                            </style>
                        """,
                        unsafe_allow_html=True
                    )
                    col2.write(champ_name.upper())
                    break

    icon_ctnr, stats_ctnr, rp = st.columns([0.5, 2, 1], gap="small")
    champion_asset_json = "http://ddragon.leagueoflegends.com/cdn/{}/data/en_US/champion.json".format(current_version)
    try:
        summoner = lol_watcher.summoner.by_name(lol_region, summoner_name)
        with icon_ctnr:
            image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/profileicon/{icon}.png".format(
                version=current_version,
                icon=summoner["profileIconId"])
            st.image(image, use_column_width="auto")
        with stats_ctnr:
            ranked = lol_watcher.league.by_summoner(lol_region, summoner["id"])
            st.subheader("{}".format(summoner["name"]))
            try:
                st.text(ranked[0]["tier"] + " " + ranked[0]["rank"])
            except IndexError:
                st.text("Unranked")
            st.text("Summoner level: {}".format(summoner["summonerLevel"]))
            st.text("Patch: " + current_version[:-2])

        mastery = lol_watcher.champion_mastery.by_summoner(lol_region, summoner["id"])
        response = urlopen(champion_asset_json)
        champion = json.loads(response.read())

        for items, champ in enumerate(mastery):
            if items != MAX_MASTERY_SHOWCASE:
                mastery_list[items] = [str(champ["championId"])]
                captions.append(str("{:,}").format(champ["championPoints"]))
            else:
                break

        with st.expander("Top 5 Champion Mastery"):
            for mastery in mastery_list:
                for champions, champ_info in champion["data"].items():
                    if champ_info["key"] == mastery_list[mastery][0]:
                        mastery_list[mastery].append(champions)

            m1, m2, m3, m4, m5 = st.columns(MAX_MASTERY_SHOWCASE)
            mastery_col_lst = [m1, m2, m3, m4, m5]

            for num_mastery, mastery_col in enumerate(mastery_col_lst):
                for x in mastery_list:
                    if num_mastery == x:
                        image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{mastery}.png".format(
                            version=current_version, mastery=mastery_list[x][1])
                        mastery_col.image(image, caption=captions[num_mastery] + " pts")

        st.subheader("Most Recent Matches")
        match_id_list = lol_watcher.match.matchlist_by_puuid(region=lol_match_region, puuid=summoner["puuid"])
        summoner_spell = lol_watcher.data_dragon.summoner_spells(version="12.13.1")["data"]

        for match_id_index, match_id in enumerate(match_id_list):
            if match_id_index < max_matches:
                game = lol_watcher.match.by_id(lol_match_region, match_id)["info"]
                match = lol_watcher.match.by_id(lol_match_region, match_id)["info"]["participants"]
                with st.expander(str(match_id_index + 1)):
                    with st.container():
                        mins = game["gameDuration"] // MINUTE
                        secs = game["gameDuration"] % MINUTE
                        m0, m1, m2, m3, m4, m5 = st.columns([0.4, 0.1, 0.4, 0.1, 0.65, 0.5])

                        for count, match_player_data in enumerate(match):
                            if match_player_data["summonerName"].lower() == summoner_name.lower():
                                if match_player_data["win"]:
                                    win = True
                                    total_wins += 1
                                else:
                                    total_losses += 1
                                kills = match_player_data["kills"]
                                deaths = match_player_data["deaths"]
                                assists = match_player_data["assists"]
                                cs = match_player_data["totalMinionsKilled"]
                                if match_player_data["firstBloodKill"]:
                                    firstBlood = True
                                items = [match_player_data["item0"], match_player_data["item1"],
                                         match_player_data["item2"],
                                         match_player_data["item3"], match_player_data["item4"],
                                         match_player_data["item5"]]
                                summoner1 = str(match_player_data["summoner1Id"])
                                summoner2 = str(match_player_data["summoner2Id"])
                                role = match_player_data["teamPosition"]
                                mode = game["gameMode"]
                                if match_player_data["gameEndedInEarlySurrender"] or \
                                        match_player_data["gameEndedInSurrender"]:
                                    surrender = True

                            image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champ}.png" \
                                .format(version=current_version, champ=match_player_data["championName"])
                            participant = match_player_data["summonerName"] + " - lv " + str(
                                match_player_data["champLevel"])

                            if count < MAX_TEAM_MEM:
                                with m1:
                                    st.image(image, width=GAME_CHAMP_IMG_WIDTH)
                                with m2:
                                    st.write(participant)
                                    st.write("")
                            else:
                                with m3:
                                    st.image(image, width=GAME_CHAMP_IMG_WIDTH)
                                with m4:
                                    st.write(participant)
                                    st.write("")
                        with m5:
                            st.subheader("Game Stats")
                            st.text("Duration: " + str(mins) + "m " + str(secs) + "s ")
                            st.text("Mode: " + mode)
                            if win:
                                st.text("Result: Victory")
                            else:
                                if surrender:
                                    st.text("Result: Surrender")
                                else:
                                    st.text("Result: Defeat")
                            if role == "UTILITY":
                                role = "SUPPORT"
                            elif role != "":
                                st.text("Role: " + role)
                            if firstBlood:
                                st.text("First Blood")
                            st.text("KDA: " + str(kills) + "/" + str(deaths) + "/" + str(assists))
                            st.text("CS: " + str(cs) + " (" + str(round(cs / mins, 1)) + ")")

                    with st.container():
                        st.text("")
                        spacing_col_front, item_build_text, i1, i2, i3, i4, i5, i6, sum1_col, sum2_col = \
                            st.columns([0.075, 0.05, 0.02, 0.02, 0.02, 0.02, 0.02, 0.04, 0.02, 0.25])
                        item_col_lst = [i1, i2, i3, i4, i5, i6]
                        with item_build_text:
                            st.text("Items Built: ")
                        for col_index, item_col in enumerate(item_col_lst):
                            for count, item in enumerate(items):
                                if col_index == count:
                                    if item != 0:
                                        image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/item/{item}.png".\
                                            format(version=current_version, item=item)
                                        item_col.image(image, width=GAME_ITEM_SUM_WIDTH)

                        for name, match_player_data in summoner_spell.items():
                            if match_player_data["key"] == summoner1:
                                summoner1 = name
                            elif match_player_data["key"] == summoner2:
                                summoner2 = name

                        with sum1_col:
                            image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{sum1}.png".format(
                                version=current_version, sum1=summoner1)
                            sum1_col.image(image, width=GAME_ITEM_SUM_WIDTH)
                        with sum2_col:
                            image = "http://ddragon.leagueoflegends.com/cdn/{version}/img/spell/{sum2}.png".format(
                                version=current_version, sum2=summoner2)
                            sum2_col.image(image, width=GAME_ITEM_SUM_WIDTH)

        if total_wins + total_losses != 0:
            win_rate = math.floor((total_wins / (total_wins + total_losses)) * 100)
            with rp:
                st.metric(label="Win Rate for Last " + str(int(max_matches)) + " matches", value=str(win_rate) + "%")
    except ApiError as err:
        if err.response.status_code == 429:
            st.error("Should retry in {} seconds due several requests".format(err.response.headers["Retry-After"]))
        elif err.response.status_code == 404:
            st.error("Cannot find the summoner")
        elif err.response.status_code == 403:
            pass
        else:
            raise

if selected == "Valorant":
    st.write("")
    val_region = valorantRegionIdentifier(val_region)

    try:
        if personal_key:
            val_client = valorant.Client(str(personal_key), region=val_region)
        else:
            val_client = valorant.Client(getKey(), region=val_region)

        icon_ctnr, info_ctnr, rp1 = st.columns([1, 4.5, 1])

        with icon_ctnr:
            image = "assets/logo/valorant_logo.png"
            st.image(image)
        with info_ctnr:
            st.subheader("Valorant")
            current_act = val_client.get_acts()
            last_act = list(current_act)[-1].name.lower().capitalize()
            last_act_query = last_act.split()
            if last_act_query[0] == "Episode":
                st.text(last_act)
                st.text("Act 1")
            else:
                episode = list(current_act)[-1 - int(last_act_query[1])].name.lower().capitalize()
                st.text(episode)
                st.text(last_act)
            st.text("Patch " + val_client.get_content().version[8:])

        st.write("")
        with st.expander("Leaderboard"):
            st.write("")

            spacing_front, rank, name, rr = st.columns([.5, .8, 1, .8])

            with rank:
                st.markdown("#### **Rank**")
            with name:
                st.markdown("#### **Name**")
            with rr:
                st.markdown("#### **Rating**")

            player_num = st.number_input("Number of Players", min_value=1, max_value=20, step=1, value=10)
            try:
                leaderboard = val_client.get_leaderboard(size=player_num)
                for player in leaderboard.players:
                    with rank:
                        st.text(str(player.leaderboardRank))
                    with name:
                        st.text(str(player.gameName))
                    with rr:
                        st.text(str(player.rankedRating))
            except requests.exceptions.HTTPError:
                pass

        with st.expander("Radiant Query"):
            st.write("")
            st.info("Obtains the queried player(s) in Radiant")

            radiant_query = st.text_input("Esports org or player name")
            if radiant_query != "":
                for pg in range(0, 5):
                    leaderboard = val_client.get_leaderboard(size=LEADERBOARD_SIZE, page=pg)
                    players = leaderboard.players.get_all(gameName=exp('.startswith', radiant_query))
                    for name in players:
                        st.write(name.gameName)

        with st.expander("Skins"):
            st.write("")

            st.info("Obtains every skin from the queried skin bundle")
            skin_query = st.text_input("Skin bundle name").lower().capitalize()

            if skin_query != "":
                skin_query_alias = skin_query.split()[0]
                skin = val_client.get_skins().get_all(name=exp('.startswith', skin_query_alias))
                try:
                    st.image("assets/bundles/{}.png".format(skin_query), width=400)
                except FileNotFoundError:
                    pass

                match skin_query_alias:
                    case "Sarmad":
                        st.write("Blade of Serket")
                    case "Prelude":
                        st.write("Blade of Chaos")
                    case "Undercity":
                        st.write("Hack")
                    case "Tigris":
                        st.write("Hu Else")
                    case "Protocol":
                        st.write("Personal Administrative Melee Unit")
                    case "Nunca":
                        st.write("Catrina")
                    case "Rgx":
                        skin = val_client.get_skins().get_all(name=exp('.startswith', "RGX"))
                    case "Spectrum":
                        st.write("Waveform")
                    case "Sentinel":
                        st.write("Relic of the Sentinel")
                    case "Ruination":
                        st.write("Broken Blade of the Ruined King")
                    case "Origin":
                        st.write("Crescent Blade")
                    case "Tethered":
                        st.write("Prosperity")
                    case "Forsaken":
                        st.write("Ritual Blade")
                    case "Valorant":
                        skin = val_client.get_skins().get_all(name=exp('.startswith', "VALORANT"))
                    case "Blastx":
                        skin = val_client.get_skins().get_all(name=exp('.startswith', "BlastX"))
                    case "Gun":
                        skin = val_client.get_skins().get_all(
                            name=exp('.startswith', "Gravitational Uranium Neuroblaster"))
                    case _:
                        pass
                for name in skin:
                    st.write(name.name)

        with st.expander("Esports Org"):

            st.info("Obtain information about the queried Esports organization.")

            org = st.text_input("Esports Organization")
            st.write("")
            spacing, q1, q2, q3 = st.columns([0.5, 1, 0.6, 1.5])

            if orgIdentifier(org) is not None:
                org = orgIdentifier(org)

            if org != "":
                url = "https://liquipedia.net/valorant/{}".format(org)
                result = requests.get(url)
                doc = BeautifulSoup(result.text, "lxml")

                table = doc.find(class_="wikitable wikitable-striped roster-card")
                info_card = doc.find(class_="fo-nttax-infobox wiki-bordercolor-light")

                try:
                    roster = table.find_all(href=re.compile("valorant/"))
                    with q2:
                        for member in roster:
                            name = member.text
                            if name != "":
                                st.write(name)

                    with q1:
                        try:
                            icon = "assets/esports/{}.png".format(org)
                            st.image(icon, width=200)
                        except FileNotFoundError:
                            st.image("assets/esports/basic/player silhouette.jpeg", width=200)

                    with q3:
                        total_winnings = " N/A"
                        esports_location = " N/A"
                        ign = " N/A"
                        esports_region = " N/A"
                        query_region = ""
                        div = info_card.find_all(class_="infobox-cell-2")
                        for index, member in enumerate(div):
                            name = member.text
                            if name == "Approx. Total Winnings:":
                                total_winnings = div[index + 1].text
                            elif name == "Location:":
                                esports_location = div[index + 1].text
                            elif name == "In-Game Leader:":
                                ign = div[index + 1].text
                            elif name == "Region:":
                                esports_region = div[index + 1].text.lower().strip()

                        match esports_region:
                            case "middle east":
                                query_region = "mena"
                            case "north america":
                                query_region = "north-america"
                            case "asia pacific":
                                query_region = "asia-pacific"
                            case _:
                                query_region = esports_region

                        vlr_url = "https://www.vlr.gg/rankings/{}".format(query_region)
                        vlr_result = requests.get(vlr_url)
                        vlr_doc = BeautifulSoup(vlr_result.text, "lxml")

                        mod_scroll = vlr_doc.find("div", {"class": "mod-scroll"})
                        ranking_list = mod_scroll.find_all(class_="rank-item wf-card fc-flex")

                        for index, element in enumerate(ranking_list):
                            if index < 10:
                                if str(element.find("div", {"class": "ge-text"}).next.text).strip() == org:
                                    esport_rank = element.find(class_="rank-item-rank-num").text.strip()
                                    st.text("Rank: " + esport_rank)
                                    break

                        st.text("Location:" + esports_location)
                        st.text("Region: " + esports_region.title())
                        st.text("Total Winnings: " + total_winnings)
                        st.text("IGN:" + ign)
                except AttributeError:
                    st.error("Provide the EXACT spelling of the org name for best results. "
                             "Not all common aliases will be catched.")
                st.write("")

    except requests.exceptions.HTTPError as err:
        if err.response.status_code == 403:
            st.error("Invalid or expired API key")

st.sidebar.title("")
st.sidebar.title("")
st.sidebar.title("")
with st.sidebar.expander("About this app"):
    st.write("Designed by **SweetBubbleTea** as a personal project.")
    st.write("GitHub: https://github.com/SweetBubbleTea/league-stat-tracker")
    st.write("Used to track different stats from League of Legends")

with st.sidebar.expander("Disclaimer"):
    st.write("League Stat Tracker is a personal project that is **not** associated with Riot Games nor League of "
             "Legends in any shape or form.")
    st.write("League Stat Tracker is usable without having to obtain your own personal API key from Riot Games; "
             "however, "
             "Development API keys from Riot Games has a shelf life of 24 hours. This would mean that the in order to "
             "use the web application, a personal API key from Riot Games **MAY** be needed.")
