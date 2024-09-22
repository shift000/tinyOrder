

class Postbox:
	def __init__(self):
		self.box = []
    def add(self, msg):
        self.box.append(msg)
    def get_post(self):
        if self.box:
            return self.box.pop()
        