import os,requests

from flask import Flask, session,render_template,request,jsonify
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash,check_password_hash

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/")
def index():
    if "user_id" not in session.keys():
        session["user_id"] = None
        return render_template("index.html")
    elif session["user_id"] is None:
        return render_template("index.html")
    else:
        return render_template("search.html",books2018=session["top_rated_books"][0],books2017=session["top_rated_books"][1],books2016=session["top_rated_books"][2],books2015=session["top_rated_books"][3],books2014=session["top_rated_books"][4],booksalltime=session["top_rated_books"][5])

@app.route("/register",methods=["POST","GET"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    else:    
        username = request.form.get("username")
        already_present_username = db.execute("SELECT user_id from USERS where username = :username", {"username" : username}).fetchall()
        if len(already_present_username) == 0:     
            password = request.form.get("password")
            email = request.form.get("email")
            confirmpassword = request.form.get("confirmpassword")
            if password == confirmpassword:
                hashed_password = generate_password_hash(password)
                db.execute("INSERT INTO USERS (username,password,email) VALUES (:username,:password,:email)", {"username" : username,"password" : hashed_password, "email" : email})
                db.commit()
                user_id = db.execute("SELECT user_id from USERS where username = :username", {"username" : username}).fetchone()
                session["user_id"] = user_id[0]
                books2018 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2018").fetchall() 
                books2017 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2017").fetchall()               
                books2016 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2016").fetchall()
                books2015 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2015").fetchall()
                books2014 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2014").fetchall()
                booksalltime = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5)").fetchall()
                session["top_rated_books"] = [books2018,books2017,books2016,books2015,books2014,booksalltime]
                return render_template("search.html",books2018=books2018,books2017=books2017,books2016=books2016,books2015=books2015,books2014=books2014,booksalltime=booksalltime)
            else:
                return render_template("error.html",error="password not same as confirm password")    
        else :
            return render_template("error.html",error="Sorry username already taken")

@app.route("/login",methods=["POST","GET"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:    
        username = request.form.get("username")
        password = request.form.get("password")
        stored_password = db.execute("SELECT password FROM users WHERE username = :username" , {"username" : username}).fetchone()
        if check_password_hash(stored_password[0],password):
            user_id = db.execute("SELECT user_id from USERS where username = :username", {"username" : username}).fetchall()
            session["user_id"] = user_id[0][0]
            books2018 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2018").fetchall() 
            books2017 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2017").fetchall()               
            books2016 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2016").fetchall()
            books2015 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2015").fetchall()
            books2014 = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5) AND year = 2014").fetchall()
            booksalltime = db.execute("SELECT title,author,isbn from books WHERE isbn in (SELECT isbn from reviews group by isbn order by AVG(rating) DESC LIMIT 5)").fetchall()
            session["top_rated_books"] = [books2018,books2017,books2016,books2015,books2014,booksalltime]
            return render_template("search.html",books2018=books2018,books2017=books2017,books2016=books2016,books2015=books2015,books2014=books2014,booksalltime=booksalltime)
        else:
            return render_template("error.html",error="wrong password")    
    

@app.route("/logout")
def logout():
    session["user_id"] = None
    return render_template("index.html")

@app.route("/search",methods=["POST"])
def search():
    if request.method == "POST":
        if session["user_id"] is not None:
            word = request.form.get("search")
            word = '%' + word + '%'
            books = db.execute("SELECT title,author,isbn from books WHERE title LIKE  :word OR author LIKE  :word  OR isbn LIKE  :word ",{"word" : word}).fetchall()
            if len(books) == 0:
                return render_template("search.html",books=books,error="no books related to the search",books2018=session["top_rated_books"][0],books2017=session["top_rated_books"][1],books2016=session["top_rated_books"][2],books2015=session["top_rated_books"][3],books2014=session["top_rated_books"][4],booksalltime=session["top_rated_books"][5])
            else:
                return render_template("search.html",books=books,books2018=session["top_rated_books"][0],books2017=session["top_rated_books"][1],books2016=session["top_rated_books"][2],books2015=session["top_rated_books"][3],books2014=session["top_rated_books"][4],booksalltime=session["top_rated_books"][5])
        else:
            return render_template("index.html")

@app.route("/<string:isbn>",methods=["GET","POST"]) 
def book(isbn):

    # get goodreads rating which is to be used by both post and get method
    goodreadsrating = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.environ.get("API_KEY"), "isbns": isbn})
    if goodreadsrating.status_code != 200:
      raise Exception("ERROR: API request unsuccessful.")
    goodreadrating = goodreadsrating.json()

    # change responsre to a list containing at [0] no. of rating and at 1 avg rating
    apirating = [goodreadrating["books"][0]["work_ratings_count"],goodreadrating["books"][0]["average_rating"]]
    
    if request.method == "GET":
        book = db.execute("SELECT * FROM books WHERE isbn = :isbn", { "isbn" : isbn}).fetchone()
        reviews = db.execute("SELECT rating,review,username from reviews INNER JOIN users ON reviews.user_id = users.user_id WHERE  isbn = :isbn", { "isbn":isbn}).fetchall()
        if db.execute("SELECT * from reviews WHERE user_id = :user_id AND isbn = :isbn", { "user_id":session["user_id"],"isbn":isbn}).rowcount == 0:
            return render_template("book.html",reviews=reviews,book=book,apirating=apirating)
        else:
            return render_template("bookreviewdone.html",reviews=reviews,book=book,apirating=apirating)
    else:
        bookrating = request.form.get("bookrating")
        bookreview = request.form.get("bookreview")
        if db.execute("SELECT * FROM reviews where isbn = :isbn AND user_id = :user_id", {"isbn" : isbn ,"user_id" :session["user_id"] }).rowcount != 0:
            return render_template("error.html",error="looks like you have already subitted a review. please dont try to submit again. try going back from this page")
        else:
            db.execute("INSERT INTO reviews values(:isbn,:user_id,:rating,:review)",{"isbn":isbn,"user_id":session["user_id"],"rating":bookrating,"review":bookreview})
            db.commit()
            book = db.execute("SELECT * FROM books WHERE isbn = :isbn", { "isbn" : isbn}).fetchone()
            reviews = db.execute("SELECT rating,review,username from reviews INNER JOIN users ON reviews.user_id = users.user_id WHERE  isbn = :isbn", { "isbn":isbn}).fetchall()
            return render_template('bookreviewdone.html',reviews=reviews,book=book,apirating=apirating)

@app.route("/api/<string:isbn>")
def book_api(isbn):
    book = db.execute("SELECT title,author,year,books.isbn,COUNT(review),AVG(rating) FROM books INNER JOIN reviews ON books.isbn = reviews.isbn WHERE books.isbn = :isbn GROUP BY books.isbn ",{"isbn" : isbn}).fetchone()
    if book is None:
        return jsonify({"error" : "try checking your isbn,wrong isbn" }),404
    return jsonify({
    "title": book[0],
    "author": book[1],
    "year": book[2],
    "isbn": book[3],
    "review_count": book[4],
    "average_score": book[5]
    }),200


