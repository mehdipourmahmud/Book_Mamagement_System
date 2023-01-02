import datetime
from datetime import timedelta
from flask import Flask,url_for,request,flash,redirect,render_template,session
import pymongo
app = Flask(__name__)
app.secret_key="secret_key"
# myclient= pymongo.MongoClient("memeber.t"")
myclient= pymongo.MongoClient("mongodb+srv://hamedan386:hamedan386@cluster0.2uadrnr.mongodb.net/test")   #Campass
myclient= pymongo.MongoClient("mongodb+srv://hamedan386:hamedan386@cluster0.2uadrnr.mongodb.net/?retryWrites=true&w=majority") #Atlas
mydb = myclient["LMS"]



@app.route("/")
def hello():
    return render_template("home.html")

@app.route("/home")
def home():
    return render_template("home.html")
    
    
@app.route("/about")
def about():
    return render_template("about.html")
@app.route("/contact")
def contact():
    return render_template("contact.html")
# ----------------------------------------------------------------Sign Up----------------------------------------------------------------------------
userfirstname=""
userlastname=""
useremail=""
userpassword=""
usertype=""
joined=''
class user:
  def __init__(self,*user):
        self.userfirstname = user[0]
        self.userlastname = user[1]
        self.useremail = user[2]
        self.userpassword = user[3]
        self.usertype = user[4]
        self.joined = user[5]
  def addUser(self):
          mydb.Users.insert_one({"user_first_name":self.userfirstname,"user_last_name":self.userlastname,"user_email":self.useremail,"user_password":self.userpassword,"user_type":self.usertype,"joined":self.joined}) 
    
@app.route("/signup", methods=["POST","GET"])
def signup():
    if request.method =="POST":
        user_first_name= request.form["firstName"]
        user_last_name=request.form["lastName"]
        user_email=request.form["InputEmail1"]
        user_password=request.form["InputPassword1"]
        user_repassword=request.form["reInputPassword1"]
        user_type="member"
        joined =datetime.datetime.now().strftime("%c")
        if not user_first_name.isalpha() and not user_last_name.isalpha():
            flash("Invalid First Name/Last Name","danger")
            return render_template("signup.html")
        elif user_password != user_repassword:
            flash("Passwords not matched","danger")
            return render_template("signup.html")
        else:
            try:
                isertUser = user(user_first_name,user_last_name,user_email,user_password,user_type,joined)
                isertUser.addUser()
                flash("successfully registered","success")  
                return render_template("login.html")
            except pymongo.errors.DuplicateKeyError:
                    flash('Email and Password must be unique','danger')
                    return render_template('signup.html')


    else:
        return render_template('signup.html')



# ----------------------------------Login-----------------------------------------------------



@app.route("/login", methods=["POST","GET"])
def login():
    if "user" in session:
        return render_template("profile.html",username=username,joined=joined)
    else:                        
        if request.method=="POST":
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=120)
            adminpassword = request.form["admin"]
            user_email=request.form["InputEmail1"]
            user_password=request.form["InputPassword1"]
            countThree = mydb.Users.count_documents({"username":adminpassword})
            countOne = mydb.Users.count_documents({"user_email":user_email})
            user_passwordfound = mydb.Users.find({"user_email":user_email})
            for y in user_passwordfound:
                user_pass = y["user_password"]
                if user_pass==user_password:
                    countTwo = mydb.Users.count_documents({"user_password":user_password})
                    if countOne and countTwo:
                        session["user"]=user_email
                        userName = mydb.Users.find({"user_email":user_email})
                        for x in userName:
                            username = x["user_first_name"]
                            joined = x["joined"]
                        return render_template("profile.html",username=username,joined=joined)

                    else:
                        flash('Invalid Password',"danger")
                else:
                    flash('Invalid Password',"danger")
                    return render_template('login.html')
            if countThree:
                            session["admin"] = adminpassword
                            return redirect(url_for('view'))
            else:
                    flash('Invalid Password',"danger")
                    return render_template('login.html')
                
        else:
            return render_template('login.html')

