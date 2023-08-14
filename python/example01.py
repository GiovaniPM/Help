# import required packages
import json

# custom class
class Student:
	def __init__(self, roll_no, name, batch):
		self.roll_no = roll_no
		self.name = name
		self.batch = batch

class Car:
	def __init__(self, brand, name, batch):
		self.brand = brand
		self.name = name
		self.batch = batch

# main function
if __name__ == "__main__":
	
	# create two new student objects
	s1 = Student(85, "Swapnil", "IMT")
	s2 = Student(124, "Akash", "IMT")

	# create two new car objects
	c1 = Car("Mazda","","2006")
	c2 = Car("Honda", "Amaze", "2011")

	# convert to JSON format
	jsonstr1 = json.dumps(s1.__dict__)
	jsonstr2 = json.dumps(s2.__dict__)
	jsonstr3 = json.dumps(c1.__dict__)
	jsonstr4 = json.dumps(c2.__dict__)

	# print created JSON objects
	print(jsonstr1)
	print(jsonstr2)
	print(jsonstr3)
	print(jsonstr4)