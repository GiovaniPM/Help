# Python3 code to demonstrate  
# to extract words from string  
# using split() 
  
# initializing string   
test_string = "Geeksforgeeks,    is best @# Computer Science Portal.!!!"
  
# printing original string 
print ("The original string is : " +  test_string) 

# using split() 
# to count words in string 
qtd = len(test_string.split())   

# using split() 
# to extract words from string 
res = test_string.split() 
  
# Sorting the words 
words = res
words.sort() 

# printing result 
print ("Quantity of words:" + str(qtd))
print ("The list of words is : " +  str(res)) 
print ("This is the third word : " +  str(res[2])) 
print ("Ordered : " +  str(words))