# -------------------------------------view & search---------------------------------------------------
@app.route('/view',methods=["POST","GET"])
def view():
    if request.method=="POST":
        searchInput = request.form["search"].split(" ")
        books = mydb.Book.aggregate([{
                                        "$search": {
                                        "index": "title",
                                        "text": {
                                            "query": searchInput,
                                            "path": {
                                            "wildcard": "*"
                                            }
                                        }
                                        }
                                    }
                                    ])
        return render_template('view.html',books=books)
    else:
        if "user" in session or "admin" in session:
            books = mydb.Book.find({})
            return render_template('view.html',books=books)
        else:
            return render_template("home.html")    



# ---------------------------------------------add new books----------------------------------------
bookId=""
bookTitle=""
bookAuthor=""
bookPublisher=""
bookLanguage=""
bookCategory=""
bookCover=""
class book:
  def __init__(self,*book):
        self.bookAuthor = book[0]
        self.bookId = book[1]
        self.bookCategory = book[2]
        self.bookLanguage = book[3]
        self.bookPublisher = book[4]
        self.bookTitle = book[5]
        self.bookCover = book[6]
  def addBook(self):
          mydb.Book.insert_one({"author":self.bookAuthor,"book_id":self.bookId,"category":self.bookCategory,"language":self.bookLanguage,"publisher":self.bookPublisher,"title":self.bookTitle,"book_cover":self.bookCover}) 
  def updateBook(self):
          myquery = {"book_id":self.bookId}
          newvalues = {"$set": {"author":self.bookAuthor,"category":self.bookCategory,"language":self.bookLanguage,"publisher":self.bookPublisher,"title":self.bookTitle,"book_cover":self.bookCover}} 
          mydb.Book.update_one(myquery,newvalues) 

