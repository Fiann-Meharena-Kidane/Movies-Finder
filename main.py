from flask import Flask, render_template, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, String, create_engine, DATE, Float, desc

from sqlalchemy.orm import declarative_base, session
from wtforms import StringField, SubmitField, validators
from wtforms.validators import DataRequired
import requests
import os


api_key=os.environ.get('movie_key')
# example_request="https://api.themoviedb.org/3/movie/550?api_key=api_key"


app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('movie_secret_key')


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my-movies.db'
# connect app to our db,

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
# silence error if set to False ?

db = SQLAlchemy(app)
# create a db object from SQLAlchemy class by passing our app,

Base = declarative_base()


class Movie(Base, db.Model):
    # creates a Book table, inherits from both Base an db.Model too,

    __tablename__ = 'Movies'
    # book name,

    id = Column(Integer, primary_key=True)
    title = Column(String, unique=False)
    year = Column(String, nullable=False)
    description=Column(String,nullable=False)
    rating = Column(Float, nullable=False)
    ranking=Column(Integer,nullable=False)
    review=Column(String, nullable=False)
    img_url=Column(String,nullable=False)
    # columns of our table along with their constraints


if __name__ == '__main__':
    engine = create_engine('sqlite:///my-movies.db')
    Base.metadata.create_all(engine)


db.create_all()


new_movie = Movie(
        title="Book Book",
        year=2022,
        description="Shepard finds himself trapped in a phone booth, pinned down by an extortionist's sniper rifle. Unable to leave or receive outside help, Stuart's negotiation with the caller leads to a jaw-dropping climax.",
        rating=5.3,
        ranking=6,
        review="My favourite actor was the worker.",
        img_url="https://image.tmdb.org/t/p/w500/tjrX2oWRCM3Tvarz38zlZM7Uc10.jpg"
)

#
# db.session.add(new_movie)
# db.session.commit()
#


class EditForm(FlaskForm):
    # creates a from to change movie rating and review,
    rating = StringField("Your new rating", [validators.DataRequired()])
    review = StringField("Your Review", [validators.DataRequired()])
    submit = SubmitField("Update")
    # submit button


class AddForm(FlaskForm):
    # creates a from to add movie by title,
    title=StringField('Movie Title', [validators.DataRequired()])
    add_button=SubmitField("Add Movie")


app.config['SECRET_KEY'] = "secret"
# secret key to protect from csrf attack,

bootstrap=Bootstrap(app)


@app.route("/", methods=['POST','GET'])
def home():

    all_movies = Movie.query.order_by(Movie.rating).all()
    # list of all movies sorted by their rating,

    for i in range(len(all_movies)):
        # for each movie sorted by its rating value,

        all_movies[i].ranking=len(all_movies)-i
        # tap into its 'ranking' field, and change its ranking,

    db.session.commit()
    # save all changes,

    return render_template("index.html", movies=all_movies)
    # list of all rows of movies is passed,


@app.route('/edit/<movie_id>', methods=['POST','GET'])
def edit(movie_id):
    # on click, movie id is passed to this specific url path,

    form=EditForm()
    # create editing form object,

    if form.validate_on_submit():
        new_rate=form.rating.data
        new_review=form.review.data
        # if form is validate, hold both new rating and review,

        Movie.query.filter_by(id=movie_id).first().rating = new_rate
        db.session.commit()

        Movie.query.filter_by(id=movie_id).first().review=new_review
        db.session.commit()
        # update both rating and review of this book ,

        return redirect(url_for('home'))

    return render_template('edit.html', form=form)
    # if form is not validate, render edit.html page again,


@app.route('/delete/<movie_id>', methods=['POST','GEt'])
def delete(movie_id):
    # when user clicks on 'delete' button, get its movie id,

    db.session.delete(Movie.query.get(movie_id))
    db.session.commit()
    # delete that row from our db,

    return redirect(url_for('home'))
    # return updated homepage,


@app.route('/add', methods=['GET','POST'])
def add():
    form=AddForm()
    # create form object,

    if form.validate_on_submit():
        movie_title=form.title.data
        # get the movie title value user entered,
        try:
            # try to fetch all data first,
            response = requests.get(
                f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}").json()

            list_of_movies = response['results']
            print(len(list_of_movies))
            to_be_displayed = []

            for i in range(0, len(list_of_movies)):
                title = list_of_movies[i]['original_title']
                year = list_of_movies[i]['release_date']
                data = f"{title} - {year}"
                to_be_displayed.append(data)
        except :
            # if any issue in retrieving data, display message,
            return f" <h1 style='text-align:center; color:red'>Sorry, We Could not Find that Movie</h1>"
        else:
            # else if all went well, render select.html so that user chooses movie,
            return render_template('select.html', my_list=to_be_displayed)

    return render_template('add.html', form=form)


# @app.route('/select', methods=['POST','GET'])
# def select():
#     form=AddForm()
#
#     return render_template('select.html',form=form)


@app.route('/select/<int:selected_id>/<movie_title>', methods=['POST','GET'])
def move_movie(selected_id, movie_title):

    try:
        response = requests.get(
            f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={movie_title}").json()
        movie = response['results'][selected_id]

        my_movie_title = movie['original_title']
        my_movie_year = movie['release_date']
        my_movie_description = "Description"
        my_movie_review = movie['overview']
        my_movie_rating = movie['vote_average']
        my_movie_ranking = 1
        # now set to 1, later we gonna update u on home(),
        my_movie_image_url = f"https://image.tmdb.org/t/p/w500{movie['poster_path']}"

        my_new_movie = Movie(title=my_movie_title,
                             year=my_movie_year,
                             description=my_movie_review,
                             rating=my_movie_rating,
                             ranking=my_movie_ranking,
                             review=my_movie_description,
                             img_url=my_movie_image_url)

        db.session.add(my_new_movie)
        db.session.commit()
        # add new movie entry,
    except:
        return f" <h1 style='text-align:center; color:red'>Sorry,Something went wrong!</h1>"

    else:
        return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
