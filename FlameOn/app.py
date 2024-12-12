# Import the dependencies.
from flask import Flask, jsonify
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine
from sqlalchemy import func
import datetime as dt
import numpy as np

#################################################
# Database Setup
#################################################

# Create engine using the `hawaii.sqlite` database file
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# Declare a Base using `automap_base()`
Base = automap_base()

# Use the Base class to reflect the database tables
Base.prepare(autoload_with=engine)

# Assign the measurement class to a variable called `Measurement` and
# the station class to a variable called `Station`
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
@app.route("/")
def home():
    return (
        "Welcome to THE BEST Hawaii Climate API Around.<br/>"
        "Available Routes:<br/>"
        "<strong>/api/v1.0/precipitation</strong> ==  Returns last 12 months of precipitation data<br/>"
        "<strong>/api/v1.0/stations</strong>      ==  Returns list of stations included in dataset<br/>"
        "<strong>/api/v1.0/tobs</strong>          ==  Returns all temperature data from most active station<br/>"
        "For min/avg/max temperature data of specific time periods, use the following links. <strong>format for dates: yyyy-mm-dd</strong><br/>"
        "<strong>/api/v1.0/start_date</strong><br/>"
        "<strong>/api/v1.0/start_date/end_date</strong>"
    )

@app.route("/api/v1.0/precipitation")
def precip():
    """Returns past 12 months of precipitation data"""
    # Create a session
    session = Session(engine)

    # Query date/precipitation data from 1 year to most recent measurement
    rain_date = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= "2016-08-23").\
        filter(Measurement.prcp != 'None').all()
    
    # Close Session
    session.close()

    # Create empty list for appending queried data
    rain_list = []
    
    # Append list with queried data in dictionary format
    for date, prcp in rain_date:
        prcp_dict = {}
        prcp_dict[date] = prcp
        rain_list.append(prcp_dict)
    
    # Return jsonified list of dictionaries from past 12 months of precip data
    return jsonify(rain_list)

@app.route("/api/v1.0/stations")
def stations():
    """Returns list of stations from dataset"""
    # Create a session
    session = Session(engine)

    # Query stations from session
    stat_data = session.query(Station.station).all()

    # Close Session
    session.close()

    # Convert from tuples to list
    station_list = list(np.ravel(stat_data))

    # Return jsonified list of stations
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    """Returns dates and temperatures of most-active station for last 12 months"""
    # Create a session
    session = Session(engine)    

    # Query tobs
    tobs_data = session.query(Measurement.date, Measurement.tobs).\
        filter(Measurement.station == "USC00519281").\
        filter(Measurement.date >= "2016-08-23").\
        order_by(Measurement.date).all()

    # Close Session
    session.close()
    
    # Convert query data to list of dictionaries
    tobs_list = []
    for date, tob in tobs_data:
        tobs_dict = {}
        tobs_dict[date] = tob
        tobs_list.append(tobs_dict)

    # Return jsonified tobs list
    return jsonify(tobs_list)

@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def startsearch(start=None, end=None):
    """Returns min/avg/max temperature from specified start time until the most recent time, or until provided end time"""
    # Create a session
    session = Session(engine)

    # Set variable for querying min/avg/max tobs data
    sel = [func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)]

    # Check end date
    if end == None:

        # Query from start date to most recent date
        start_time_data = session.query(*sel).\
                        filter(Measurement.date >= start).all()
        
        # Close Session
        session.close()

        # Convert Query to list
        start_time_list = list(np.ravel(start_time_data))

        # Return jsonified list
        return jsonify(start_time_list)
    
    # Else statement for inclusion of end date
    else:

        # Query from start date to end date
        start_end_data = session.query(*sel).\
                        filter(Measurement.date >= start).\
                        filter(Measurement.date <= end).all()
        # Close Session
        session.close()

        # Convert Query to list
        start_end_list = list(np.ravel(start_end_data))

        # Return jsonified list
        return jsonify(start_end_list)

# Activate debug
if __name__ == "__main__":
    app.run(debug=True)