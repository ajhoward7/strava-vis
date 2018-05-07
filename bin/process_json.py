import json

f = open('all_acts.json')
json_data = f.read()
f.close()

data = json.loads(json_data)

for activity in data:
    print activity["name"]