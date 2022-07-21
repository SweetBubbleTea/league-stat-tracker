def leagueRegionIdentifier(region):
    match region:
        case "North America":
            return "na1"
        case "Europe West":
            return "EUW1"
        case "Europe Nordic & East":
            return "EUN1"
        case "Oceania":
            return "OC1"
        case "Korea":
            return "KR"
        case "Japan":
            return "JP1"
        case "Brazil":
            return "BR1"
        case "LAS":
            return "LA1"
        case "LAN":
            return "LA2"
        case "Russia":
            return "RU"
        case "Turkey":
            return "TR1"

def matchIdentifier(region):
    match region:
        case ("North America"|"Brazil"|"LAN"|"LAS"):
            return "Americas"
        case ("Europe West"|"Europe Nordic & East"|"Turkey"|"Russia"):
            return "Europe"
        case "Oceania":
            return "Sea"
        case ("Korea"|"Japan"):
            return "Asia"

def valorantRegionIdentifier(region):
    match region:
        case "Asia Pacific":
            return "ap"
        case "Brazil":
            return "br"
        case "Europe":
            return "eu"
        case "Korea":
            return "kr"
        case "Latam":
            return "latam"
        case "North America":
            return "na"

def orgIdentifier(org):
    match org:
        case "Version 1" | "V1":
            return "version1"
        case "Cloud 9":
            return "c9"
        case "Tsm" | "Team Solo Mid" | "tsm":
            return "TSM"
        case "Optic" | "Optic Gaming" | "optic":
            return "OpTic_Gaming"
        case "Loud" | "loud":
            return "LOUD"
        case "Guild" | "guild":
            return "Guild Esports"
        case "Fpx" | "Fun Plus Phoenix" "fun plus phoenix" | "fpx":
            return "FunPlus Phoenix"
        case "Leviatan" | "leviatan":
            return "Leviatán"
        case "Xset" | "xset":
            return "XSET"
        case "Kru" | "KRU Esports" | "kru" | "kru esports":
            return "KRÜ_Esports"
        case "Tl" | "tl" | "team liquid":
            return "Team Liquid"
        case "100T" | "100t" | "100 thieves":
            return "100 Thieves"
        case "Zeta" | "Zeta Division":
            return "ZETA_DIVISION"
        case "Faze" | "Faze clan" | "Faze Clan":
            return "FaZe Clan"
        case "Imt":
            return "Immortals"
        case "Nyfu":
            return "NYFU"
        case "Darkzero Esports" | "Darkzero":
            return "DarkZero Esports"
        case "Geng" | "Gen.g" | "Geng Esports":
            return "Gen.G Esports"
        case _:
            return None