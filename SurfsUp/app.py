# Import the dependencies.
import numpy as np 
import pandas as pd
import datetime as dt 
import flask 
from flask import Flask, jsonify 
import sqlalchemy 
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session 
from sqlalchemy import create_engine, func, text, inspect 

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base  = automap_base()

# reflect the tables
Base.prepare(engine, reflect = True)

# Get all table names in database
#print(Base.classes.keys())

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# 1
#################################################
@app.route("/")
def welcome():
    return(
    f"Holiday Vacation in Honolulu, Hawaii!<br/>"
    f"Available Routes: <br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<start><br/>"
    f"/api/v1.0/<start>/<end>"
    )

#################################################
# 2
#################################################
@app.route("/api/v1.0/precipitation")
def precipitation():
    most_recent_date = session.query(func.max(Measurement.date)).scalar()
    #return most_recent_date
    
    # Convert 'most_recent_date' into datetime object
    most_recent_date = dt.datetime.strptime(str(most_recent_date),"%Y-%m-%d")

    # Find year ago date    
    year_ago_date = most_recent_date.date() - dt.timedelta(days = 365)
    #return year_ago_date

    
    precipitation_year_ago = session.query(Measurement.date, Measurement.prcp).\
                                    filter(Measurement.date>=year_ago_date).all()
    #return precipitation_year_ago

    # Convert precipitation_year_ago to dictionary
    precipitation_year_dict = [{"date" : date ,"precipitation" : prcp} for date,prcp in precipitation_year_ago]

    # Return JSON response
    return jsonify(precipitation_year_dict)

#print(precipitation())

#################################################
# 3
#################################################
@app.route("/api/v1.0/stations")
def station():
    # Query for stations from the dataset
    stations = session.query(Measurement.station).distinct().all()

    # Convert the result to a list
    station_list = [station[0] for station in stations]

    # Return JSON response
    return jsonify({"stations": station_list})

#################################################
# 4
#################################################
@app.route("/api/v1.0/tobs")
def active_station_tobs():
    # Query to find active station
    most_active_station = session.query(Measurement.station, func.count(Measurement.station)).\
                                        group_by(Measurement.station).\
                                        order_by(func.count(Measurement.station).desc()).\
                                        first()[0]
    
    # Find the most recent date for the most active station
    most_recent_date = session.query(func.max(Measurement.date)).\
                                     filter(Measurement.station == most_active_station).scalar()
    # Convert most recent date to datetime object
    most_recent_date = dt.datetime.strptime(str(most_recent_date),"%Y-%m-%d")
    # Find the year ago date from most recent date
    year_ago_date = most_recent_date - dt.timedelta(days=365)

    # Query the dates and temperature observations of the most-active station 
          #for the previous year of data. 
    
    temperature_observation = session.query(Measurement.date, Measurement.tobs).\
                              filter(Measurement.station == most_active_station).\
                              filter(Measurement.date >= year_ago_date).all()
    
    # Convert the result to a list of dictionaries
    tobs_data = [{"date": date, "temperature": tobs} for date, tobs in temperature_observation]

     # Return JSON response
    return jsonify(tobs_data)

#################################################
# 5 (part-1)
#################################################
@app.route("/api/v1.0/<start>")
def temperature_start(start):
     # Query for TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
    start_temperature = session.query(Measurement.date,func.min(Measurement.tobs),\
                                       func.avg(Measurement.tobs),func.max(Measurement.tobs)).\
                                       filter(Measurement.date >= start).group_by(Measurement.date).all()
   
    # Convert the result to a dictionary (result is list of tuple)
     
    temperature_data_list = []
    
    for result in start_temperature:
        temperature_data = {"date": result[0],
                            "TMIN": result[1],
                            "TAVG": result[2],
                            "TMAX": result[3]
                            }  
        temperature_data_list.append(temperature_data)          
    
    # Return JSON response 
    return jsonify(temperature_data_list)


#################################################
# 5 (part-2)
#################################################
@app.route("/api/v1.0/<start>/<end>")
def temperature_start_end(start,end):
#Query for a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates 
    #from the start date to the end date, inclusive.
    results = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), \
                            func.max(Measurement.tobs)).\
                            filter(Measurement.date >= start).filter(Measurement.date <= end).\
                            group_by(Measurement.date).all()

    # Convert the result to a dictionary
    temperature_start_end_list = []
    
    for result in results:
        temperature_data = {"date": result[0],
                            "TMIN": result[1],
                            "TAVG": result[2],
                            "TMAX": result[3]
                            }  
        temperature_start_end_list.append(temperature_data)          
    
    # Return JSON response
    return jsonify(temperature_start_end_list)

if __name__ == "__main__":
    app.run(debug = True)
