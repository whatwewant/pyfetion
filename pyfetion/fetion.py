#!/usr/bin/env python
# coding=utf-8

import re
import json
import time
try:
    import requests
    from bs4 import BeautifulSoup
except :
    pass

def getTime():
    return str(int(time.time() * 1000))

class Fetion:
    LOGIN_URL = r'http://f.10086.cn/huc/user/space/login.do?m=submit&fr=space'

    SELFINFO_URL = r'http://f.10086.cn/im5/user/selfInfo.action?t={milisec}'

    # SEARCH_FRIEND_INFO_URL = r'http://f.10086.cn/im5/user/searchFriendByPhone.action?t={milisec}'
    SEARCH_FRIEND_INFO_URL = r'http://f.10086.cn/im5/index/searchFriendsByQueryKey.action'

    SHORTMESSAGE_URL = r'http://f.10086.cn/im5/chat/sendNewGroupShortMsg.action?t={milisec}'

    LOGOUT_URL = r'http://f.10086.cn/im5/login/login.action?type=logout'

    GROUP_CONTACTS = r'http://f.10086.cn/im5/index/loadGroupContactsAjax.action?fromUrl=&t={milisec1}&_={milisec2}'

    ONE_GROUP_CONTACTS = r'http://f.10086.cn/im5/index/contactlistView.action?idContactList={id_contact_list}&fromUrl=&t={milisec1}&_={milisec2}'

    ALLLIST_ACTION = r'http://f.10086.cn/im5/box/alllist.action?t={milisec}'

    ADD_FRIEND_SUBMIT = r'http://f.10086.cn/im5/user/addFriendSubmit.action?t={milisec}'
    # ADD_FRIEND_SUBMIT = r'http://f.10086.cn/im5/user/searchFriendByPhone.action?t={milisec}'

    def __init__(self, account=None, password=None):
        self.__account = account
        self.__password = password
        self.__session = requests.Session()

        self.__session.headers['Origin'] = 'http://f.10086.cn'
        self.__session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.__session.headers['HOST'] = 'f.10086.cn'
        self.__session.headers['User-Agent'] = 'Mozilla/5.0 (iPad; CPU OS 4_3_5 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8L1 Safari/6533.18.5'
        self.__session.headers['Accept-Language'] = 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4'
        self.__session.headers['Content-Type'] = 'application/x-www-form-urlencoded;charset=UTF-8'


        self.__leave_now = False

    def set_leave_now(self):
        if self.__leave_now == False:
            self.__leave_now = True

    def do_heart_beat(self):
        self.__session.headers['Referer'] = 'http://f.10086.cn/im5/login/login.action?mnative=0&t=%s' % getTime()
        # self.__session.post(Fetion.ALLLIST_ACTION.format(milisec=getTime()))
        return 

    def leave_now(self, return_type):
        if self.__leave_now:
            return return_type

    def login(self, account=None, password=None):
        if account and password:
            self.__account = account
            self.__password = password

        data = {
            'mobilenum': self.__account,
            'password': self.__password,
            'm': 'submit',
            'backurl': 'http://f.10086.cn/',
            'fr': 'space',
        }

        self.__session.get(Fetion.LOGIN_URL)

        self.__session.post(Fetion.LOGIN_URL, data=data)
        # We have to go to this page to finish login,
        # otherwise it will be redirected when we go to other pages.
        return self.__session.post(Fetion.SELFINFO_URL.format(milisec=getTime()))

    def get_user_id(self, tel):
        if self.__leave_now == True:
            return '-1'

        # heart beat
        self.do_heart_beat()

        if tel == self.__account:
            result = self.__session.post(Fetion.SELFINFO_URL.format(milisec=getTime()))
            try:
                return str(result.json().get('userinfo').get('idUser', '-1'))
            except:
                self.__leave_now = True
                return '-1'
        else:
            data = {
               'number': tel
            }
            # data = {
            #    'queryKey': tel
            # }
            result = self.__session.post(Fetion.SEARCH_FRIEND_INFO_URL,
            #                            .format(milisec=getTime()),
                                         data=data)
        
            try:
                # userinfo = result.json().get(u'userinfo', u'-2')
                userinfo = result.json().get(u'contacts', u'-2')[0]
            except ValueError:
                self.set_leave_now()
                return '-2'

            idUser = userinfo.get(u'idContact', u'-2')
            # idUser = userinfo.get(u'idUser', u'-2')
            if userinfo == u'-2' or idUser == u'-2':
                self.__leave_now = True
                return '-1'
            return str(idUser)

    def send(self, to_tel, msg):
        # heart beat
        self.do_heart_beat()

        touserid = []
        if not isinstance(to_tel, list):
            to_tel = str(to_tel)
            if not re.match(r'\+{0,1}[0-9]{11,128}$', to_tel):
                touserid = '-1'
                return {u'info': u'接收手机不合法', u'sendCode': u'400'}
            # print('Totel: ', to_tel)
            # print('Totle : ', isinstance(to_tel, list))
            touserid = self.get_user_id(to_tel)
        else:
            for ttl in list(set(to_tel)):
                ttl = str(ttl)
                if not re.match(r'\+{0,1}[0-9]{11,128}$', ttl):
                    continue
                touserid.append(self.get_user_id(ttl))
            touserid = list(set(touserid))
            try:
                touserid = touserid.remove('-1')
            except :
                pass
            # print('touserid: ', str(touserid))
            touserid = ','.join(touserid)

        if touserid == '-1':
            return {u'info': u'用户名或密码不正确', u'sendCode': u'400'}
        elif touserid == '-2':
            return {u'info': u'ta还不是你的好友,请先加ta为好友!', u'sendCode': u'404'}

        msgdata = {
            'msg': msg,
            'touserid': ',' + touserid
        }
        req = self.__session.post(Fetion.SHORTMESSAGE_URL\
                        .format(milisec=getTime()), 
                                data=msgdata)

        return req.json()

    def logout(self):
        # heart beat
        self.do_heart_beat()

        return self.__session.get(Fetion.LOGOUT_URL)

    def get_group_contacts_ids(self):
        # only get not null group
        if self.__leave_now == True:
            return {}

        # heart beat
        self.do_heart_beat()

        tt = getTime()

        result = self.__session.get(Fetion.GROUP_CONTACTS\
                                    .format(milisec1=tt, milisec2=tt))
        try:
            jsonData = result.json()
        except ValueError:
            # print('Error: 用户名或密码不正确!')
            self.set_leave_now()
            return {}
        total_groups = jsonData.get('contacts')
        # cleared_groups = []
        friendGroupIds = {}
        for each in total_groups:
            if each.get(u'contactTotal', 0) != 0:
                # cleared_groups.append(each)
                friendGroupIds[each.get(u'contactListName')] =\
                        each.get(u'idContactList')
        return friendGroupIds

    def get_one_group_contacts(self, id_contact_list):
        if self.__leave_now:
            return {'user_ids': [], 'detail': []}

        # heart beat
        self.do_heart_beat()

        tt = getTime()
        result = self.__session.get(Fetion.ONE_GROUP_CONTACTS\
                        .format(id_contact_list=id_contact_list, 
                                milisec1=tt, 
                                milisec2=tt))
        try:
            jsonData = result.json()
        except ValueError:
            # print('Error: 用户名或密码不正确!')
            self.set_leave_now()
            return {'user_ids': [], 'detail': []}
        contacts = jsonData.get('contacts')
        detail = []
        simple = []
        for each in contacts:
            detail.append((each.get('localName'), 
                           str(each.get('idContact'))))
            simple.append(str(each.get('idContact')))

        return {'user_ids': simple, 'detail': detail}

    def get_group_id_by_name(self, name):
        if self.__leave_now:
            return -1

        # heart beat
        self.do_heart_beat()

        all_groups = self.get_group_contacts_ids()
        if self.__leave_now:
            return -1

        if all_groups == {}:
            # print('Error: Cannot Get Groups Infomation.')
            self.set_leave_now()
            return -1
        return all_groups.get(name.decode('utf-8'), -1)

    def send_all_fetion_group(self, msg):
        friendGroupIds = self.get_group_contacts_ids()
        status = []
        for name in friendGroupIds:
            status.append(self.send_fetion_group(name, msg))
        return status

    def send_fetion_group(self, group_name, msg):
        # heart beat
        self.do_heart_beat()

        if self.__leave_now:
            return {u'info': u'用户名或密码不正确', u'sendCode': u'400'}

        id_contact_list = self.get_group_id_by_name(group_name)
        if self.__leave_now:
            return {u'info': u'用户名或密码不正确,'+
                    u'或者飞信群组不存在或未空', u'sendCode': u'400'}

        if id_contact_list == -1:
            return {u'info': u'组不存在或者组为空', u'sendCode': u'400'}

        user_ids = self.get_one_group_contacts(id_contact_list)\
                            .get('user_ids')
        touserid = ','.join(user_ids)
        msgdata = {
            'msg': msg,
            'touserid': touserid
        }
        req = self.__session.post(Fetion.SHORTMESSAGE_URL\
                                  .format(milisec=getTime()), 
                                   data=msgdata)
        return req.json()

    def send_fetion_groups(self, group_names, msg):
        '''
            group_names is list object
        '''
        if not group_names:
            return {u'info': u'分组不能为空!', u'sendCode': u'400'}

        info = ''
        for each in group_names:
            status = self.send_fetion_group(each, msg)
            info_tmp = 'succeeded' if status['sendCode'] == u'200' else 'failed' 
            info += (str(each) + info_tmp + '#')
        return {u'info': info, u'sendCode': u'200'}

    def add_friend(self, to_tel):
        if self.__leave_now == True:
            return {u'info': u'用户名或密码不正确', u'sendCode': u'400'}

        # heart beat
        self.do_heart_beat()

        data = {
            'number': str(to_tel),
            'type': '0'
        }

        resp = self.__session.post(Fetion.ADD_FRIEND_SUBMIT\
                                   .format(milisec=getTime()), data=data)

        try:
            info = resp.json().get('tip')
            info = info if info != u"" else u''
            return {u'info': info, u'sendCode': u'200'}
        except:
            return {u'info': u'用户名或密码不正确, 或用户不存在', u'sendCode': u'400'}

