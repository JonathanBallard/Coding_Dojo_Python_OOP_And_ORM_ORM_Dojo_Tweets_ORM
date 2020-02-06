
# TODO
# 
# CREATE DB Classes --DONE-- 
# Create DB relationships --DONE--
# Update all routes to use correct queries --DONE--
# Check templates for same --DONE--
# CURRENTLY SHOWS ALL TWEETS
# FIX EDIT   --DONE--
# FIX DELETE


from flask import Flask, render_template, request, redirect, session, flash
from flask_sqlalchemy import SQLAlchemy			# instead of mysqlconnection
from sqlalchemy.sql import func                         # ADDED THIS LINE FOR DEFAULT TIMESTAMP
from flask_migrate import Migrate			# this is new
import re
from flask_bcrypt import Bcrypt
from sqlalchemy import text


app = Flask(__name__)
# configurations to tell our app about the database we'll be connecting to
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///$dojo_tweets_orm.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# an instance of the ORM
db = SQLAlchemy(app)
# a tool for allowing migrations/creation of tables
migrate = Migrate(app, db)
app.secret_key = "secretstuff"
bcrypt = Bcrypt(app)     # we are creating an object called bcrypt, 
                         # which is made by invoking the function Bcrypt with our app as an argument



likes_table = db.Table('likes',
db.Column('user_id', db.Integer, db.ForeignKey('Users.id', ondelete='cascade'), primary_key=True),
db.Column('tweet_id', db.Integer, db.ForeignKey('Tweets.id', ondelete='cascade'), primary_key=True))


follows_table = db.Table('follows',
db.Column('user_being_followed', db.Integer, db.ForeignKey('Users.id', ondelete='cascade')))



class Users(db.Model):	
    __tablename__ = "Users"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(45))
    last_name = db.Column(db.String(45))
    email = db.Column(db.String(45))
    password = db.Column(db.String(255))
    tweet_id = db.relationship('Tweets', secondary=likes_table)
    user_being_followed = db.relationship('Users', secondary=follows_table)
    user_following = db.relationship('Users', secondary=follows_table)

    # group_id = db.Column(db.ForeignKey(Group.id))
    # group = db.relationship(Group, backref='users')


    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())



class Tweets(db.Model):	
    __tablename__ = "Tweets"    # optional		
    id = db.Column(db.Integer, primary_key=True)
    tweet = db.Column(db.String(255))
    user_id = db.relationship(Users, secondary=likes_table)
    created_at = db.Column(db.DateTime, server_default=func.now())    # notice the extra import statement above
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())









@app.route('/')
def index():
    users = Users.query.all()
    print(users)
    return render_template("index.html", all_users = users)


@app.route('/register', methods=['POST'])
def register():

    users = Users.query.all()
    print(users)
    EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
    PW_REGEX = re.compile(r'^.*(?=.{8,10})(?=.*[a-zA-Z])(?=.*?[A-Z])(?=.*\d)[a-zA-Z0-9!@£$%^&*()_+={}?:~\[\]]+$')
    firstName = request.form['first_name']
    lastName = request.form['last_name']
    email = request.form['email']
    password = request.form['password']
    conPassword = request.form['passwordConfirm']
    form = request.form['formType']
    isValid = True
    pwHash = bcrypt.generate_password_hash(password).decode('utf-8')


    if len(firstName) <= 0:
        isValid = False
        flash('Please enter a first name', 'register')

    if not firstName.isalpha():
        isValid = False
        flash('Please enter a first name using only alphabetic characters', 'register')

    if len(lastName) <= 0:
        isValid = False
        flash('Please enter a last name', 'register')

    if not lastName.isalpha():
        isValid = False
        flash('Please enter a last name using only alphabetic characters', 'register')

    if len(email) <= 3:
        isValid = False
        flash('Please enter an email address', 'register')

    if not EMAIL_REGEX.match(request.form['email']):
        isValid = False
        flash("Invalid email address!", 'register')

    if not PW_REGEX.match(request.form['password']):
        isValid = False
        flash("Invalid password! Minimum 8 characters, 1 number, and 1 special character", 'register')

    if len(password) <= 4:
        isValid = False
        flash('Please enter a valid password (minimum 5 characters)', 'register')

    if not password == conPassword:
        isValid = False
        flash('Password doesnt match confirm password', 'register')

    
    
    if isValid == True:
        new_user = Users(first_name = firstName, last_name =lastName, email = email, password=pwHash)
        db.session.add(new_user)
        db.session.commit()

        users = Users.query.all()
        print(users)
        flash('Success!')
        return redirect('/')
    else:
        return redirect('/')

@app.route('/destroy', methods=['POST','GET'])
def destroy():
    session.clear()
    return redirect('/')

