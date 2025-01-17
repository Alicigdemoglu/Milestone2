
from os import error
from re import S
from flask import escape
from sqlalchemy.orm import session
from werkzeug.security import check_password_hash, generate_password_hash
from myapp import myobj
from myapp import db
from myapp.loginforms import LoginForm
from myapp.deleteforms import DeleteForm
from myapp.noteforms import NoteForm
from myapp.models import User, Notes, Todo, Tracker, FlashCard
from myapp.searchforms import SearchForm
from myapp.registerforms import RegisterForm
from flask import render_template, escape, flash, redirect,request
from markdown import markdown
from flask_login import UserMixin,login_user,LoginManager,login_required,logout_user,current_user
from myapp.todoforms import ToDo
from myapp.workhrs import Track
from datetime import datetime
import pdfkit
from werkzeug.utils import secure_filename
from myapp.GetFile import GetFile
from myapp.flashcards import FlashCardForm

@myobj.route("/")
def home():
    """Return home page 
    """
    return render_template("home.html")

@myobj.route("/home")
def study():
    """
        Return home page (should be in html)
    """
    return render_template("home.html")

@myobj.route("/login", methods=['GET', 'POST'])
def login(): 
    '''
    Get the login in information from the login page and verify if the 
    information matching the exiting User database. If so log user in.
    otherwise, giving user warning message.
        Returns:
            return html pages
    '''
    form = LoginForm()
    # if the user hit submit on the forms page
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        user = User.query.filter_by(email=email).first()
        if user != None:
            passed = check_password_hash(user.password_hash,password)
            if passed == True:
                login_user(user)
                flash("Login Successfully!")
            else: 
                flash("Wrong information, please try again")
        else:
            flash('User doesn not exit, try agian!')
            return redirect('/login')
        return redirect('/home')
    return render_template('login.html',form=form)

@myobj.route("/logout", methods=['GET', 'POST'])
@login_required
def logout():
    '''
    Logout current user and block user from login required page
        Returns:
            return login html page
    '''
    logout_user()
    flash('Logout Successfully!')
    return redirect('/login')


@myobj.route("/register", methods=['GET', 'POST'])
def register():
    '''
    Get the sign up information from the sign up page and store them
    to the User database. Verify the sign up email if already exit, if
    so, flash message to user that email already exiting, otherwise add
    the new user information to the User database
        Returns:
            return html pages
    '''
    form = RegisterForm()
    if form.validate_on_submit():
        flash(f'{form.username.data} registered succesfully')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password_hash']
        password_hash = generate_password_hash(password)
        email = request.form['email']
        if User.query.filter_by(email=email).first():
            flash('Email already exsit')
        add_user = User(username=username,email=email, password_hash=password_hash)
        db.session.add(add_user)
        db.session.commit()
        return redirect('/login')
    return render_template('/register.html', form = form)

@myobj.route('/delete/', methods=['GET', 'POST'])
@login_required
def delete_account():
    '''
    Get the delete information from the delete page and verify if the 
    information matching the exiting User database and if the user are
    in their own account. If so delete the current user from the database.
    otherwise, giving user warning message.
        Returns:
            return html pages
    '''
    form = DeleteForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password_hash.data
        user = User.query.filter_by(email=email).first()
        passed = check_password_hash(user.password_hash,password) 
        if user.id == current_user.id and passed == True:   
            try:
                db.session.delete(user)
                db.session.commit()
                flash('Account Deleted Successfully!')
            except:
                flash('Something went wrong, please try agian later')
        else: 
            flash('Wrong Information, Please Try Agian!')
            return redirect('/delete')
    return render_template('/delete.html', form = form)

@myobj.route("/note", methods=['GET', 'POST'])
@login_required
def add_notes():
    '''
    Get the notes information from the add notes page and store notes
    in the Notes database.
        Returns:
            return html pages
    '''
    form = NoteForm()
    if form.validate_on_submit():
        note = Notes(title=form.title.data,user_id = current_user.id,text=form.text.data)
        db.session.add(note)
        db.session.commit()
        flash('Notes added')
    return render_template('note.html',form=form)

