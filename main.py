import json
import math

from config import *
from utilities import *
from urllib.request import urlopen
from riotwatcher import LolWatcher, ApiError
import streamlit as st

win = False
kills = 0
deaths = 0
assists = 0
cs = 0
firstBlood = False
items = []
summoner1 = ""
summoner2 = ""
role = ""
mode = ""
surrender = False
mastery_list = {}
captions = []

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

st.title("LoL Statistics")
st.empty().write("---")

st.sidebar.header("Settings")
personal_key = st.sidebar.text_input("Personal API Key", placeholder="Optional")

if personal_key:
    lol_watcher = LolWatcher(str(personal_key))
else:
    lol_watcher = LolWatcher(getKey())

summoner_name = st.sidebar.text_input("Summoner Name", "")
region = st.sidebar.selectbox('Region',
                              ("North America", "Europe West", "Europe Nordic & East", "Oceania",
                               "Korea", "Japan", "Brazil", "LAS", "LAN", "Russia", "Turkey"))

max_matches = st.sidebar.number_input("Number of Matches to Display", min_value=1, max_value=15, step=1)

champion_asset_json = "http://ddragon.leagueoflegends.com/cdn/12.13.1/data/en_US/champion.json"
match_region = matchIdentifier(region)
region = regionIdentifier(region)
icon_ctnr, stats_ctnr, rp = st.columns([0.5, 2, 1], gap="small")

try:
    summoner = lol_watcher.summoner.by_name(region, summoner_name)
    with icon_ctnr:
        image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/profileicon/{}.png".format(
            summoner["profileIconId"])
        st.image(image, use_column_width="auto")
    with stats_ctnr:
        ranked = lol_watcher.league.by_summoner(region, summoner["id"])
        st.subheader("{}".format(summoner["name"]))
        try:
            st.text(ranked[0]["tier"] + " " + ranked[0]["rank"])
        except IndexError:
            st.text("Unranked")
        st.text("Summoner level: {}".format(summoner["summonerLevel"]))

    mastery = lol_watcher.champion_mastery.by_summoner(region, summoner["id"])
    response = urlopen(champion_asset_json)
    champion = json.loads(response.read())
    for items, champ in enumerate(mastery):
        if items != 5:
            mastery_list[items] = [str(champ["championId"])]
            captions.append(str("{:,}").format(champ["championPoints"]))
        else:
            break

    with st.expander("Top 5 Champion Mastery"):
        for mastery in mastery_list:
            for champions, champ_info in champion["data"].items():
                if champ_info["key"] == mastery_list[mastery][0]:
                    mastery_list[mastery].append(champions)

        m1, m2, m3, m4, m5 = st.columns(5)
        mastery_col_lst = [m1, m2, m3, m4, m5]

        for num_mastery, mastery_col in enumerate(mastery_col_lst):
            for x in mastery_list:
                if num_mastery == x:
                    image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png".format(
                        mastery_list[x][1])
                    mastery_col.image(image, caption=captions[num_mastery] + " pts")

    st.subheader("Most Recent Matches")
    match_id_list = lol_watcher.match.matchlist_by_puuid(region=match_region, puuid=summoner["puuid"])
    summoner_spell = lol_watcher.data_dragon.summoner_spells(version="12.13.1")["data"]

    total_wins = 0
    total_losses = 0

    number_of_matches = 0
    for match_id in match_id_list:
        if number_of_matches < max_matches:
            game = lol_watcher.match.by_id(match_region, match_id)["info"]
            match = lol_watcher.match.by_id(match_region, match_id)["info"]["participants"]
            with st.expander(str(number_of_matches + 1)):
                with st.container():
                    mins = game["gameDuration"] // 60
                    secs = game["gameDuration"] % 60
                    m0, m1, m2, m3, m4, m5 = st.columns([0.4, 0.1, 0.4, 0.1, 0.65, 0.5])

                    for count, match_player_data in enumerate(match):
                        if match_player_data["summonerName"] == summoner_name:
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
                            items = [match_player_data["item0"], match_player_data["item1"], match_player_data["item2"],
                                     match_player_data["item3"], match_player_data["item4"], match_player_data["item5"]]
                            summoner1 = str(match_player_data["summoner1Id"])
                            summoner2 = str(match_player_data["summoner2Id"])
                            role = match_player_data["teamPosition"]
                            mode = game["gameMode"]
                            if match_player_data["gameEndedInEarlySurrender"] or match_player_data["gameEndedInSurrender"]:
                                surrender = True

                        if count < 5:
                            with m1:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png"\
                                    .format(match_player_data["championName"])
                                st.image(image, width=40)
                            with m2:
                                st.write(match_player_data["summonerName"] + " - lv" + str(match_player_data["champLevel"]))
                                st.write("")
                        else:
                            with m3:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png".format(
                                    match_player_data["championName"])
                                st.image(image, width=40)
                            with m4:
                                st.write(match_player_data["summonerName"] + " - lv" + str(match_player_data["champLevel"]))
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
                    index = 0
                    with item_build_text:
                        st.text("Items Built: ")
                    for item_col in item_col_lst:
                        for count, item in enumerate(items):
                            if index == count:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/item/{}.png".format(item)
                                item_col.image(image, width=30)
                        index += 1

                    for name, match_player_data in summoner_spell.items():
                        if match_player_data["key"] == summoner1:
                            summoner1 = name
                        elif match_player_data["key"] == summoner2:
                            summoner2 = name

                    with sum1_col:
                        image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/spell/{}.png".format(summoner1)
                        sum1_col.image(image, width=30)
                    with sum2_col:
                        image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/spell/{}.png".format(summoner2)
                        sum2_col.image(image, width=30)
        number_of_matches += 1

    if total_wins + total_losses != 0:
        win_rate = math.floor((total_wins / (total_wins + total_losses)) * 100)
        st.sidebar.metric(label="Win Rate for Last " + str(int(max_matches)) + " matches", value=str(win_rate) + "%")
except ApiError as err:
    if err.response.status_code == 429:
        st.error("Should retry in {} seconds due several requests".format(err.response.headers["Retry-After"]))
    elif err.response.status_code == 404:
        st.error("Cannot find the summoner")
    elif err.response.status_code == 403:
        st.sidebar.info("Insert an valid Summoner name")
    else:
        raise

st.sidebar.title("")
st.sidebar.title("")
with st.sidebar.expander("About this app"):
    st.write("Designed by **SweetBubbleTea** as a personal project.")
    st.write("GitHub: https://github.com/SweetBubbleTea/league-stat-tracker")
    st.write("Used to track different stats from League of Legends")

with st.sidebar.expander("Disclaimer"):
    st.write("League Stat Tracker is a personal project that is **not** associated with Riot Games nor League of Legends in any shape or form.")
    st.write("League Stat Tracker is usable without having to obtain your own personal API key from Riot Games; however, "
             "Development API keys from Riot Games has a shelf life of 24 hours. "
             "This would mean that the in order to use the web application, a personal API key from Riot Games **MAY** be needed.")