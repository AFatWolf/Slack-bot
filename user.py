import datetime

class user:
    def __init__(self, user_id:str):
        self.user_id = user_id
        self.status = "Not working"
        self.working_hour = 0
        # books that are reading 
        self.book_station = {}

    def isWorking(self):
        return (True if self.status == "Working" else False)

    def check_in(self):
        if not self.isWorking():
            self.start = datetime.datetime.now()
            self.end = datetime.datetime.now()
            self.status = "Working"

    def check_out(self):
        if self.isWorking():
            self.end = datetime.datetime.now()
            self.working_hour += (self.end - self.start).total_seconds() / 3600
            self.status = "Not working"

    def get_working_hours(self):
        if self.isWorking():
            current_time = datetime.datetime.now()
            return self.working_hour + (current_time - self.start).total_seconds() / 3600
        else:
            return self.working_hour
            # JUY-817