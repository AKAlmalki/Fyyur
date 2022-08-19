#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

from ctypes import sizeof
import json
from urllib import response
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify,abort
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from flask_migrate import Migrate
import sys
from datetime import date
from models import db, Artist, Venue, Show
from jinja2.utils import markupsafe

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

# the toolbar is only enabled in debug mode:
app.debug = True

# set a 'SECRET_KEY' to enable the Flask session cookies
app.config['SECRET_KEY'] = '<replace with a secret key>'

markupsafe.Markup()


# Flask-Migrate [done]
migrate = Migrate(app, db)

# TODO: connect to a local postgresql database [done but with the password abc in the config.py]

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data. [done]
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.

  # to store info about venues per each state and city
  data = []

  venues = db.session.query(Venue.state, Venue.city).distinct().order_by(Venue.state).all()
  # print(venues)
  
  # loop to get the information for the venues per state and city.
  for venue in venues:

    # all_venues will store all venues with different city and state.
    all_venues = Venue.query.filter_by(state=venue.state, city=venue.city).all()

    # to store info about the venues
    data2 = [] 

    for venue_info in all_venues: # loop for counting the num_upcoming_shows and other info for each venue
      
      # calculating the upcoming shows [using join]
      num_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_info.id).filter(Show.start_time > datetime.now()).count()

      # storing venue info on data2 variable
      data2.extend([{
        "id": venue_info.id,
        "name": venue_info.name,
        "num_upcoming_shows": num_upcoming_shows,
      }])
    
    data.extend([{
      "city": venue.city,
      "state": venue.state,
      "venues": data2
    }])

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive. [done]
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # Note: ilike: is not case-insensitive,
  # like: is case-sensitive

  # get the name that the user want to search for
  search = request.form.get('search_term', '')

  # to store information about venue
  data = []

  # query to search partially for venues based on the name
  venues = Venue.query.filter(Venue.name.ilike("%" + search + "%")).all()

  for venue in venues:

    # calculating the upcoming shows [using join]
    num_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue.id).filter(Show.start_time > datetime.now()).count()

    data.append({
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': num_upcoming_shows,
    })

  # fill out the reponse and send it back to the user
  response={
    "count": len(data),
    "data": data
  }

  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id [done]
  # TODO: replace with real venue data from the venues table, using venue_id

  # to store info about venue
  data = []
  data2 = []
  data3 = []

  # to store info about the shows
  past_shows = []
  upcoming_shows = []

  # get all venues with value equal to 'venue_id' variable
  venues = Venue.query.filter_by(id=venue_id).all()

  # get all the past shows [using join]
  past_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()

  # get all the upcoming shows [using join]
  upcoming_shows = db.session.query(Show).join(Venue).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()

  for show in past_shows:
    # storing past_shows info on data2 variable
    data2.extend([{
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
    }])

  for show in upcoming_shows:
    # storing past_shows info on data3 variable
    data3.extend([{
      "artist_id": show.artist_id,
      "artist_name": Artist.query.get(show.artist_id).name,
      "artist_image_link": Artist.query.get(show.artist_id).image_link,
      "start_time": str(show.start_time)
    }])
      
  
  # loop to get the information for each venue
  for venue in venues:

    data.extend([{
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres.replace('{','').replace('}','').replace("\"","").split(','),
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.is_seeking_talent,
      "seeking_description": venue.seeking_talent_desc,
      "image_link": venue.image_link,
      "past_shows": data2,
      "upcoming_shows": data3,
      "past_shows_count": len(data2),
      "upcoming_shows_count": len(data3),
    }])

  data = list(filter(lambda d: d['id'] == venue_id, data))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead [done]
  # TODO: modify data to be the data object returned from db insertion [done]

  form = VenueForm(request.form)
  error = False

  if form.validate():

    try:

      venue = Venue(
        name=form.name.data, 
        city=form.city.data, 
        state=form.state.data, 
        address=form.address.data, 
        phone=form.phone.data, 
        genres=form.genres.data, 
        facebook_link=form.facebook_link.data, 
        image_link=form.image_link.data, 
        website_link=form.website_link.data, 
        seeking_talent_desc=form.seeking_description.data, 
        is_seeking_talent=form.seeking_talent.data
      )

      # Check if the phone number format is valid or not.
      if not is_valid_phone(form.phone.data):
        flash('Phone number is not valid! try a valid one.')
        raise TypeError('Not Valid Phone Number! Check the phone number you entered.')
        
      db.session.add(venue)
      db.session.commit()

      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    
    except:
      error = True

      # TODO: on unsuccessful db insert, flash an error instead. [done]
      # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
      # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
      flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
      print(sys.exc_info())
      db.session.rollback()
      
    finally:
      db.session.close()

    if error:
      abort(500)
    else:
      return render_template('pages/home.html')

  else:

    flash('Errors: Invalid phone number!')
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using [done]
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  error = False
  
  try:

    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
    flash("Venue " + Venue.query.get(venue_id).name + " was successfully deleted!")
  except:

    error = True
    print(sys.exc_info())
    db.session.rollback()
    flash("An error occured. A venue with the id " + str(venue_id) + " couldn't be deleted.")

  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('pages/home.html'))

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database [done]
  data = []
  artists = Artist.query.order_by(Artist.id).all()

  for artist in artists:
    data.extend([{
      "id": artist.id,
      "name": artist.name
    }])

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.[done]
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # Note: ilike: is not case-insensitive,
  # like: is case-sensitive

  # get the name that the user want to search for
  search = request.form.get('search_term', '')

  # to store information about artist
  data = []

  # query to search partially for artists based on the name
  aritsts = Artist.query.filter(Artist.name.ilike("%" + search + "%")).all()

  for artist in aritsts:

    # calculating the upcoming shows [using join]
    num_upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist.id).filter(Show.start_time > datetime.now()).count()

    # print('num:\t\t', num_upcoming_shows)

    data.append({
      'id': artist.id,
      'name': artist.name,
      'num_upcoming_shows': num_upcoming_shows,
    })

  # fill out the reponse and send it back to the user
  response={
    "count": len(data),
    "data": data
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id [done]
  # TODO: replace with real artist data from the artist table, using artist_id

  # to store info about venue
  data = []
  data2 = []
  data3 = []

  # to store info about the shows
  past_shows = []
  upcoming_shows = []

  # get all artist with value equal to 'venue_id' variable
  artists = Artist.query.filter_by(id=artist_id).all()

  # get all the past shows [using join]
  past_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time < datetime.now()).all()

  # get all the upcoming shows [using join]
  upcoming_shows = db.session.query(Show).join(Artist).filter(Show.artist_id==artist_id).filter(Show.start_time > datetime.now()).all()

  for show in past_shows:
    # storing past_shows info on data2 variable
    data2.extend([{
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "venue_image_link": Venue.query.get(show.venue_id).image_link,
      "start_time": str(show.start_time)
    }])

  for show in upcoming_shows:
    # storing past_shows info on data3 variable
    data3.extend([{
      "venue_id": show.venue_id,
      "venue_name": Venue.query.get(show.venue_id).name,
      "venue_image_link": Venue.query.get(show.venue_id).image_link,
      "start_time": str(show.start_time)
    }])
      
  
  # loop to get the information for each venue
  for artist in artists:

    data.extend([{
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres.replace('{','').replace('}','').replace("\"","").split(','),
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.is_seeking_venues,
      "seeking_description": artist.seeking_venues_desc,
      "image_link": artist.image_link,
      "past_shows": data2,
      "upcoming_shows": data3,
      "past_shows_count": len(data2),
      "upcoming_shows_count": len(data3),
    }])

  data = list(filter(lambda d: d['id'] == artist_id, data))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  data = Artist.query.get(artist_id)

  artist={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_venue": data.is_seeking_venues,
    "seeking_description": data.seeking_venues_desc,
    "image_link": data.image_link
  }

  # TODO: populate form with fields from artist with ID <artist_id> [done]
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes [done]
  
  artist_num = str(artist_id)
  error = False

  # get the form from the request (to get the data after it have been edited by the user)
  form = ArtistForm(request.form)

  # get the artist that the user want to edit
  artist = Artist.query.get(artist_id)

  try:

    # pass the data
    artist.name = form.name.data
    artist.genres = form.genres.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.website = form.website_link.data
    artist.facebook_link = form.facebook_link.data
    artist.image_link = form.image_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('An artist with the id ' + artist_num + ' have been edited successfully!')

  except:
    
    error = True
    print(sys.exc_info())
    db.session.rollback()
    flash("An error occured. An artist with the id " + artist_num + " couldn't edit its information!")

  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()

  data = Venue.query.get(venue_id)

  venue={
    "id": data.id,
    "name": data.name,
    "genres": data.genres,
    "address": data.address,
    "city": data.city,
    "state": data.state,
    "phone": data.phone,
    "website": data.website_link,
    "facebook_link": data.facebook_link,
    "seeking_talent": data.is_seeking_talent,
    "seeking_description": data.seeking_talent_desc,
    "image_link": data.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id> [done]
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes [done]
  venue_num = str(venue_id)
  error = False

  # get the form from the request (to get the data after it have been edited by the user)
  form = VenueForm(request.form)

  # get the venue that the user want to edit
  venue = Venue.query.get(venue_id)

  try:

    # pass the data
    venue.name = form.name.data
    venue.genres = form.genres.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.website = form.website_link.data
    venue.facebook_link = form.facebook_link.data
    venue.image_link = form.image_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data

    db.session.commit()
    flash('A venue with the id ' + venue_num + ' have been edited successfully!')
  except:
    
    error = True
    print(sys.exc_info())
    db.session.rollback()
    flash("An error occured. A venue with the id " + venue_num + " couldn't edit its information!")

  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead [done]
  # TODO: modify data to be the data object returned from db insertion [done]

  form = ArtistForm(request.form)
  error = False

  if form.validate():

    try:

      new_artist = Artist(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data, 
        phone=form.phone.data, 
        genres=form.genres.data, 
        facebook_link=form.facebook_link.data, 
        image_link=form.image_link.data, 
        website_link=form.website_link.data, 
        seeking_venues_desc=form.seeking_description.data, 
        is_seeking_venues=form.seeking_venue.data
      )

      # Check if the phone number format is valid or not.
      if not is_valid_phone(form.phone.data):
        flash('Phone number is not valid! try a valid one.')
        raise TypeError('Not Valid Phone Number! Check the phone number you entered.')

      db.session.add(new_artist)
      db.session.commit()

      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    
    except:
      error = True

      # TODO: on unsuccessful db insert, flash an error instead. [done]
      # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
      flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
      db.session.rollback()
    
    finally:
      db.session.close()

    if error:
      abort(500)
    else:
      return render_template('pages/home.html')

  else:

    flash('Errors: Invalid phone number!')
    return render_template('pages/home.html')

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data. [done]

  data = []
  shows = Show.query.all()

  for show in shows:
    
    venue = Venue.query.get(show.venue_id)
    artist = Artist.query.get(show.artist_id)
    
    data.extend([{
      "venue_id": venue.id,
      "venue_name": venue.name,
      "artist_id": artist.id,
      "aritst_name": artist.name,
      "artist_image_link": artist.image_link,
      "start_time": str(show.start_time)
    }])

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead [done]

  form = ShowForm(request.form)
  error = False

  try:

    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
   
    db.session.add(show)
    db.session.commit()

    # on successful db insert, flash success [done]
    flash('Show was successfully listed!')

  except:
    error = True
    print(sys.exc_info())

    # TODO: on unsuccessful db insert, flash an error instead. [done]
    # e.g., flash('An error occurred. Show could not be listed.')
    # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    
    flash('An error occurred. Show could not be listed.')

    db.session.rollback()

  finally:
    db.session.close()

  if error:
    abort(500)
  else:
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
