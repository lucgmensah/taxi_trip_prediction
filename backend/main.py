from fastapi import FastAPI, HTTPException
import pandas as pd
import uvicorn

from pydantic import BaseModel, conint

from db import create_connection, create_table, get_all_predictions, insert_prediction
from model import perform_predict

path_model = 'model/model.pkl'
db_path = 'data/database.db'
app = FastAPI()


# Creer la connexion a la base de donnees
conn = create_connection(db_path)
create_table(conn)


class TimeExpected(BaseModel):
    hour: conint(ge=0, le=23)  # Hour must be between 0 and 23
    abnormal_period: conint(ge=0, le=1)  # Accept 0 or 1
    weekday: conint(ge=0, le=6)  # Weekday must be between 0 and 6
    month: conint(ge=1, le=12)  # Month must be between 1 and 12
    prediction: float = None
    


@app.get("/")
def root():
    hour = 12
    abnormal_period = 1
    weekday = 3
    month = 12
    
    data = {
        'hour': hour,
        'abnormal_period': abnormal_period,
        'weekday': weekday,
        'month': month
    }
    prediction = perform_predict(pd.DataFrame([data]), path_model)
    
    return {"message": "Hello World", "prediction": prediction}    


@app.get("/predictions/")
async def get_predictions():
    predictions = get_all_predictions(conn)
    return {"predictions": predictions}


@app.post("/predict/")
async def predict_trip_duration(time: TimeExpected):
    try:
        prediction = perform_predict(pd.DataFrame([time.dict()]), path_model)
        
        # Save the prediction in the database
        insert_prediction(conn, time.hour, time.abnormal_period, time.weekday, time.month, prediction)
        
        return {"prediction": prediction, "data": time}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Prediction failed: {str(e)}")


if __name__ == '__main__':
    uvicorn.run("main:app", host="0.0.0.0",
                port=8000, reload=True)