def get_weather_fetion(city):
    url = r'http://f.10086.cn/weather/sch.do?code=%s' % city
    headers={'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/600.1.3 (KHTML, like Gecko) Version/8.0 Mobile/12A4345d Safari/600.1.4', 'Host': 'f.10086.cn'}
    resp = requests.get(url, headers=headers)
    respB = BeautifulSoup(resp.content)
    
    today = respB.find(name='dl', attrs={'class', 'info'}).text
    future = respB.find(name='ul', attrs={'id': 'future'})
    tomorrow = future.findAll(name='li')[0].text
    thedayaftertomorrow = future.findAll(name='li')[1].text
    return u'%s 天气:\n' % city + \
            today + '\n\n' + \
            tomorrow + '\n'
        
def sendMessage(account, password, to_tel, msg):
    '''
        Situations:
            1. send a message
            2. send a group message (more than people)
        Usage:
            sendMessage(fetionAccount, fetionPassword, 
                        receiver_phone, message_content)
        For example:
            send message someone:
                sendMessage('13011111111', 'fetion password',
                        '13011111112', 'test message')

            send message to more than one people:
                sendMessage('13011111111', 'fetion password',
                        ['13011111112', '13011111113', '13011111114'],
                        'test message')

    '''
    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.send(to_tel, msg)
    oo.logout()
    return sendStatus

