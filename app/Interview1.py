import time

class API(object):
	"""docstring for API"""
	def __init__(self, timeRecord):
		super(API, self).__init__()
		self.timeRecord = timeRecord

	def getRelevantCount(self, timeTuple):

		theArray = timeTuple[0]

		count = 0
		i = len(theArray) - 1
		while i != 0:

			if(time.time() - theArray[i] <= 2):
				count += 1
				print(count)
				if(count > 5):
					raise Exception("Too many requests", customer)

			i -= 1
		
		return timeTuple[1]

	def execute_endpoint(self, customer):

		try: 
			self.timeRecord[customer][0].append(time.time())

		except:
			self.timeRecord[customer] = ([time.time()], 1)

		self.getRelevantCount(self.timeRecord[customer])
		
		return customer


overallAPI = API({})

customer = "John"

for i in range(8):
	print(overallAPI.execute_endpoint(customer))
	time.sleep(.2)
		