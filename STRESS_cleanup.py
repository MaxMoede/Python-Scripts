import json

# Simple python script to clean up STRESS json file
# by removing unselected projects

IDList = []
counter = 0

fileName = raw_input("Enter full name of STRESS json file: ");

with open(fileName, 'r') as data_file:
   data = json.load(data_file)

for item in data["selectedIds"]:
   IDList.append(item)
   counter = counter + 1

projectCount = 0
for element in data["projects"]:
   projectCount += 1

newcounter = 0
for x in range(0, projectCount):
   if data["projects"][newcounter]["id"] not in IDList:
      del data["projects"][newcounter]
   else:
      newcounter += 1

with open(fileName, 'w') as data_file:
   data = json.dump(data, data_file)