def sendFetionGroupMessage(account, password, group_name, msg):
    '''
        Description:
            Send Message According to Fetion Group:
        Usage:
            sendFetionGroupMessage(fetionAccount, fetionPassword,
                        fetionGroupName, messageContent)
        Take Care:
            1. Make sure fetionAccount and fetionPassword Correct
            2. Make sure fetionGroupName exist 
            3. Make sure fetionGroupName must be not Empty. 
        For example:
            sendFetionGroupMessage('13011111111', 'fetionPassword',
                                '同学', '大家还好吗?有空聚一聚')

    '''

    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.send_fetion_group(group_name, msg)
    oo.logout()
    return sendStatus

def sendFetionGroupsMessage(account, password, group_names, msg):
    '''
        Description:
            Send Message According to Fetion Group:
        Usage:
            sendFetionGroupMessage(fetionAccount, fetionPassword,
                        fetionGroupsName, messageContent)
        Take Care:
            1. Make sure fetionAccount and fetionPassword Correct
            2. Make sure fetionGroupsName exist 
            3. Make sure fetionGroupsName must be not Empty. 
            4. Make sure fetionGroupsName must be a list
        For example:
            sendFetionGroupMessage('13011111111', 'fetionPassword',
                                ['同学'], '大家还好吗?有空聚一聚')

    '''

    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.send_fetion_groups(group_names, msg)
    oo.logout()
    return sendStatus

def addFetionFriend(account, password, receiver_phone):
    '''
        Description:
            Send Message According to Fetion Group:
        Usage:
            sendFetionGroupMessage(fetionAccount, fetionPassword,
                        fetionGroupName, messageContent)
        Take Care:
            1. Make sure fetionAccount and fetionPassword Correct
            2. Make sure fetionGroupName exist 
            3. Make sure fetionGroupName must be not Empty. 
        For example:
            sendFetionGroupMessage('13011111111', 'fetionPassword',
                                '同学', '大家还好吗?有空聚一聚')

    '''

    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.add_friend(receiver_phone)
    oo.logout()
    return sendStatus

def sendWeather(fuser, fpass, rec, city_name):
    sendMessage(fuser, fpass, rec, 
                   get_weather_fetion(city_name))

def sendGroupWeather(fuser, fpass, group_name, city_name):
    sendFetionGroupMessage(fuser, fpass, group_name, 
                   get_weather_fetion(city_name))

def sendFetionAllGroupsMessage(account, password, msg):
    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.send_all_fetion_group(msg)
    oo.logout()
    return sendStatus

