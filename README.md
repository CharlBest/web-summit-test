# Part 1 - SQL

Given the below subset of Web Summit’s schema, write executable SQL queries to answer
the two questions below. Please answer in a single query and assume read-only access to
the database (i.e. do not use CREATE TABLE).
Assume a PostgreSQL database, server timezone is UTC.

### Table Name: tickets

| Column Name | Datatype |
| ------ | ----------- |
| id | integer |
| user_id | integer (Foreign keyed to users.usersid) |
| conference_id | integer (Foreign keyed to conferences.usersid) |
| bought_date | timestamp with timezone |
| cancelled_date | timestamp with timezone |
| ticket_type | Enum(‘general’,’startup’,’investor’,’media’,’speaker’,’partner’) |
| completed | Boolean |

### Table Name: users

| Column Name | Datatype |
| ------ | ----------- |
| usersid | integer |
| email | character varying |
| country_id | integer |
| previous_attendee | Boolean |
| role | Enum(‘attendee’,’speaker’,’volunteer’) |
| created_at | timestamp with timezone |

1. Between Oct 1, 2014 at 10am PDT and Oct 22, 2015 at 5pm PDT, what percentage
of tickets purchased by returning users were cancelled?
2. For conference_ids 1, 6 and 12, list the top three most popular country_ids by ticket
purchase for each week between June 3, 2015 and June 24, 2015

## Answer
### Setup
```sql
CREATE TYPE user_role AS ENUM ('attendee', 'speaker', 'volunteer');
CREATE TABLE users (
    usersid             INTEGER PRIMARY KEY	NOT NULL,
    email               VARCHAR(100)		NOT NULL,
    country_id          INTEGER,
    previous_attendee   BOOLEAN,
    role                user_role,
    created_at          timestamptz
);

CREATE TYPE ticket_type AS ENUM ('general', 'startup', 'investor', 'media', 'speaker', 'partner');
CREATE TABLE tickets (
    id              INTEGER PRIMARY KEY NOT NULL,
    user_id         INTEGER REFERENCES users,
    conference_id   INTEGER,
    bought_date     timestamptz,
    cancelled_date  timestamptz,
    ticket_type     ticket_type,
    completed       BOOLEAN
);

--Users
INSERT INTO users VALUES (1, 'charlbest@yahoo.com', 1, TRUE, 'attendee', now());
INSERT INTO users VALUES (2, 'charlbest@yahoo.com', 1, FALSE, 'attendee', now());

--Tickets
--Before date out of range tests
INSERT INTO tickets VALUES (1, 1, 1, '2014-08-01 10:00:00'::timestamp AT TIME ZONE 'PST', '2014-09-01 17:00:00'::timestamp AT TIME ZONE 'PST', 'general', TRUE);
INSERT INTO tickets VALUES (2, 1, 1, '2014-09-01 10:00:00'::timestamp AT TIME ZONE 'PST', '2014-12-01 17:00:00'::timestamp AT TIME ZONE 'PST', 'general', TRUE);

--Canceled ticket in time range
INSERT INTO tickets VALUES (3, 1, 1, '2014-12-01 10:00:00'::timestamp AT TIME ZONE 'PST', '2015-08-01 17:00:00'::timestamp AT TIME ZONE 'PST', 'general', TRUE);
--No canceled ticket in time range
INSERT INTO tickets VALUES (4, 1, 1, '2014-12-01 10:00:00'::timestamp AT TIME ZONE 'PST', NULL, 'general', TRUE);

--After date out of range tests
INSERT INTO tickets VALUES (5, 1, 1, '2015-09-01 10:00:00'::timestamp AT TIME ZONE 'PST', '2015-12-01 17:00:00'::timestamp AT TIME ZONE 'PST', 'general', TRUE);
INSERT INTO tickets VALUES (6, 1, 1, '2016-10-01 10:00:00'::timestamp AT TIME ZONE 'PST', '2016-10-01 17:00:00'::timestamp AT TIME ZONE 'PST', 'general', TRUE);
```

## Question 1
### Assumptions
* Default value for previous_attendee is FALSE
* Default value for cancelled_date is NULL
* The time range for the query takes into account the bought_date AND cancelled_date. BOTH have to be within the given time frame (Oct 1, 2014 at 10 am PDT and Oct 22, 2015 at 5pm PDT)

### Permutations

```python
time range             |------|
1               |----|
2                   |----|
3                       |----|
4                           |----|
5                               |----|
```

