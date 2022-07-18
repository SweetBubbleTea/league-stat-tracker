import json
import math

from config import *
from utilities import *
from urllib.request import urlopen
from riotwatcher import LolWatcher, ApiError
import streamlit as st

lol_watcher = LolWatcher(KEY)

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
summoner_name = st.sidebar.text_input("Summoner Name", "")
region = st.sidebar.selectbox('Region',
                              ("North America", "Europe West", "Europe Nordic & East", "Oceania",
                               "Korea", "Japan", "Brazil", "LAS", "LAN", "Russia", "Turkey"))

max_matches = st.sidebar.number_input("Number of Matches to Display", min_value=1, max_value=15, step=1)




champion_url = "http://ddragon.leagueoflegends.com/cdn/12.13.1/data/en_US/champion.json"
match_region = matchIdentifier(region)
region = regionIdentifier(region)
icon_ctnr, stats_ctnr, rp = st.columns([0.5, 2, 1], gap="small")
mastery_list = {}
captions = []

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
    response = urlopen(champion_url)
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
        index = 0
        for mastery_col in mastery_col_lst:
            for x in mastery_list:
                if index == x:
                    image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png".format(
                        mastery_list[x][1])
                    mastery_col.image(image, caption=captions[index] + " pts")
            index += 1

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
                    win = False
                    kills = 0
                    deaths = 0
                    assists = 0
                    cs = 0
                    firstBlood = False
                    mins = game["gameDuration"] // 60
                    secs = game["gameDuration"] % 60
                    items = []
                    summoner1 = ""
                    summoner2 = ""
                    role = ""
                    mode = ""
                    m0, m1, m2, m3, m4, m5 = st.columns([0.4, 0.1, 0.4, 0.1, 0.65, 0.5])

                    for count, json in enumerate(match):
                        if json["summonerName"] == summoner_name:
                            if json["win"]:
                                win = True
                                total_wins += 1
                            else:
                                total_losses += 1
                            kills = json["kills"]
                            deaths = json["deaths"]
                            assists = json["assists"]
                            cs = json["totalMinionsKilled"]

                            if json["firstBloodKill"]:
                                firstBlood = True
                            items = [json["item0"], json["item1"], json["item2"], json["item3"], json["item4"],
                                     json["item5"]]
                            summoner1 = str(json["summoner1Id"])
                            summoner2 = str(json["summoner2Id"])
                            role = json["teamPosition"]
                            mode = game["gameMode"]

                        if count < 5:
                            with m1:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png"\
                                    .format(json["championName"])
                                st.image(image, width=41)
                            with m2:
                                st.text(json["summonerName"] + " - lv" + str(json["champLevel"]))
                                st.text("")
                        else:
                            with m3:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/champion/{}.png".format(
                                    json["championName"])
                                st.image(image, width=41)
                            with m4:
                                st.text(json["summonerName"] + " - lv" + str(json["champLevel"]))
                                st.text("")
                    with m5:
                        st.subheader("Game Stats")
                        st.text("Duration: " + str(mins) + "m " + str(secs) + "s ")
                        st.text("Mode: " + mode)
                        if win:
                            st.text("Result: Victory")
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
                    i00, i0, i1, i2, i3, i4, i5, i6, i7, i8 = st.columns([0.075, 0.05, 0.02, 0.02, 0.02, 0.02, 0.02,
                                                                          0.04, 0.02, 0.25])
                    item_col_lst = [i1, i2, i3, i4, i5, i6]
                    index = 0
                    with i0:
                        st.text("Items Built: ")
                    for item_col in item_col_lst:
                        for count, item in enumerate(items):
                            if index == count:
                                image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/item/{}.png".format(item)
                                item_col.image(image, width=30)
                        index += 1

                    for name, json in summoner_spell.items():
                        if json["key"] == summoner1:
                            summoner1 = name
                        elif json["key"] == summoner2:
                            summoner2 = name

                    with i7:
                        image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/spell/{}.png".format(summoner1)
                        i7.image(image, width=30)
                    with i8:
                        image = "http://ddragon.leagueoflegends.com/cdn/12.13.1/img/spell/{}.png".format(summoner2)
                        i8.image(image, width=30)
        number_of_matches += 1

    if total_wins + total_losses != 0:
        st.sidebar.metric(label="Win Rate for Last " + str(int(max_matches)) + " matches", value=str(math.floor((total_wins / (total_wins + total_losses)) * 100)) + "%")

    st.sidebar.title("")
    st.sidebar.title("")
    with st.sidebar.expander("About this app"):
        st.write("Designed by **SweetBubbleTea** as a personal project.")
        st.write("GitHub: https://github.com/SweetBubbleTea/league-stat-tracker")
        st.write("Used to track different stats from League of Legends")

except ApiError as err:
    if err.response.status_code == 429:
        st.error("Should retry in {} seconds due several requests".format(err.response.headers["Retry-After"]))
    elif err.response.status_code == 404:
        st.error("Cannot find the summoner")
    elif err.response.status_code == 403:
        st.sidebar.info("Insert an valid Summoner name")
    else:
        raise
