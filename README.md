PyFetion
===================================

This python module is used to send short message.<br />

Now it only support sending messages by Fetion.<br />
So you can only send to yourself or your friends in Fetion.<br />

### In order to use the module, you need to import message_factory.py.
> Use message_factory.MessageFactory.create_message(class type, your phone number, password) to create a message sender.<br />
> 
> The class type should be one of 'short fetion' or 'long fetion'.<br />
> * 'short fetion' means that you will login only when you send a message and logout immediately.<br />
> * 'long fetion' means that you will login when the message sender constructed and logout only when destroyed.<br />
> 
> So, you'd better use 'long fetion' when you want to send several messages at a time. And don't forget to del it after sending, otherwise it may affect your normal use of fetion.<br />

### After constructed, you can use the send(message, receiver's phone number) method of the object to send message.
The receiver's phone number can be a string or an array of strings.<br />
If receiver's phone number is none, the message will be send to yourself.<br />

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
