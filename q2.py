from datetime import datetime
import numpy as np
from sklearn import model_selection, neighbors
import pandas as pd

df = pd.read_json('data.json')
df.fillna(-99999, inplace=True)

# 1300 days is used rahter than 30 otherwise the active users will be 0 because the data is for 2014. With 1300 +-50% of users are active
retained = [True if (datetime.now() - datetime.strptime(last_chat_date, '%Y-%m-%d')).days <= 1300 else False for last_chat_date in df['last_chat_date']]        

#note: avg_chat_numbers AND chats_in_fist_30_days spelling in PDF file is wrong
X = np.array(df.drop(['last_chat_date', 'signup_date', 'phone', 'city'], 1))
y = np.array(retained)

X_train, X_test, y_train, y_test = model_selection.train_test_split(X, y, test_size=0.2)

clf = neighbors.KNeighborsClassifier()
clf.fit(X_train, y_train)

accuracy = clf.score(X_test, y_test)
print('{0}%'.format(accuracy * 100))

# Columns: 'avg_chat_numbers' 'avg_rating_of_app' 'avg_rating_of_attendee' 'chats_in_fist_30_days' 'premium_app_user'
predict_example_user = np.array([0, 2, 1, 1, True])
predict_example_user = predict_example_user.reshape(1, -1)

prediction = clf.predict(predict_example_user)
print(prediction)