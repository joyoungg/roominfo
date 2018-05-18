#고시원
# -*- coding: utf-8 -*-
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import os
import re

#3900
for num in range(3899, 3901):
    c_url = 'http://roomnspace.co.kr/gosiwon/info/{}'.format(num)
    html = urlopen(c_url).read()
    soup = BeautifulSoup(html, 'html.parser')

    summary = soup.select_one('div.detail_container.gs > section.detail_content > aside')

    category = summary.find('span', class_='category').text
    name = summary.find('li',class_='name').text
    tel = ''.join( re.findall('\d+', summary.find('li',class_='tel').find('span').text))
    room_yn = ''.join( re.findall('\d', summary.find('li',class_='room_yn').text))
    addr = summary.find('span',class_='addr').text
    data = {
        'category' : category,
        'name' : name,
        'tel' : tel,
        'room_yn': room_yn,
        'addr' : addr
    }

    basicInfo = soup.find('article', id='go_basicInfo').select('div > ul > li')
    b_info = {}
    BASIC={}
    for item in basicInfo:
        info = item.find('span',class_='heading').string

        if info == '고시원 사용 층 / 건물 총 층수' :
            content = ''.join(re.sub('[가-힣]','',item.ul.li.text))
        elif info == '총 방 개수':
            content = ''.join(re.sub('[가-힣]','',item.ul.li.text))
        elif info == '복도 넓이' :
            content = ''.join(re.findall('\d+\.?\d?', item.ul.li.text))
        else :
            content =  item.ul.li.string
        b_info[info]=content
    data.update(b_info)
    BASIC['기본정보'] = data
    dest = dict(BASIC)

    # 시설 및 서비스정보
    GO_OPTION={}
    go_option = soup.find('article', id='go_option')
    option = go_option.select('div > ul > li')
    k_item=[]
    c_item=[]
    options=[]
    facility_service_info={}
    for item in option:
        info = item.find_all('span',class_='heading')[0].string
        if(info == '공용옵션'):
            opt_h = go_option.find('ul', class_='option_wrap')
            opt_k = go_option.find('li', class_='kitchen_item')
            child = opt_k.ul.findChildren()
            c = opt_h.find_all('span')
            for span in c:
                if span in child:
                    k_item.append(span.text)
                else:
                    c_item.append(span.text)
            facility_service_info['공용옵션'] = c_item
            facility_service_info['주방시설'] = k_item
            k_item=[]
            c_item=[]
        else :
            contents = item.find_all('li')[0].string
            facility_service_info[info]=contents
    GO_OPTION['시설 및 서비스정보'] = facility_service_info
    dest.update(GO_OPTION)
    facility_service_info={}

    #빈 방 정보
    con_A=[]
    ROOM={}
    room_val=[]
    room_con_info={}
    roominfo = soup.find('section',id='go_roomInfo').find('div',class_='table')
    room_box = roominfo.find_all('li', class_='tr room_box_item')
    for item in room_box:
        r_opt_val=[]
        room_name = item.find('li').string  #호수
        room_con_info['room_name']=room_name

        room_content = item.find('ul',class_='more_show').find_all('span', class_='heading')
        for item in room_content:
            room_con_title = item.string
            if item.string == '방 옵션':
                r_opt = item.parent.ul.find_all('span')
                for item in r_opt:
                    item = item.string
                    r_opt_val.append(item)
                con_val = r_opt_val
            else :
                con_val = item.parent.ul.li.text
                if re.findall('^\d\.?', con_val):
                    con_val = ''.join(re.findall('^\d\.?\d?\d?', con_val))
            room_con_info[room_con_title] = con_val
            r_opt_val = []
        room_val.append(dict(room_con_info))
    ROOM['빈 방 정보'] = room_val
    dest.update(ROOM)
    room_val=[]

    with open('Gosiwon_json{}.json'.format(num), 'a', encoding="utf-8") as make_file:
                  json.dump(dest,make_file,ensure_ascii=False, indent='\t')
