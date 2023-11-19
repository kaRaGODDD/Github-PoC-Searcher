import asyncio
import aiohttp
import json

from bs4 import BeautifulSoup

import os
#from dotenv import load_dotenv

#load_dotenv()

#def get_github_token_from_dotenv():
    #return os.getenv('GITHUB')

def write_json(url : str,lst : list) -> None:
    with open("/home/kara/python/course_project/data/"+url+".json","a",encoding="utf-8") as file:
        json.dump(lst,file,indent=4,ensure_ascii=False)
                 

def read_from_json(json_name : str) -> list:
    with open(json_name,"r") as file:
        lst = json.load(f)
    return lst

async def parse_all_packetstorm_security(how_many_pages_need_to_parse : int):
    
    async with aiohttp.ClientSession() as session:
        async with session.get("https://packetstormsecurity.com/search/files/page{1}/?s=files&q=proof%20of%20concept") as response:
           
            soup = BeautifulSoup(await response.text(),"lxml") 
            pages_on_source = int(soup.find(attrs={'id':'nv'}).find("strong").text.lstrip("Page 1 of ")) 
             
            if how_many_pages_need_to_parse < pages_on_source:

                for i in range(1,how_many_pages_need_to_parse + 1):
                    async with aiohttp.ClientSession() as current_session:
                        async with current_session.get(f"https://packetstormsecurity.com/search/files/page{i}/?s=files&q=proof%20of%20concept") as current_response:

                            object_of_soup = BeautifulSoup(await current_response.text(),"lxml")
                            get_all_cards  = object_of_soup.find_all("dl",class_="file")
                            data = []
                            
                        

                            for card in get_all_cards:

                                date_source_url = str("https://packetstormsecurity.com"+card.find("a").get("href"))
                                get_date = card.find("dd",class_="datetime").text
                                get_time = card.find("dd",class_="datetime").find("a").get("title")
                                date_time = str(get_date + " " + get_time)
                                get_author = card.find("dd",class_="refer").text
                                get_cve = card.find("dd",class_="cve")

                                if (type(get_cve) is not type(None)):
                                    text = get_cve.text.lstrip("advisories | ")
                                else:
                                    text = "Author did not provide CVE"
                            

                                data.append(
                                    {
                                        "URL" : date_source_url, 
                                        "Date and Time" : date_time,
                                        "Author" : get_author,
                                        "CVE" : text
                                    }
                                )
                            write_json(f"scrapping_packetstormsecurity{i}",data)            
            else:
                print("Wrong amount of pages")
                



async def scrapping_github_open_repository(repository_name : str):
    get_token_access = get_github_token_from_dotenv()


async def main():
    PAGES_TO_PARSE = 1 
    async with asyncio.TaskGroup() as tg:
        parse_all_site = tg.create_task(parse_all_packetstorm_security(PAGES_TO_PARSE))


if __name__ == "__main__":
    asyncio.run(main())