@myobj.route("/note_dashboard", methods=['GET', 'POST'])
@login_required
def notes_dashboard():
    '''
    Get current login user's notes information form Notes database
    and display all the notes in the dashboard page and provides
    a search box for user to search their notes by a word
        Returns:
            return html pages
    '''
    form = SearchForm()
    note_id = None
    word = ""
    notes = Notes.query.filter_by(user_id=current_user.id)
    if form.validate_on_submit():
        word = form.search.data
        for i in notes:
            found_test= i.text
            found_title=i.title
            if word in found_test:
                flash('word found in note title : ' +found_title + ', with content : ' + found_test)
        flash('No word found' )
    for note in notes:
        note_id = note.user_id
    return render_template('note_dashboard.html',notes=notes,note_id=note_id,form=form,word=word)


@myobj.route("/todo", methods = ['GET', 'POST'])
@login_required
def toDo():
    '''
        Allows the user to create a Todo list that lets them type what is due,
        when it is due, and how important that assignment is (priority)
            Returns:
                String
    '''
    form = ToDo()

    if form.validate_on_submit():
        flash(f' {form.goal.data} added')
        goalname = form.goal.data
        prior = form.prio.data
        dueDate = form.due_date.data
        doList = Todo(goal = goalname, prio = prior,due_date = dueDate)
        db.session.add(doList)
        db.session.commit()
        return redirect ("todo")

    orderList = Todo.query.order_by(Todo.prio).all()
    return render_template('todo.html', form = form, orderList = orderList)
@myobj.route("/track",methods = ['GET', 'POST'])
@login_required
def trackhours():
    '''
        Allows the user to input when they worked and how many hours
        they worked. This function will create a list that will store 
        the data, so they can track how many hours they worked that day.
            Returns:
                Date
                Integer
    '''
    form = Track()

    if form.validate_on_submit():
        flash(f' data saved')
        hoursworked = form.hours.data
        dateworked = form.datew.data
        organize = Tracker(hours = hoursworked,datew = dateworked)
        db.session.add(organize)
        db.session.commit()
    current = datetime.now().strftime("%m/%d/%Y")
    order = Tracker.query.all()
    return render_template('tracker.html',current = current, form = form, order = order )
@myobj.route("/cards", methods=['GET', 'POST'])
@login_required
def add_card():
    '''
    Stores the card information in the card database.
        Returns:
            return html pages
    '''
    form = FlashCardForm()
    if form.validate_on_submit():
        card = FlashCard(title=form.title.data,user_id = current_user.id,content=form.content.data)
        db.session.add(card)
        db.session.commit()
        flash('Card added')
    return render_template('flashcard.html', form=form)

@myobj.route("/myflashcards", methods=['GET', 'POST'])
@login_required
def my_flashcards():
    '''
    View all the flashcards of the user
        Returns:
            return html pages
    '''
    card_id = None
    cards = FlashCard.query.filter_by(user_id=current_user.id)
    for card in cards:
        card_id = card.user_id
    return render_template('myflashcards.html', cards=cards, card_id=card_id)

@myobj.route("/cardtopdf", methods=['GET', 'POST'])
@login_required
def card_to_pdf():
    '''
    Convert Card to pdf
        Returns:
            return pdf file
    '''
    form = GetFile()
    if form.validate_on_submit():
        name = secure_filename(form.file.data.name)
        form.file.data.save('myapp/static/cards/' +name)
        input_name= 'myapp/static/cards/' +name
        output_name=input_name.split(".html")[0] + ".pdf"
        pdfkit.from_file(input_name, output_name)
        return render_template('cardtopdf.html', form=form, pdf=output_name)
    return render_template('cardtopdf.html', form=form)
