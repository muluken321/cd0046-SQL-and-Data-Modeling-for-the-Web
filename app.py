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
from flask_wtf import FlaskForm as Form
from forms import *
from datetime import datetime
import re
from flask_migrate import Migrate
from models import Venue, Artist, Show, db
# from flask_migrate import Migrate
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#
# app = Flask(__name__)
app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)  # Just initiate it here.
migrate = Migrate(app, db)
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
  show_venue_result['image_link'] = data_db.image_link
  show_venue_result['website'] = data_db.website_link
  show_venue_result['seeking_description'] = data_db.seeking_description

  show_venue_result['seeking_talent'] = str(data_db.looking_talent).lower() in ['true', '1', 't', 'y', 'yes']


  for gener in data_db.genres:
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
  form = VenueForm(request.form)
  try:
    name = form.name.data
    city = form.city.data
    state = form.state.data
    address = form.address.data
    phone = form.phone.data
    genres = form.genres.data

    image_link = form.image_link.data
    facebook_link = form.facebook_link.data
    website_link = form.website_link.data
    looking_talent = form.seeking_talent.data
    seeking_description = form.seeking_description.data
    venue = Venue(name=name, city=city, state=state, address=address, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link,website_link=website_link, looking_talent=looking_talent, seeking_description=seeking_description)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + form.name.data + ' was successfully listed!')
  except:
    flash('An error has occured ' + form.name.data + ' Data was not recorder!')
    
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
 
  # data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  show_artist_result = {
    "id": "",
    "name": "",
    "genres": [],
    "city": "",
    "state": "",
    "phone": "",
    "seeking_venue": False,
    "website": "",
    "facebook_link": "",
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
  show_artist_result['website'] = data_db.website_link
  show_artist_result['facebook_link'] = data_db.facebook_link

  show_artist_result['seeking_description'] = data_db.seeking_description
  #show_artist_result['genres'].append(data_db.genres)
  show_artist_result['seeking_venue'] = str(data_db.looking_venue).lower() in ['true', '1', 't', 'y', 'yes']
  #show_artist_result['genres'].append(data_db.genres)
  for gener in data_db.genres:
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
 
  # TODO: populate form with fields from artist with ID <artist_id>
  artist_detail = Artist.query.get(artist_id)
  return render_template('forms/edit_artist.html', form=form, artist=artist_detail)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  form = ArtistForm(request.form)
  artist_detail = Artist.query.get(artist_id)
  if len(form.name.data)>0:
        artist_detail.name = form.name.data
  if len(form.city.data)>0:
    artist_detail.city = form.city.data
  if len(form.state.data)>0:
    artist_detail.state = form.state.data
  # address = form.address']
  if len(form.phone.data)>0:
    artist_detail.phone = form.phone.data
  if len(form.genres.data)>0:
    artist_detail.genres = form.genres.data
  if len(form.image_link.data)>0:
    artist_detail.image_link = form.image_link.data
  if len(form.facebook_link.data)>0:
    artist_detail.facebook_link = form.facebook_link.data
  if len(form.website_link.data)>0:
    artist_detail.website_link = form.website_link.data
  #if len(form.looking_venue.data)>0:
  artist_detail.looking_venue = form.seeking_venue.data
  if len(form.seeking_description.data)>0:
    artist_detail.seeking_description = form.seeking_description.data
  db.session.commit()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  # TODO: populate form with values from venue with ID <venue_id>
  venue_detail = Venue.query.get(venue_id)
  return render_template('forms/edit_venue.html', form=form, venue=venue_detail)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  venue_detail = Venue.query.get(venue_id)
  if len(form.name.data)>0:
    venue_detail.name = form.name.data
  if len(form.city.data)>0:
    venue_detail.city = form.city.data
  if len(form.state.data)>0:
    venue_detail.state = form.state.data
  if len(form.address.data)>0:
    venue_detail.address = form.address.data
  if len(form.phone.data)>0:
    venue_detail.phone = form.phone.data
  if len(form.genres.data)>0:
    venue_detail.genres = form.genres.data
  if len(form.image_link.data)>0:
    venue_detail.image_link = form.image_link.data
  if len(form.facebook_link.data)>0:
    venue_detail.facebook_link = form.facebook_link.data
  if len(form.website_link.data)>0:
    venue_detail.website_link = form.website_link.data
  #if len(form.seeking_description.data)>0:
  venue_detail.looking_talent = form.seeking_talent.data
  if len(form.seeking_description.data)>0:
    venue_detail.seeking_description = form.seeking_description.data

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
  form = ArtistForm(request.form)
  if form.validate_on_submit():
    try:
      name = form.name.data
      city = form.city.data
      state = form.state.data
      # address = form.address.data
      phone = form.phone.data
    # genres = form.genres.data
      genres = form.genres.data

      image_link = form.image_link.data
      facebook_link = form.facebook_link.data
      website_link = form.website_link.data
      looking_venue = form.seeking_venue.data
      seeking_description = form.seeking_description.data
      artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, image_link=image_link, facebook_link=facebook_link,website_link=website_link, looking_venue=looking_venue, seeking_description=seeking_description)
      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + form.name.data + ' was successfully listed!')
    except:
      flash(' An error occured' + form.name.data + ' Data was not recorder!')
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
  form = ShowForm(request.form)

  try:
    artist_id = form.artist_id.data
    venue_id = form.venue_id.data
    start_time = datetime.strptime(str(form.start_time.data), '%Y-%m-%d %H:%M:%S')
    #start_time = request.form.start_time.data
    show_record = Show(artist_id=artist_id, venue_id=venue_id, start_time=start_time)
    db.session.add(show_record)
    db.session.commit()
    artist_id
    flash('Show was successfully listed!')
    
  except:
    flash('An error has occured. data was not recorded. make sure, Artist ID is existed, Venue ID is existed and start date time is in a correct format')
  return render_template('pages/home.html')

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
