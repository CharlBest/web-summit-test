import json
from datetime import datetime

# I deliberately didn't use Pandas to show how to work with the plain json file reader
# Pandas is used in question 2

with open('data.json') as file:
    data = json.load(file)

total_users = len(data['last_chat_date'])
count = 0
for user_id, last_chat_date in data['last_chat_date'].items():
    last_active_date_diff = datetime.now() - datetime.strptime(last_chat_date, '%Y-%m-%d')

    # 1300 days is used rahter than 30 otherwise the active users will be 0 because the data is for 2014. With 1300 +-50% of users are active
    if last_active_date_diff.days <= 1300:
        count += 1

print(count / total_users * 100)