### Query
```sql
SELECT ceil(((COUNT(tickets.cancelled_date)::decimal / COUNT(*)::decimal) * 100)) as percentage
FROM tickets
INNER JOIN users ON users.usersid = tickets.user_id
WHERE 
      tickets.bought_date > '2014-10-01 10:00:00'::timestamp AT TIME ZONE 'PST'
  AND tickets.bought_date < '2015-10-22 17:00:00'::timestamp AT TIME ZONE 'PST'
  AND 
      --ensure that the cancel date also falls within the query dates
      ((tickets.cancelled_date IS NULL)
      OR (tickets.cancelled_date > '2014-10-01 10:00:00'::timestamp AT TIME ZONE 'PST'
      AND tickets.cancelled_date < '2015-10-22 17:00:00'::timestamp AT TIME ZONE 'PST'))
  AND users.previous_attendee = TRUE
```

## Question 2
### Assumptions
* I didn’t exclude the tickets that was canceled because I assumed that the intent to purchase was still there and thus it contributes to the country’s ranking

### More test data
```sql
--Users
INSERT INTO users VALUES (20, 'test@test.com', 20, FALSE, 'attendee', now());
INSERT INTO users VALUES (30, 'test@test.com', 30, FALSE, 'attendee', now());
INSERT INTO users VALUES (40, 'test@test.com', 40, FALSE, 'attendee', now());
INSERT INTO users VALUES (50, 'test@test.com', 50, FALSE, 'attendee', now());

--Out of range tests
INSERT INTO tickets VALUES (8, 20, 6, '2015-06-02'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (9, 20, 6, '2015-06-25'::timestamp, NULL, 'general', TRUE);

--Valid tickets in date range (week 1)
INSERT INTO tickets VALUES (10, 20, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (11, 20, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (12, 20, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (13, 20, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (14, 30, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (15, 30, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (16, 30, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (17, 40, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (18, 40, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (19, 50, 6, '2015-06-04'::timestamp, NULL, 'general', TRUE);
--Week 2
INSERT INTO tickets VALUES (20, 20, 6, '2015-06-11'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (21, 20, 6, '2015-06-11'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (22, 20, 6, '2015-06-11'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (23, 20, 6, '2015-06-11'::timestamp, NULL, 'general', TRUE);
--Week 3, 4
INSERT INTO tickets VALUES (24, 20, 6, '2015-06-18'::timestamp, NULL, 'general', TRUE);
INSERT INTO tickets VALUES (25, 20, 6, '2015-06-23'::timestamp, NULL, 'general', TRUE);
```

### Query
```sql
SELECT * 
FROM 
(
    SELECT users.country_id,
    COUNT(tickets.bought_date) as total_bought,
    date_part('week', bought_date) as week,
    ROW_NUMBER() OVER (PARTITION BY date_part('week', bought_date) ORDER BY COUNT(tickets.bought_date) DESC) AS rank 
    FROM tickets
    INNER JOIN users ON users.usersid = tickets.user_id
    WHERE tickets.conference_id = ANY('{1, 6, 12}'::INT[])
        AND tickets.bought_date > '2015-06-03'::timestamp
        AND tickets.bought_date < '2015-06-24'::timestamp
    GROUP BY users.country_id, week
) AS dt
WHERE rank <= 3
```

# Part 2 - Data analysis

For every conference we produce, we release an app which allows our attendees to connect
with recommended peers. We are interested to determine how many of our users continue
to use our app after our event has finished. We consider someone to be an active user of
our app if they used the app in the last 30 days.
We would like to see what factors are the best predictors of user retention, using the
accompanying dataset.

1. What fraction of the observed users were retained?
2. Build a predictive model to help us determine whether or not a user will be retained.
Tell us why you chose these particular predictions, what alternatives you considered and any concerns you may have. How valid is your model? Include any key indicators of model performance.
3. Briefly discuss how we might leverage the insights you have gained into our data to improve our user retention over time.

Dataset description:

city: The city the user comes from

phone: Primary device of the user

signup_date: date of account registration

chats_in_first_30_days: Number of chats in the first 30 days

avg_chat_numbes: Average number of chats user engages with

avg_rating_of_app: Rating of the app by the user

avg_rating_of_attendee: Rating of the attendees based on their use of the app

last_chat_date: Last time the user chatted

premium_app_user: If user paid for premium access to the app

## Answer
## Question 1

```shell
python q1.py
```

## Question 2

```shell
python q2.py
```

### Notes
* The prediction result that is needed is either retained or not retained which means we want a model that best separates or divides our data. This is a classification model
* So we are trying to predict a category and our data is labeled
* Our sample size is smaller than 100K samples and is not text data

Because of these factors I decided to use K Nearest Neighbors.

* I removed 'last_chat_date', 'signup_date', 'phone' and 'city' because I don't think they contribute to the accuracy and performance of the model. Signup date and phone number doesn't tell us anything regarding the user's app retention. Last chat date is the value we use to determine if the user was retained.
* The 5, 'avg_chat_numbers' 'avg_rating_of_app' 'avg_rating_of_attendee' 'chats_in_fist_30_days' 'premium_app_user', predictors can all contribute to the category prediction.
* Included in the script there is a accuracy measure. Currently the model is +-66% accurate.

