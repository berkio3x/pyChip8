class DelayTimer:
	def __init__(self, val=0,):
		self.time = val 

	def countdown(self):
		if self.time > 0:
			self.time -= 1

	def get_time(self):
		return self.time

	def set_time(self, t):
		self.time = t


# class SoundTimer:
# 	def __init__(self, val=0):
# 		self.