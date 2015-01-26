PyFetion
===================================

This python module is used to send short message.<br />

Now it only support sending messages by Fetion.<br />
So you can only send to yourself or your friends in Fetion.<br />

### Installation:
    $ pip install pyfetion
    or 
    $ python setup.py install

### Usage:
```python
        Situations:
            1. send a message
            2. send a group message (more than people)

        Import:
            from pyfetion import sendMessage
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
```