@app.route('/login', methods=['POST'])
def login():


    form = request.form['formType']

    email = request.form['emailLogin']
    password = str(request.form['passwordLogin'])

    data = {
        "em": email
    }


    # query = "SELECT email FROM users WHERE email = %(em)s;"
    emailCheckDB = Users.query.filter_by(email = email).all()
    print('TEEEEEEEEEEEEEEEEEEEEEST', emailCheckDB)
    # check if emailCheckDB is populated
    if len(emailCheckDB) == 0:
        emailCheckDBFull = False
    else:
        emailCheckDBFull = True

    login_id = Users.query.filter_by(email = email).all()
    # query = "SELECT password FROM users WHERE email= %(em)s;"
    
    
    # user first name
    # query = "SELECT first_name FROM users WHERE email = %(em)s;"
    userId = Users.query.filter_by(email = email).all()

    # userId

    # query = "SELECT id FROM users WHERE email = %(em)s;"
    idDict = Users.query.filter_by(email = email).all()

    print('idDict^%^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^', idDict)
    if len(idDict) > 0:
        session['id'] = idDict[0].id
        
    if not emailCheckDBFull:
        print('EmailCheck ****************************', 'email')
        flash('Email not in our database', 'login')
        return redirect('/')
    else:
        hashCheck = bcrypt.check_password_hash(login_id[0].password, password)
        print('hashCheck ***************************************', hashCheck)
        if not hashCheck:
            flash('Invalid Password', 'login')
            return redirect('/')
        else:
            flash("Successfully Logged In!")
            if not 'user_id' in session:
                session['user_id'] = userId[0].first_name
                print('Session[user_id] *******---------------+***********', session['user_id'])
            return redirect('/dashboard')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():

    if not session['id']:
        return redirect('/')

    
    # userFriends = mysql.query_db(f"SELECT followed_user_id FROM follows WHERE follower_user_id = {session['id']} OR user_id = {session['id']}")
    # userFriends = Users.query('user_being_followed').filter('user_following' == session['id'] OR 'id' == session['id'])

    # return list of tweets for welcome.html
    # tweetList = mysql.query_db(f"SELECT * FROM tweets")   #SELECT ALL TWEETS
    # tweetList = mysql.query_db(f"SELECT * FROM tweets WHERE user_id = {session['id']}")  #ONLY SHOW TWEETS THAT PERSON MADE


    friendsList = list()

    # for index in range(len(userFriends)):
        # print('INDEX+++++++++++++++++++++++++++++++++', index)
        # friendsList[index].append(userFriends[index]['followed_user_id'])
        # x = userFriends[index]['followed_user_id']

    # friendsList = [4,6]

    # tweetList = mysql.query_db(f"SELECT * FROM tweets WHERE user_id IN {friendsList}")  #SELECT MY AND FRIENDS TWEETS
    # print('TWEETLIST =======__________________________________=====', tweetList)


    
    # tweetList = mysql.query_db(f"SELECT * FROM tweets JOIN users ON tweets.user_id = users.id JOIN follows ON users.id = follows.user_id")  #SELECT MY AND FRIENDS TWEETS
    tweetList = Tweets.query.all()
    usersList = Users.query.all()
    print('TWEETLIST =======__________________________________=====', tweetList)


    tweetTuple = ()
    friendsList.append(session['id'])
    friendsList.append(session['id'])


    for index in range(len(tweetList)):
        if tweetList[index].user_id == session['id']:
            friendsList.append(tweetList[index].user_id)

    for index in range(len(usersList)):
        if usersList[index].user_following == session['id']:
            friendsList.append(usersList[index].user_being_followed)

            


    if len(friendsList):
        tweetTuple = tuple(friendsList)
    else:
        tweetTuple = tuple()

    tweetList3 = list(tweetTuple)

    # tweetList2 = Tweets.query.from_statement(text(f"SELECT * FROM Tweets WHERE users_who_like_this_tweet IN {tweetTuple}"))
    # tweetList2 = Tweets.query.filter_by(Users.user_being_followed.in_(tweetList3))
    # tweetList2 = mysql.query_db(f"SELECT * FROM tweets WHERE user_id IN {tweetTuple}")
    tweetList2 = Tweets.query.all()
    tweetListFinal = list()

    for tweet in range(len(tweetList2)):
        print('tweet.user_id   323222222222222222222222222222222222222222222222', tweetList2[tweet].user_id)
        if tweetList2[tweet].user_id in tweetList3:
            print('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++ appending')
            tweetListFinal.append(tweetList2[tweet])
    
    # tweetList = mysql.query_db(f"SELECT tweets.id, tweets.tweet, tweets.created_at, tweets.updated_at, tweets.user_id, follows.followed_user_id, follows.follower_user_id FROM tweets JOIN users ON tweets.user_id = users.id JOIN follows ON users.id = follows.user_id WHERE tweets.user_id IN {followed_users} GROUP BY tweets.id")
    
    print('tweetList2   23222222222222222222222222222222222222222222222', tweetList2)
    print('tweetList3   23222222222222222222222222222222222222222222222', tweetList3)
    print('tweetListFinal   23222222222222222222222222222222222222222222222', tweetListFinal)


    # get number of likes to display per tweet

    # likesNum = mysql.query_db("SELECT COUNT(id) FROM likes GROUP BY tweet_id")
    likesNum = 55
    print('LIKESNUM=======55555555555555555555555555=====', likesNum)

    return render_template('welcome.html', tweetList = tweetList2, likesNum = likesNum)




