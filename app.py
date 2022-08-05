#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from datetime import datetime
import re
from config import SQLALCHEMY_DATABASE_URI, app
from models import Venue, Artist, Show, db
# from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
# app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
# migrate = Migrate(app, db)
# TODO: connect to a local postgresql database
## Connected from config
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
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]
  # return render_template('pages/venues.html', areas=data);
  result_data = []
  cities = Venue.query.distinct()
  
  for x in cities:
       city_data = {
        "city":x.city,
        "state":x.state,
        "venues":[]
       }
       cities_list = Venue.query.filter_by(city=x.city).all()
       venue_in_city = []
       for y in cities_list:
          city_data['venues'].append({"id":y.id, "name":y.name,"num_upcoming_shows":0})
      # city_data.append(venue_in_city)
       result_data.append(city_data)
  return render_template('pages/venues.html', areas=result_data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  response={
    "count": 1,
    "data": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }
  search_text = '%{0}%'.format(request.form.get('search_term'))
  find_venue_name = Venue.query.filter(Venue.name.ilike(search_text)).all()
  find_venue_state = Venue.query.filter(Venue.state.ilike(search_text)).all()
  find_venue_city = Venue.query.filter(Venue.city.ilike(search_text)).all()

  counter = 0
  response_data = {
     "count": counter,
     "data": []
  }
  for venue_list in find_venue_name:
       counter = counter+1
       event = Show.query.filter(Show.venue_id==venue_list.id).count()
       response_data['count'] = counter
       response_data['data'].append({
              "id": venue_list.id,
              "name": venue_list.name,
              "num_upcoming_shows": event,
      })
  for venue_list in find_venue_state:
        counter = counter+1
        event = Show.query.filter(Show.venue_id==venue_list.id).count()

        response_data['count'] = counter
        response_data['data'].append({
              "id": venue_list.id,
              "name": venue_list.name,
              "num_upcoming_shows": event,
      })
  for venue_list in find_venue_city:
        counter = counter+1
        event = Show.query.filter(Show.venue_id==venue_list.id).count()
        response_data['count'] = counter
        response_data['data'].append({
              "id": venue_list.id,
              "name": venue_list.name,
              "num_upcoming_shows": event,
      })
  return render_template('pages/search_venues.html', results=response_data, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  data_db = Venue.query.get(venue_id)
  venue_detail = db.session.query(Show, Artist).select_from(Show).join(Artist).filter(Show.venue_id == venue_id and Show.artist_id == Artist.id).all()
  show_venue_result = {
          "id": "",
          "name": "",
          "genres": [],
          "address": "",
          "city": "",
          "state": "",
          "phone": "",
          "website": "",
          "facebook_link": "",
          "seeking_talent": False,
          "image_link": "",
          "past_shows": [],
          "upcoming_shows": [],
          "past_shows_count": 0,
          "upcoming_shows_count": 0,
  }
  show_venue_result['id'] = data_db.id
  show_venue_result['name'] = data_db.name
  show_venue_result['address'] = data_db.address
  show_venue_result['city'] = data_db.city
  show_venue_result['state'] = data_db.state
  show_venue_result['phone'] = data_db.phone
  show_venue_result['facebook_link'] = data_db.facebook_link
  show_venue_result['website'] = data_db.website_link
  show_venue_result['seeking_talent'] = data_db.looking_talent=='y'
  reg_x_pattern = r'[{}]'
  geners = (re.sub(reg_x_pattern, '', data_db.genres)).split(',')
  for gener in geners:
        show_venue_result['genres'].append(gener)
  for show, artist in venue_detail:
        date_time_record = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        if date_time_record<current_time:
          show_venue_result['past_shows_count'] = show_venue_result['past_shows_count']+1
          show_venue_result['past_shows'].append({
             "artist_id": show.artist_id,
             "artist_name": artist.name,
             "artist_image_link": artist.image_link,
              "start_time": show.start_time
            })

        else:
         show_venue_result['upcoming_shows_count'] = show_venue_result['upcoming_shows_count']+1
         show_venue_result['upcoming_shows'].append({
             "artist_id": show.artist_id,
            "artist_name": artist.name,
             "artist_image_link": artist.image_link,
            "start_time": show.start_time
           })

        
  return render_template('pages/show_venue.html', venue=show_venue_result)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    address = request.form['address']
    phone = request.form['phone']
    genres = request.form.getlist('genres')

    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    looking_talent = request.form.get('seeking_talent')
    seeking_description = request.form['seeking_description']
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link,website_link=website_link, looking_talent=looking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    flash('An error has occured ' + request.form['name'] + ' Data was not recorder!')
    form = VenueForm()
    return render_template('forms/new_venue.html', form=form)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return None

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  data=[{
    "id": 4,
    "name": "Guns N Petals",
  }, {
    "id": 5,
    "name": "Matt Quevedo",
  }, {
    "id": 6,
    "name": "The Wild Sax Band",
  }]
  # return render_template('pages/artists.html', artists=data)
  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  response={
    "count": 1,
    "data": [{
      "id": 4,
      "name": "Guns N Petals",
      "num_upcoming_shows": 0,
    }]
  }
  
  search_text = '%{0}%'.format(request.form.get('search_term'))
  find_artist_name = Artist.query.filter(Artist.name.ilike(search_text)).all()
  find_artist_state = Artist.query.filter(Artist.state.ilike(search_text)).all()
  find_artist_city = Artist.query.filter(Artist.city.ilike(search_text)).all()
  counter = 0
  response_data = {
     "count": counter,
     "data": []
  }
  for artist_list in find_artist_name:
       counter = counter+1
       event = Show.query.filter(Show.artist_id==artist_list.id).count()
       response_data['count'] = counter
       response_data['data'].append({
              "id": artist_list.id,
              "name": artist_list.name,
              "num_upcoming_shows": event,
      })
  for artist_list in find_artist_state:
        counter = counter+1
        event = Show.query.filter(Show.artist_id==artist_list.id).count()
        response_data['count'] = counter
        response_data['data'].append({
              "id": artist_list.id,
              "name": artist_list.name,
              "num_upcoming_shows": event,
      })
  for artist_list in find_artist_city:
        counter = counter+1
        event = Show.query.filter(Show.artist_id==artist_list.id).count()
        response_data['count'] = counter
        response_data['data'].append({
              "id": artist_list.id,
              "name": artist_list.name,
              "num_upcoming_shows": event,
      })
  return render_template('pages/search_artists.html', results=response_data, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  show_artist_result = {
    "id": "",
    "name": "",
    "genres": [],
    "city": "",
    "state": "",
    "phone": "",
    "seeking_venue": False,
    "image_link": "",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data_db= Artist.query.get(artist_id)
  artist_detail = db.session.query(Show, Venue).select_from(Show).join(Venue).filter(Show.artist_id == artist_id and Show.venue_id == Venue.id).all()


  show_artist_result['id'] = data_db.id
  show_artist_result['name'] = data_db.name
  show_artist_result['city'] = data_db.city
  show_artist_result['state'] = data_db.state
  show_artist_result['phone'] = data_db.phone
  show_artist_result['image_link'] = data_db.image_link
  #show_artist_result['genres'].append(data_db.genres)
  show_artist_result['seeking_talent'] = data_db.looking_venue=='y'
  #show_artist_result['genres'].append(data_db.genres)
  reg_x_pattern = r'[{}]'
  geners = (re.sub(reg_x_pattern, '', data_db.genres)).split(',')
  for gener in geners:
        show_artist_result['genres'].append(gener)

  for show, venue in artist_detail:
        date_time_record = datetime.strptime(show.start_time, '%Y-%m-%d %H:%M:%S')
        current_time = datetime.now()
        if date_time_record<current_time:
         show_artist_result['past_shows_count'] = show_artist_result['past_shows_count']+1
         show_artist_result['past_shows'].append({
        "venue_id": show.venue_id,
        "venue_name": venue.name,
        "venue_image_link": venue.image_link,
        "start_time": show.start_time
            })
        else:
          show_artist_result['upcoming_shows_count'] = show_artist_result['upcoming_shows_count']+1
          show_artist_result['upcoming_shows'].append({
            "venue_id": show.venue_id,
            "venue_name": venue.name,
            "venue_image_link": venue.image_link,
            "start_time": show.start_time
           })
        
  return render_template('pages/show_artist.html', artist=show_artist_result)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80"
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_detail = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist_detail)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  artist_detail = Artist.query.get(artist_id)
  if len(request.form['name'])>0:
        artist_detail.name = request.form['name']
  if len(request.form['city'])>0:
    artist_detail.city = request.form['city']
  if len(request.form['state'])>0:
    artist_detail.state = request.form['state']
  # address = request.form['address']
  if len(request.form['phone'])>0:
    artist_detail.phone = request.form['phone']
  if len(request.form['genres'])>0:
    artist_detail.genres = request.form['genres']
  if len(request.form['image_link'])>0:
    artist_detail.image_link = request.form['image_link']
  if len(request.form['facebook_link'])>0:
    artist_detail.facebook_link = request.form['facebook_link']
  if len(request.form['website_link'])>0:
    artist_detail.website_link = request.form['website_link']
  #if len(request.form['looking_venue'])>0:
  artist_detail.looking_venue = request.form.get('seeking_venue')
  if len(request.form['seeking_description'])>0:
    artist_detail.seeking_description = request.form['seeking_description']
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60"
  }
  # TODO: populate form with values from venue with ID <venue_id>
  venue_detail = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue_detail)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  venue_detail = Venue.query.get(venue_id)
  if len(request.form['name'])>0:
    venue_detail.name = request.form['name']
  if len(request.form['city'])>0:
    venue_detail.city = request.form['city']
  if len(request.form['state'])>0:
    venue_detail.state = request.form['state']
  if len(request.form['address'])>0:
    venue_detail.address = request.form['address']
  if len(request.form['phone'])>0:
    venue_detail.phone = request.form['phone']
  if len(request.form['genres'])>0:
    venue_detail.genres = request.form['genres']
  if len(request.form['image_link'])>0:
    venue_detail.image_link = request.form['image_link']
  if len(request.form['facebook_link'])>0:
    venue_detail.facebook_link = request.form['facebook_link']
  if len(request.form['website_link'])>0:
    venue_detail.website_link = request.form['website_link']
  #if len(request.form['seeking_description'])>0:
  venue_detail.looking_talent = request.form.get('seeking_talent')
  if len(request.form['seeking_description'])>0:
    venue_detail.seeking_description = request.form['seeking_description']

  db.session.commit()

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
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    # address = request.form['address']
    phone = request.form['phone']
  # genres = request.form['genres']
    genres = request.form.getlist('genres')

    image_link = request.form['image_link']
    facebook_link = request.form['facebook_link']
    website_link = request.form['website_link']
    looking_venue = request.form.get('seeking_venue')
    seeking_description = request.form['seeking_description']
    artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link,website_link=website_link, looking_venue=looking_venue, seeking_description=seeking_description)
    db.session.add(artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except:
    flash(' An error occured' + request.form['name'] + ' Data was not recorder!')
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  # show_detail = db.session.query(Artist, Show, Venue).join(Show).filter(Artist.id == Show.artist_id).join(Venue).filter(Venue.id == Show.venue_name).all()

  joind_shows = db.session.query(Artist,Show, Venue).select_from(Artist).join(Show, isouter=True).join(Venue, isouter=True).filter(Artist.id == Show.artist_id and Venue.id == Show.venue_id).all()
  show_result = []
  for artist, show, venue in joind_shows:
        show_result.append({
          "venue_id": venue.id,
          "venue_name": venue.name,
          "artist_id": artist.id,
          "artist_name": artist.name,
          "artist_image_link": artist.image_link,
          "start_time": show.start_time
        })
     
  return render_template('pages/shows.html', shows=show_result)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = datetime.strptime(request.form['start_time'], '%Y-%m-%d %H:%M:%S')
    #start_time = request.form['start_time']
    show_record = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show_record)
    db.session.commit()
    flash('Show was successfully listed!')
  except:
    flash('An error has occured. data was not recorded. make sure, Artist ID is existed, Venue ID is existed and start date time is in a correct format')
    form = ShowForm()
    return render_template('forms/new_show.html', form=form)

  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
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
