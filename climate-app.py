import numpy as np
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlaclhemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify

#Setup
engine = create_engine("sqlite:///./Resources/hawaii.sqlite")

Base = automap_base()

Base.prepare(engine, reflect = True)

#References
Measurement = Base.classes.measurement
Station = Base.classes.station

#Flask Setup and Routes
app = Flask(__name__)

@app.route("/")
def welcome():
    return (
         f"Welcome! <br/>"
         f"Available Routes: <br/>"
         f"/api/v1.0/precipitation<br/>"  
         f"/api/v1.0/stations<br/>"  
         f"/api/v1.0/tobs<br/>"  
         f"/api/v1.0/<start><br/>"
         f"/api/v1.0/<start>/<end>"    
    )

#Convert the query results to a dictionary using date as the key and prcp as the value.
#Return the JSON representation of your dictionary.
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).all()
    session.close()
    #Append Dictionary.
    all_measurement = []
    for date, prcp in results:
        measurement_dict = {}
        measurement_dict["date"] = date
        measurement_dict["prcp"] = prcp
        all_measurement.append(measurement_dict)

        return jsonify(all_measurement)

#Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    results = session.query(Station.name).all()
    session.close()
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

#Query the dates and temperature observations of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) for the previous year.
@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.station == 'USC00519281').filter(Measurement.date >= '2016-08-23').all()

    session.close()
    lastyear_tobs = list(np.ravel(results))

    return jsonify(lastyear_tobs)

#Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
#When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start(startdate):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= startdate).all()

    session.close()
    start_date = list(np.ravel(results))
    
    return jsonify(start_date)

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
@app.route("/api/v1.0/<start>/<end>")
def start_end(startdate, enddate):
    session = Session(engine)
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= startdate).filter(Measurement.date <= enddate).all()

    session.close()
    startend_date = list(np.ravel(results))
    
    return jsonify(startend_date)

if __name__ == '__main__':
    app.run(debug=True)