@app.route("/add", methods=["POST","GET"])
def add():
     if request.method=="POST":
        id = (request.form["id"])
        title = request.form["title"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        language = request.form["language"]
        category = request.form["category"]
        book_cover = request.form["url"]
        count = mydb.Book.count_documents({"book_id":id})
        if count:
            flash("Invalid ID","danger")
            return render_template("add.html")
        else:    
            isertbook = book(author,id,category,language,publisher,title,book_cover)
            isertbook.addBook()
            flash("book successfully added","success")
            return redirect(url_for('view'))
     else:
          return render_template('add.html')
# ------------------------------delete---------------------------------------------------------------

@app.route("/delete/<book_id>")
def delete(book_id):
             mydb.Book.delete_one({"book_id":book_id})
             return redirect(url_for('view'))

# ---------------------------------update---------------------------------------------------------------------

@app.route("/update/<book_id>")
def update(book_id):
    bookfound = mydb.Book.find({"book_id":book_id})
    for x in bookfound:
         book_id =int(x["book_id"]) 
         title = x["title"]
         author = x["author"]
         language = x["language"]
         publisher = x["publisher"]
         category = x["category"]
         book_cover=x["book_cover"]
         return render_template('update.html',title=title,book_id=book_id,author=author,language=language,publisher=publisher,category=category,book_cover=book_cover)


@app.route("/updateBook",methods=["POST","GET"])
def updateBook():  
    if request.method == "POST":
        book_id =request.form["id"]
        title = request.form["title"]
        author = request.form["author"]
        publisher = request.form["publisher"]
        language = request.form["language"]
        category = request.form["category"]
        book_cover =request.form["url"]  
        try:
            updatebook = book(author,book_id,category,language,publisher,title,book_cover)
            updatebook.updateBook()
            flash("book successfully updated","success")
            return redirect(url_for("view"))
        except Exception:
                print('error')
    else:
        return render_template("update.html")
           
# ----------------------------------borrow------------------------------------------------------        

@app.route("/borrowBook/<book_id>")
def borrowBook(book_id):
    count = mydb.bookStatus.count_documents({"book_id":book_id})
    if count:
        cursor = mydb.bookStatus.find({"book_id":book_id})
        for x in cursor:
                availability = x["book_status"]
                if availability=="onloan":
                    flash("This book is not available!","danger")
                    return redirect(url_for("view"))
                else:
                   user_email=session["user"]
                   cursor = mydb.Users.find({"user_email":user_email})
                   for x in cursor:
                    user_id = x["_id"]
                   myquery = {"book_id":book_id}
                   dueDate=datetime.datetime.now() + datetime.timedelta(days=21)
                   newvalues = {"$set": {"book_status":"onloan","user_id":user_id,"dueDate":dueDate}} 
                   mydb.bookStatus.update_one(myquery,newvalues)
                   flash("This book is successfully added to your book list","success")
                   return redirect(url_for("view"))
    else:
        dueDate=datetime.datetime.now()+ datetime.timedelta(days=21)
        user_email=session["user"]
        cursor = mydb.Users.find({"user_email":user_email})
        for x in cursor:
            user_id = x["_id"]
        mydic = {"book_status":"onloan","book_id":book_id,"user_id":user_id,"dueDate":dueDate}
        mydb.bookStatus.insert_one(mydic)
        flash("book is successfully added","success")
        return redirect(url_for("view"))





@app.route("/viewBook/<book_id>")
def viewBook(book_id):
        bookfound = mydb.Book.find({"book_id":book_id})
        for x in bookfound:
            book_id =int(x["book_id"]) 
            title = x["title"]
            author = x["author"]
            language = x["language"]
            publisher = x["publisher"]
            category = x["category"]
            book_cover=x["book_cover"]
            return render_template('viewBook.html',title=title,book_id=book_id,author=author,language=language,publisher=publisher,category=category,book_cover=book_cover)


# -------------------------------return------------------------------------------------------------------
@app.route('/returnBook/<book_id>')
def returnBook(book_id):
    count = mydb.bookStatus.count_documents({"book_id":book_id})
    if count: 
        user_email=session["user"]
        cursor = mydb.Users.find({"user_email":user_email})
        for x in cursor:
            user_id1 = x["_id"]
        findUser =mydb.bookStatus.find({"book_id":book_id})
        for y in findUser:
            user_id2 = y["user_id"]
        if user_id1 == user_id2:
                    cursor = mydb.bookStatus.find({"book_id":book_id})
                    for x in cursor:
                        availability = x["book_status"]
                        if availability=="onloan":
                            myquery = {"book_id":book_id}
                            newvalues = {"$set": {"book_status":"available","user_id":"","dueDate":""}} 
                            mydb.bookStatus.update_one(myquery,newvalues)
                            flash("This book has returened","success")
                            return redirect(url_for("view"))
                        else:
                            flash("This book is available for borrowing","info")
                            return redirect(url_for("view"))

        else:
            flash("This book is not in your borrowed list","danger")
            return redirect(url_for("view"))

    else:
            return redirect(url_for("view"))

#   ---------------------------------log out-----------------------------------------------------------------
@app.route('/logout')
def logout():
    session.pop("user", None)
    session.pop("admin", None)
    session.clear()
    return render_template('logout.html')



# ------------------borrowedBooks------------------------------------------



@app.route('/borrowedBooks')
def borrowedBooks():
        listBooks=[]
        dueDate=''
        user_email=session["user"]
        cursor = mydb.Users.find({"user_email":user_email})
        for x in cursor:
                    user_id1 = x["_id"]
                    findUser = mydb.bookStatus.find({"user_id":user_id1 })
                    for y in findUser:
                        dueDate = y["dueDate"].strftime("%c")
                        book_id =(y["book_id"])
                        listBooks.append(book_id)
                        print(listBooks)
                    findUserdate = mydb.bookStatus.count_documents({"user_id":user_id1 }) 
                    if findUserdate:       
                        books = mydb.Book.find({"book_id": {"$in": listBooks}})
                        return render_template("borrowedBooks.html", books=books,dueDate=dueDate)
                    else:
                        return render_template("view.html")        


   









if __name__ == '__main__':
    app.run(debug=True)

