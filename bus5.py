from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, String
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

app = FastAPI()

# Postgres connection details
DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'FinalBus'
DB_USER = 'postgres'
DB_PASSWORD = '310D60c9@'

# SQLAlchemy configuration
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Define database models


class TransportRegistration(Base):
    __tablename__ = 'transport_registration'

    userid = Column(String, primary_key=True)
    semstr_details_semester_sub_id = Column(String)


class BusQRScanLog(Base):
    __tablename__ = 'bus_qr_scan_log'

    id = Column(String, primary_key=True)
    log_userid = Column(String)
    semstr_details_semester_sub_id = Column(String)

# Define request body schema


class TransportRegistrationRequest(BaseModel):
    userid: str
    semstr_details_semester_sub_id: str

# Define route to handle incoming requests


@app.post('/TR')
def get_transport_registration(request: TransportRegistrationRequest):
    # Extract parameters from request body
    user_id = request.userid
    sem_sub_id = request.semstr_details_semester_sub_id

    # Create a session
    db = SessionLocal()

    try:
        # Query the database using SQLAlchemy ORM
        result = db.query(TransportRegistration).filter_by(
            userid=user_id, semstr_details_semester_sub_id=sem_sub_id).all()

        if len(result) > 0:
            # Convert result to list of dictionaries
            result_dict = [entry.__dict__ for entry in result]
            result_dict = [{k: v for k, v in entry.items() if not k.startswith('_')}
                           for entry in result_dict]

            return result_dict
        else:
            # Insert error details into bus_qr_scan_log table
            log_entry = BusQRScanLog(
                log_userid=user_id, semstr_details_semester_sub_id=sem_sub_id)
            db.add(log_entry)
            db.commit()

            raise HTTPException(
                status_code=404, detail='No records found for the given user id and semester subject id')

    except Exception as e:
        # Log error and raise HTTPException
        raise HTTPException(status_code=500, detail='Failed to execute query')

    finally:
        # Close the session
        db.close()
