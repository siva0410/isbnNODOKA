import os
import json
import urllib.request
from pprint import pprint

from notion_client import Client

notion = Client(auth=os.environ['NOTION_TOKEN'])


def getJSON(isbn):
    openDB = "https://api.openbd.jp/v1/get?isbn={}&pretty"
    url = openDB.format(isbn)
    
    req = urllib.request.Request(url)
    
    with urllib.request.urlopen(req) as res:
        content = json.load(res)

    return content


def insertNotion(content):    
    db = notion.pages.create(
        **{
           'parent': {'database_id':os.environ['NOTION_DB']},
           'properties': {
               'ISBN': {
                   'rich_text': [
                       {                                                
                       'text': {
                           'content': content[0]["summary"]["isbn"],                    
                           },
                       }
                   ],
               },
               'ステータス': {
                   'select': {
                       'name': 'これから読む'
                   },
               },
               'タイトル': {
                   # 'id': 'title',
                   'title': [
                       {
                       'text': {
                           'content': content[0]["summary"]["title"],
                           },
                       }
                   ],
               },
               '出版社': {
                   # 'id': 'gWtB',
                   'select': {
                       'name': content[0]["summary"]["publisher"]
                       },
               },
               '発行年月日': {
                   'date': {
                       'end': None,
                       'start': content[0]["summary"]["pubdate"],
                       'time_zone': None
                       },
               },
               '著者': {
                   'rich_text': [
                       {                   
                       'text': {
                           'content': content[0]["summary"]["author"],
                           },
                       }
                   ],
               },
               '表紙': {
                   'files': [
                   {
                   'external': {'url': content[0]["summary"]["cover"]},
                               'name': content[0]["summary"]["cover"],
                               'type': 'external'
                   }
               ],                                                       
           },
        }
    }
    )    

    return db
    

def getBookInfo(isbn):
    content = getJSON(isbn)
    db = insertNotion(content)
    
    return content
