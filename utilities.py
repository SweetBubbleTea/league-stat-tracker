def regionIdentifier(region):
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


