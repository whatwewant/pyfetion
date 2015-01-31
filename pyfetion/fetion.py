#!/usr/bin/env python
# coding=utf-8

import re
import json
import time
try:
    import requests
except :
    pass

def getTime():
    return str(int(time.time() * 1000))

class Fetion:
    LOGIN_URL = r'http://f.10086.cn/huc/user/space/login.do?m=submit&fr=space'

    SELFINFO_URL = r'http://f.10086.cn/im5/user/selfInfo.action?t={milisec}'

    SEARCH_FRIEND_INFO_URL = r'http://f.10086.cn/im5/user/searchFriendByPhone.action'

    SHORTMESSAGE_URL = r'http://f.10086.cn/im5/chat/sendNewGroupShortMsg.action?t={milisec}'

    LOGOUT_URL = r'http://f.10086.cn/im5/login/login.action?type=logout'

    GROUP_CONTACTS = r'http://f.10086.cn/im5/index/loadGroupContactsAjax.action?fromUrl=&t={milisec1}&_={milisec2}'

    ONE_GROUP_CONTACTS = r'http://f.10086.cn/im5/index/contactlistView.action?idContactList={id_contact_list}&fromUrl=&t={milisec1}&_={milisec2}'

    ALLLIST_ACTION = r'http://f.10086.cn/im5/box/alllist.action?t={milisec}'

    def __init__(self, account=None, password=None):
        self.__account = account
        self.__password = password
        self.__session = requests.Session()

        self.__session.headers['Origin'] = 'http://f.10086.cn'
        self.__session.headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        self.__session.headers['HOST'] = 'f.10086.cn'
        self.__session.headers['User-Agent'] = 'Mozilla/5.0 (iPad; CPU OS 4_3_5 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8L1 Safari/6533.18.5'


        self.__leave_now = False

    def set_leave_now(self):
        if self.__leave_now == False:
            self.__leave_now = True

    def do_heart_beat(self):
        self.__session.post(Fetion.ALLLIST_ACTION.format(milisec=getTime()))

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
        # heart beat
        self.do_heart_beat()

        if tel == self.__account:
            result = self.__session.post(Fetion.SELFINFO_URL.format(milisec=getTime()))
            return str(result.json().get('userinfo').get('idUser', '-1'))
        else:
            data = {
                'number': tel
            }
            result = self.__session.post(Fetion.SEARCH_FRIEND_INFO_URL,
                                         data=data)
        
            try:
                userinfo = result.json().get(u'userinfo', u'-2')
            except ValueError:
                return '-1'
            idUser = userinfo.get(u'idUser', u'-2')
            if userinfo == u'-2' or idUser == u'-2':
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

        msgdata = {
            'msg': msg,
            'touserid': ',' + touserid
        }
        req = self.__session.post(Fetion.SHORTMESSAGE_URL.format(milisec=getTime()), 
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

        result = self.__session.get(Fetion.GROUP_CONTACTS.format(milisec1=tt, milisec2=tt))
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
        req = self.__session.post(Fetion.SHORTMESSAGE_URL.format(milisec=getTime()), 
                                   data=msgdata)
        return req.json()

        
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
