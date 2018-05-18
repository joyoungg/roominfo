#쉐어하우스
# -*- coding: utf-8 -*-
import sys
import io
import re
sys.stdout = io.TextIOWrapper(sys.stdout.detach(), encoding = 'utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.detach(), encoding = 'utf-8')

from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import os

# url = 'http://roomnspace.co.kr/sharehouse/info/5'
# html = urlopen(url).read()
# soup = BeautifulSoup(html, 'html.parser')

for num in range(3,4):
    c_url = 'http://roomnspace.co.kr/sharehouse/info/{}'.format(num)
    html = urlopen(c_url).read()
    soup = BeautifulSoup(html, 'html.parser')

    summary = soup.select_one('div.detail_container.sh > section.detail_content > aside')
    category = summary.find('span', class_='category').text
    name = summary.find('span').text
    tel = ''.join( re.findall('\d+', summary.find('li',class_='tel').find('span').text))
    summary.find('li',class_='tel').find('span').text
    rent =''.join( re.findall('\d+\~\d+', summary.find('li',class_='rent').text))
    deposit =''.join( re.findall('\d+\~\d+', summary.find('li',class_='deposit').text))
    room_yn = summary.find('li',class_='room_yn').text
    addr = summary.find('span',class_='addr').text
    data = {
        'category': category,
        'name' : name,
        'tel' : tel,
        'rent' : rent,
        'deposit' : deposit,
        'room_yn': room_yn,
        'addr' : addr
    }


    #기본정보
    basicInfo = soup.find('article', id='go_basicInfo').select('div > ul > li')
    basic={}
    BASIC={}
    for item in basicInfo:
        info = item.find('span', class_='heading').string
        content = item.ul.li
        if content:
            content = (item.find_all('li'))[0].parent.text.replace('\n', '').replace('\r', '')
            print(content)
            print(1)
            if re.findall('^\d',content) and len(content) <= 5:
                content = ''.join( re.findall('\d+', content))
        else :
            content = ''
        basic[info] = content
    data.update(basic)
    BASIC['기본정보'] = data
    dest = dict(BASIC)


    #입주조건 및 절차
    MOVE_IN={}
    move_in_data={}
    move_in_process={}
    move_in = soup.find('article', class_='process').select('div > ul > li')
    for item in move_in:
        if item.span.string == '입주조건':
            move_condition = item.span.string
            condition = item.ul.find_all('span',class_='heading')
            for item in condition:
                title = item.string
                content = item.parent.ul.li.text.replace('\r',' ')
                move_in_process[title] = content
            move_in_data[move_condition] = move_in_process
        else:
            move_condition = item.find('span',class_='heading').string
            move_condition_val = item.find('li',class_='txt').text.replace('\r',' ')
            move_in_data[move_condition] = move_condition_val
    MOVE_IN['입주조건 및 절차'] = move_in_data
    dest.update(MOVE_IN)
    move_in_data={}


    # result['입주조건 및 절차'] = move_in_data
    # DATA.append(result)

    # 시설 및 서비스정보
    GO_OPTION={}
    go_option = soup.find('article', id='go_option')
    option = go_option.select('div > ul')
    k_item=[]
    c_item=[]
    r_item=[]
    facility_service_info={}
    for item in option:
        info = item.find_all('li',class_='mg_b')
        for li in info:
            container = li.find('span', class_='heading').string
            if li.find('span', class_='heading').string == '공용옵션':
                container = li.find('span', class_='heading').parent
                opt_h = container.find('ul',class_='option_wrap').find_all('li', class_='item')
                opt_k = container.find('li', class_='kitchen_item')
                k_data = opt_k.find_all('li', class_='item')
                for item in opt_h:
                    if item in k_data and item.span:
                        item = item.text
                        k_item.append(item.replace('\n',' '))
                        #go_option > div > ul > li:nth-child(3) > ul > li:nth-child(1) > del
                    else:
                        if item == container.find('ul',class_='option_wrap').find('li', class_='item'):
                            if item.select('del') :
                                item = item.find('ul').text
                                c_item.append(item.replace('\n',' '))
                            else :
                                item = item.text
                                c_item.append(item.replace('\n',' '))
                        else :
                            if item.span:
                                item = item.text
                                c_item.append(item.replace('\n',' '))
                facility_service_info['공용옵션'] = c_item
                facility_service_info['주방시설'] = k_item
                k_item=[]
                c_item=[]

            #방 옵션
            elif li.find('span', class_='heading').string == None:
                container = li.find('span', class_='heading').text
                room = li.find('ul',class_='option_wrap').find_all('span')
                for item in room:
                    r_item.append(item.text)
                facility_service_info[container] = r_item
                r_item=[]

            else:
                container = li.find('span', class_='heading').string
                item = li.find('li').string
                facility_service_info[container] = item
    GO_OPTION['시설 및 서비스정보'] = facility_service_info
    dest.update(GO_OPTION)
    facility_service_info={}


    #관리 및 서비스 정보
    manage_service_info = {}
    SERVICE_INFO={}
    service = soup.find('article', class_='service_info')
    if service :
        service = service.select('div > ul > li')
        for item in service:
            info = item.find_all('span',class_='heading')[0].string
            content = (item.find_all('li'))[0].parent.text.replace('\r',' ')
            manage_service_info[info] = content
        SERVICE_INFO['관리 및 서비스 정보'] = manage_service_info
        dest.update(SERVICE_INFO)
        manage_service_info = {}


    #방 정보
    roominfo = soup.find('section',id='go_roomInfo').find('div',class_='table')
    box_A=[]
    box_r=[]
    room_box = roominfo.find_all('li', class_='room_box')

    for item in room_box:
        room_name = item.find_all('li')[0].string
        room_rent_fee = ''.join( re.findall('\d+', item.find_all('li')[1].string))
        room_deposit = ''.join( re.findall('\d+', item.find_all('li')[2].string))
        room_type = ''.join( re.findall('\d+', item.find_all('li')[3].string))
        room_available = item.find_all('li')[4].text
        box_A = {
            'roon_name' : room_name,
            'room_rent_fee' : room_rent_fee,
            'room_type' : room_type,
            'room_deposit' : room_deposit,
            'room_available' : room_available
        }
        box_r.append(box_A)
    con_A=[]
    con_r=[]
    r_opt_val=[]
    room_con_info={}
    room_con = roominfo.find_all('li', class_='sh_roomContent')
    for item in room_con:
        room_con_h = item.find_all('span',class_='heading')
        for item in room_con_h:
            con_title = item.string
            if con_title == '방 옵션':
                r_opt = item.parent.ul.find_all('span')
                for item in r_opt:
                    item = item.string
                    r_opt_val.append(item)
                con_val = r_opt_val
            elif con_title == '방 설명':
                con_val = item.parent.ul.li.string
            else :
                con_val = item.parent.ul.li.string
                if con_val == None or re.findall('^1/n', con_val) :
                    con_val = ''
                elif re.findall('^\d', con_val):
                    con_val = item.parent.ul.li.string.split(',')
                    if len(con_val) > 1:
                        con_val = ''.join( re.findall('^\d+', con_val[0]+con_val[1]))
                # else :
                #     con_val = item.parent.ul.li.string
                #     print(con_val)
            room_con_info[con_title]= con_val
            r_opt_val = []
        con_r.append(room_con_info)
        room_con_info={}
    ROOM={}
    room_data=[]
    for n in range(len(room_box)):
        box_r[n].update(con_r[n])
        room_data.append(box_r[n])

    ROOM['방 정보'] = room_data
    dest.update(ROOM)
    room_data={}

    #위치 및 교통정보
    LOCATION_TRAFFIC={}
    location_traffic_info = soup.find('article', id='go_loactionInfo').select('div > ul > li')
    location_opt={}
    traffic_opt={}
    location_info_data={}
    traffic_info_data={}

    location = location_traffic_info[0].find('ul')
    for item in location.find_all('span', class_='heading'):
        title = item.string
        content = item.parent.ul.li.string
        location_opt[title] = content
    location_info_data[location.parent.span.string] = location_opt


    traffic = location_traffic_info[1].find('ul')
    for item in traffic.find_all('span', class_='heading'):
        title = item.string
        content = item.parent.ul.li.string
        traffic_opt[title] = content
    traffic_info_data[traffic.parent.span.string]=traffic_opt

    location_info_data.update(traffic_info_data)
    LOCATION_TRAFFIC['위치 및 교통 정보'] = location_info_data
    dest.update(LOCATION_TRAFFIC)
    location_info_data={}

    # print(num)
    # with open('sharehouse_json{}.json'.format(num), 'a', encoding="utf-8") as make_file:
    #     json.dump(dest,make_file,ensure_ascii=False, indent='\t')