## Question 3
By knowing which factors influence the app's usage afterwards the you can use that to your advantage. For example:

1. If the 'premium_app_user' indicates that it has a big influence then maybe there are some features in the premium version that really keeps the user from using the app. It would maybe be worth placing that feature in the free version to increase user retention.
2. Based on the app rating if it has a big influence on user app retention then maybe the team should go and look on the app store at the app reviews and see why users are rating it so low. Is it because of bugs or a lack of specific features. Local focus groups and also be used to investigate low app ratings.

# Part 3 - Switches

You are a secret agent who is tracking an enemy spy.

You follow the spy to a hotel which has 8 rooms and find out what room the spy is staying in.

Your objective is to to pass on the room number the spy is staying in to a fellow agent who will arrive at the hotel the next day, after you have left the hotel.

The only means of passing on the information to your colleague is by flipping a single switch of a randomly configured switchboard of 40 switches (i.e. 40 simple light switches which can be either on or off) at the reception of the hotel.

You have previously agreed upon a method with your fellow agent before you set out on the mission.

You or your colleague don't know the initial configuration of the switchboard.

You can only touch one switch once to pass on the message.

The method you come up with must work no matter what configuration the switchboard is in
initially.

The switchboard remains in the same state you leave it in after you alter it, i.e. no one interferes with it after you have encoded the message.

## Answer

Switches that are on and off can be seen as 1s or 0s (binary) which means a binary system can be created on the switch board.

Discuss with your fellow agent that you will number the rooms as follow:

Room 1: 000

Room 2: 001

Room 3: 010

Room 4: 011

Room 5: 100

Room 6: 101

Room 7: 110

Room 8: 111

* So we have 3 bit rows (3 columns). Now give each column a letter like X, Y and Z respectively.
* The number of switches needed will be calculated by: 2 to the power of the number of binary numbers needed to represent the highest room number which in this example is 8 rooms = 111 binary = 3 bits, minus 1. Thus for this example it will be (2^3)-1 = 7
* Now draw a table with the 3 column values (X,Y,Z) and assign a letter fro each permutation.

| Column | 1 | 2 | 3 | 4 |
| --- | --- | --- | --- | --- |
| X | A | D | E | G |
| Y | B | D | F | G |
| Z | C | E | F | G |

* By looking at the table above you can see that changing A will only alter X
* Change B and only Y will change
* Change C and only Z will change
* Change D and both X and Y will change
* Change E and both X and Z will change
* Change F and both Y and Z will change
* Change G and all 3 X, Y and Z will change

**Exclusive or** or exclusive disjunction is a logical **operation** that outputs true only when inputs differ (one is true, the other is false). It can be symbolized by **XOR**. When the XOR result is an even number the result is 0 (zero) and when it is uneven the result is 1 (one).

Refer to the table above and compute XOR

X = A XOR D XOR E XOR G

Y = B XOR D XOR F XOR G

Z = C XOR E XOR F XOR G

## Example

Remember that only 7 switches are needed. So let's create some randomly and give each one a letter from A-G

| Info | 1 | 2 | 3 | 4 | 5 | 6 | 7 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Switch state | On | Off | On | On | Off | Off | Off |
| Switch bit value | 1 | 0 | 1 | 1 | 0 | 0 | 0 |
| Switch letter representation | A | B | C | D | E | F | G |

X = A XOR D XOR E XOR G = 1 XOR 1 XOR 0 XOR 0 = even 1's and 0's = 0

Y = B XOR D XOR F XOR G = 0 XOR 1 XOR 0 XOR 0 = uneven 1's and 0's = 1

Z = C XOR E XOR F XOR G = 1 XOR 0 XOR 0 XOR 0 = uneven 1's and 0's = 1

(X,Y,Z) = 011 = 4 in binary = Room 4

Let us now assume we want to tell our fellow spy that the enemy spy is in room 2. 2 in binary is 001 so currently the board's state is in 011 and we want it to be 001 which means we only want to change the middle bit from 1 to 0. We know that if we only want to change the middle bit represented by Y (X,Y,Z) we can change the bit represented by B because it will only alter/effect Y.

So switching the second switch (B) will allow the spy to convey the encoded message.

# Comclusion
I find this work extremely exciting, stimulating and fun. I am a hard worker and fast learner and will do anything to understand and become better in what I do. I am not afraid to spend hours on end to improve anything I do. I really want this job. I find the company to be exactly what I like and the people I’ll work with seem really good in what they do and dedicated.

**Thank you** for the opportunity thus far.

### Charl Best
