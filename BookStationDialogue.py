from user import user
from Dialogue import dialogue
import re
from coverFinder import CoverFinder

class bookStationDialogue(dialogue):
    def __init__(self, user):
        self.user = user
        self.currentHandler = self.__startHandler
        self.nextQuestion = "Welcome to your book station, <@{}>!"\
                            "How can I help you?\n" \
                            "(1) Add a book to local station\n" \
                            "(2) Display my library\n" \
                            "(3) Update a book progress\n" \
                            "(4) Quit\n".format(user.user_id)
        # just for shorter return
        self.address = {"channel": self.user.channel_id,
                        "username": "librarian"}

    def __startHandler(self, message):
        # change hanlder
        self.currentHandler = self.__greetingHandler
        return {"channel": self.user.channel_id,
                "username": "librarian",
                "text": self.nextQuestion}

    def __greetingHandler(self, message):
        # change handler
        try:
            cmd = int(message)
        except:
            return {"channel": self.user.channel_id,
                "username": "librarian",
                "text": "Sorry, wrong command. Try again!"}
        else:
            # add a book
            if cmd == 1:
                # the order of questions is going to be:
                # "What is the name of the book?"
                # "Is this the book you mentioned?" - use coverFinder
                # "What is the status of the book (Plan to read/ Reading/ Finished) ?
                # if reading: "What is your current page?"
                self.currentHandler = self.__addBook_askName
                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": "What is the name of the book?"}
            elif cmd == 2:
                # if 2 then display the library so no need to change the handler in case they have more commands
                # just write down to make it clear that is does not change
                self.currentHandler = self.__greetingHandler
                bookShelf = self.user.getBookShelf()

                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": bookShelf +
                                "How can I help you?\n" \
                                "(1) Add a book to local station\n" \
                                "(2) Display my library\n" \
                                "(3) Update a book progress\n" \
                                "(4) Quit\n"}
            elif cmd == 3:
                self.currentHandler = self.__updateBook_askName
                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": "What is the name of the book? It might take a few seconds to find it.\n"}
            else:
                # quit
                self.currentHandler = None
                return {**self.address,
                        "text": "Bye. Have a good read!"}

    def __addBook_askName(self, message):
        def __confirm_book(message):
            if re.search(r"[Yy][Ee][Ss]", message):
                self.user.addBook(bookInfo["title"], bookCoverUrl=bookInfo["image_url"], authorName=bookInfo["author_name"])
                # prompt user to input again
                self.currentHandler = self.__greetingHandler
                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": "Add the book successfully.\n" \
                                "How can I help you?\n" \
                                "(1) Add a book to local station\n" \
                                "(2) Display my library\n" \
                                "(3) Update a book progress\n" \
                                "(4) Quit\n"}
            elif re.search(r"[Nn][oO0]", message):
                # ask the book again
                self.currentHandler = self.__addBook_askName
                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": "Sorry I cannot find the book. Is the name correct? Which volume is it?"}
            elif re.search(r"[Qq][Uu][Ii][Tt]", message):
                self.currentHandler = self.__greetingHandler
                return {"channel": self.user.channel_id,
                        "username": "librarian",
                        "text": "Okay choose other options then.\n" \
                                "(1) Add a book to local station\n" \
                                "(2) Display my library\n" \
                                "(3) Update a book progress\n" \
                                "(4) Quit\n"}
            else:
                self.currentHandler = __confirm_book
                return {**self.address,
                        "text": "Please answer either one of [Yes/No/Quit]. No teen code please!"}

        if re.search(r"[Qq]uit", message):
            self.currentHandler = self.__greetingHandler
            return {"channel": self.user.channel_id,
                            "username": "librarian",
                            "text": "Okay choose other options then.\n" \
                                    "(1) Add a book to local station\n" \
                                    "(2) Display my library\n" \
                                    "(3) Update a book progress\n" \
                                    "(4) Quit\n"}
        else:
            self.currentHandler = __confirm_book
            nameOfTheBook = message
            print("The name of the book is: {}\n".format(nameOfTheBook))
            bookInfo = CoverFinder(nameOfTheBook).getBookCoverUrl()
            return {"channel":self.user.channel_id,
                    "username": "librarian",
                    "attachments": [{'pretext': "Is this the book that you mentioned before?",
                                    'color': 'good',
                                    **bookInfo}]
                    }

    def __updateBook_askName(self, message):
        # in case there is two spaces in the name
        if message and re.search(r"[Qq]uit]", message):
            self.currentHandler = self.__greetingHandler
            return {"channel": self.user.channel_id,
                            "username": "librarian",
                            "text": "Okay choose other options then.\n" \
                                    "(1) Add a book to local station\n" \
                                    "(2) Display my library\n" \
                                    "(3) Update a book progress\n" \
                                    "(4) Quit\n"}

        else:
            message = " ".join(message.split(" "))
            bookName = CoverFinder(message).getBookRealName()
            print("The book name I found is: {}\n".format(bookName))
            try:
                book = self.user.book_station[bookName]
            except:
                # does not change 
                self.currentHandler = self.__updateBook_askName
                return {**self.address,
                        "text": "Sorry I can only find the book {} which is not currently in your local book shelf.\n" \
                            "Try typing the name in a different way or add the book to the shelf using (1) beforehand.\n".format(bookName)}
            else:
                def __confirm_book(message):
                    if message and re.search(r"[Yy][Ee][Ss]", message):
                        self.currentHandler = __update_page_progress
                        return {**self.address,
                                'text': 'What is the current page of your book? [Page + `a number`/ Started / Finished]'}
                    elif message and re.search(r"[Nn][Oo]", message):
                        self.currentHandler = __confirm_book
                        return {**self.address,
                                'text': 'Cannot find another book. Can you retype the name?'}
                    elif message and re.search(r"[Qq][Uu][Ii][Tt]", message):
                        self.currentHandler = self.__greetingHandler
                        return {"channel": self.user.channel_id,
                                "username": "librarian",
                                "text": "Okay choose other options then.\n" \
                                        "(1) Add a book to local station\n" \
                                        "(2) Display my library\n" \
                                        "(3) Update a book progress\n" \
                                        "(4) Quit\n"}
                    else:
                        self.currentHandler = __confirm_book
                        return {**self.address,
                                "text": "Please answer either one of [Yes/No/Quit]. No teen code please!"}

                def __update_page_progress(message):
                    print("Book station: {}\n".format(self.user.book_station))
                    if message and re.search(r"[Ss]tart|[Bb]egin", message):
                        self.user.addBook(bookName, status="Start", currentPage=0)
                    elif message and re.search(r"[Ee]nd|[Ff]inish", message):
                        self.user.addBook(bookName, status="Finished", currentPage=9999)
                    elif message and re.search(r"\d+", message):
                        digit = re.search(r"\d+", message)
                        page = int(message[digit.start():digit.end()])
                        self.user.addBook(bookName, status="Reading", currentPage=page)
                    self.currentHandler = self.__greetingHandler
                    return {
                            **self.address,
                            'text': 'Update reading progress successfully.' \
                                    "Okay choose other options.\n" \
                                    "(1) Add a book to local station\n" \
                                    "(2) Display my library\n" \
                                    "(3) Update a book progress\n" \
                                    "(4) Quit\n"
                            }
                self.currentHandler = __confirm_book
                return {**self.address,
                        "attachments": [{'pretext': "Is this the book that you mentioned before?",
                                        'color': 'good',
                                        'image_url': book["bookCoverUrl"],
                                        'title': bookName,
                                        'author': book["authorName"]
                                        }]}