@app.route('/tweets/create', methods=['POST', 'GET'])
def tweet_create():

    if request.method == 'GET' or not session['id']:
        return redirect('/')

    # validate tweets here
    incomingTweet = request.form['tweet']
    isValid = True

    if len(incomingTweet) > 255 or len(incomingTweet) < 1:
        isValid = False
        flash("Invalid Tweet, must be between 1 and 255 characters", 'tweet')


    if isValid:
        # enter tweet into database
        
        
        print('SESSION ID----------*******************************************', session['id'])
        print('TWEET----------*******************************************', incomingTweet)

        new_tweet = Tweets(tweet = incomingTweet)
        db.session.add(new_tweet)
        db.session.commit()
        # query = "INSERT INTO tweets (tweet, user_id) VALUES(%(tweet)s, %(id)s);"


    return redirect('/dashboard')




# delete route here
@app.route('/tweets/<id>/delete', methods=['POST'])
def delete_tweet(id):
    print('DELETE ID----------*******************************************', id)
    

    tweet_check = Tweets.query.get(id)
    # tweet_check = mysql.query_db(f"SELECT user_id FROM tweets WHERE id={id};")

    print('TWEET CHECK ID----------*******************************************', tweet_check.user_id)
    tweet_delete = Tweets.query.get(id)
    db.session.delete(tweet_delete)
    db.session.commit()


    # CHECK IF USER IS WRITER OF TWEET ----- NOT WORKING -----
    # if userId of tweet = session['id]
    # if tweet_check.user_id == session['id']:
    #     tweet_delete = Tweets.query.get(id)
    #     db.session.delete(tweet_delete)
    #     db.session.commit()
    #     # tweet_delete = mysql.query_db(f"DELETE FROM tweets WHERE id={id};")
    # else:
    #     flash('invalid user')

    return redirect('/dashboard')


# edit route here
@app.route('/tweets/<id>/edit', methods=['POST'])
def edit_tweet(id):
    return render_template('edit.html', tweetId = int(id))
    

# update route here
@app.route('/tweets/<id>/update', methods=['POST'])
def update_tweet(id):

    t_id = int(id)
    tweet = request.form['tweet']
    
    

    # query = "UPDATE tweets SET tweet = %(tweet)s WHERE id=%(id)s;"
    

    if len(request.form['tweet']) < 1 or len(request.form['tweet']) > 255:
        flash('Invalid tweet length')
    else:    
        tweet_edit = Tweets.query.get(t_id)
        # tweet_edit = mysql.query_db(query, data)
        tweet_edit.tweet = tweet
        db.session.commit()
    return redirect('/dashboard')
    






# add like route here
@app.route('/tweets/<id>/like', methods=['POST'])
def like_tweet(id):
    

    # add like to DB
    userId = session['id']
    tweet_to_like = Tweets.query.get(id)
    user = Users.query.get(session['id'])
    tweet_to_like.user_id.append(user)
    # tweet_like = mysql.query_db(f"INSERT INTO likes (user_id, tweet_id) VALUES({userId}, {id});")
    print('USER ID----------*******************************************', userId)
    print('TWEET ID----------*******************************************', id)
    return redirect('/dashboard')



# add users route here
@app.route('/users')
def get_users():

   
    users = Users.query.all()

    return render_template('/users.html',  users = users)

# add follow to DB

@app.route('/users/<id>/follow')
def follow_user(id):

    
    intId = int(id)

    userId = session['id']
    user_to_follow = Users.query.get(id)
    user = Users.query.get(session['id'])
    user.user_being_followed.append(user_to_follow)



    # follow = mysql.query_db(f"INSERT INTO follows (followed_user_id, follower_user_id, user_id) VALUES ({intId}, {session['id']}, {session['id']} );")


    print('FOLLOW**********************************************************', )

    return redirect('/dashboard')





if __name__ == "__main__":
    app.run(debug=True)