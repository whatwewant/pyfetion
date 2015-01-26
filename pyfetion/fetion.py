#!/usr/bin/env python
# coding=utf-8

import re
import json
try:
    import requests
except :
    pass

class Fetion:
    LOGIN_URL = r'http://f.10086.cn/huc/user/foo/login.do'
    SELFINFO_URL = r'http://f.10086.cn/im5/user/selfInfo.action'
    SEARCH_FRIEND_INFO_URL = r'http://f.10086.cn/im5/user/searchFriendByPhone.action'
    SHORTMESSAGE_URL = r'http://f.10086.cn/im5/chat/sendNewGroupShortMsg.action'
    LOGOUT_URL = r'http://f.10086.cn/im5/login/login.action?type=logout'
    GROUP_CONTACTS = r'http://f.10086.cn/im5/index/loadGroupContactsAjax.action'
    ONE_GROUP_CONTACTS = r'http://f.10086.cn/im5/index/contactlistView.action?idContactList={id_contact_list}'

    def __init__(self, account=None, password=None):
        self.__account = account
        self.__password = password
        self.__session = requests.Session()

    def login(self, account=None, password=None):
        if account and password:
            self.__account = account
            self.__password = password
        data = {
            'mobilenum': self.__account,
            'password': self.__password,
            'm': 'submit',
            'backurl': 'http://f.10086.cn/',
            'fr': 'foo',
        }

        self.__session.post(Fetion.LOGIN_URL, data=data)
        # We have to go to this page to finish login,
        # otherwise it will be redirected when we go to other pages.
        return self.__session.get(Fetion.SELFINFO_URL)

    def get_user_id(self, tel):
        if tel == self.__account:
            result = self.__session.get(Fetion.SELFINFO_URL)
            user_id =re.findall(r"var idUser = '([0-9]+)';", result.content)
            if len(user_id) != 1:
                return '-1' # -1 stand fo not getting user_id
            return str(user_id[0])
        else:
            data = {
                'number': tel
            }
            result = self.__session.post(Fetion.SEARCH_FRIEND_INFO_URL,
                                         data=data)
        
            userinfo = result.json().get(u'userinfo', u'-2')
            idUser = userinfo.get(u'idUser', u'-2')
            if userinfo == u'-2' or idUser == u'-2':
                return '-1'
            return str(idUser)

    def send(self, to_tel, msg):
        touserid = []
        if not isinstance(to_tel, list):
            if not re.match(r'\+{0,1}[0-9]{11,128}$', to_tel):
                touserid = '-1'
            touserid = self.get_user_id(str(to_tel))
        else:
            for ttl in list(set(to_tel)):
                if not re.match(r'\+{0,1}[0-9]{11,128}$', ttl):
                    continue
                touserid.append(self.get_user_id(str(ttl)))
            touserid = list(set(touserid))
            try:
                touserid = touserid.remove('-1')
            except :
                pass
            # print('touserid: ', str(touserid))
            touserid = ','.join(touserid)

        msgdata = {
            'msg': msg,
            'touserid': touserid
        }
        req = self.__session.post(Fetion.SHORTMESSAGE_URL, 
                                   data=msgdata)
        return req.json()

    def logout(self):
        return self.__session.get(Fetion.LOGOUT_URL)

    def get_group_contacts_ids(self):
        # only get not null group
        result = self.__session.get(Fetion.GROUP_CONTACTS)
        jsonData = result.json()
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
        result = self.__session.get(Fetion.ONE_GROUP_CONTACTS\
                        .format(id_contact_list=id_contact_list))
        jsonData = result.json()
        contacts = jsonData.get('contacts')
        detail = []
        simple = []
        for each in contacts:
            detail.append((each.get('localName'), each.get('idContact')))
            simple.append(each.get('idContact'))

        return {'user_ids': simple, 'detail': detail}

    def get_group_id_by_name(self, name):
        all_groups = self.get_group_contacts_ids()
        if all_groups == {}:
            print('Error: Cannot Get Groups Infomation.')
            return 
        return all_groups.get(name.decode('utf-8'), -1)

    def send_fetion_group(self, group_name, msg):
        id_contact_list = self.get_group_id_by_name(group_name)
        if id_contact_list == -1:
            return {u'info': u'组不存在或者组为空', u'sendCode': u'400'}
        user_ids = self.get_one_group_contacts(id_contact_list)
        touserid = ','.join(user_ids)
        msgdata = {
            'msg': msg,
            'touserid': touserid
        }
        req = self.__session.post(Fetion.SHORTMESSAGE_URL, 
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
            sendMessage('13011111111', 'fetion password',
                        '13011111112', 'test message')
    '''
    oo = Fetion(account, password)
    oo.login()
    sendStatus = oo.send(to_tel, msg)
    oo.logout()
    return sendStatus

def sendFetionGroupMessage(account, password, group_name, msg):
    pass
