from user import user

class dialogue :
    def __init__(self, user):
        self.currentHandler = None
        self.nextQuestion = ""
        self.user = user

    def getReply(self, message):
        if self.currentHandler == None:
            return {"channel": self.user.channel_id,
                "username": "librarian",
                "text": "Quit."}
        else:
            # so each handler return an dictionary which can be used right away with web_client.chat_postmessage
            return self.currentHandler(message)

    def changeHandlerAndQuestion(self, handler, question):
        self.currentHandler = handler
        self.nextQuestion = question

    def haveEmptyHandler(self):
        if self.currentHandler == None:
            return True
        else:
            return False