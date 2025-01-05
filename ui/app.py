from typing import Dict

import streamlit as st
import requests as rq


endpoint = "http://localhost:8000/predict/"

def predict_trip_duration(data: Dict[str, int]) -> int:
    response = rq.post(endpoint, json=data)
    response.raise_for_status()
    return response.json()["prediction"]

def body():
    image = "🚢"
    st.set_page_config(
        layout="wide",
        initial_sidebar_state="auto",
        page_title="NYC Taxi Trip Duration",
        page_icon=image,
    )
    
    st.title("NYC Taxi Trip Duration")
    st.write(
        "Base sur la date et l'heure de prise en charge, le jour de la semaine, le mois et la période anormale, "
    )
    
    
    prediction = None
    # Form
    with st.form(key="my_form"):
        
        row1 = st.columns([1, 1, 1, 1, 1])
        hour = row1[1].number_input("Hour", 0, 23, 12)
        weekday = row1[2].number_input("Weekday", 0, 6, 3)
        month = row1[3].number_input("Month", 1, 12, 12)
        
        row2 = st.columns([1, 1, 1, 1, 1])
        abnormal_period = row2[2].selectbox("Abnormal period", [0, 1])
        
        row3 = st.columns([1])
        submit_button = row3[0].form_submit_button(label="Predict")
        
        if submit_button:
            data = {
                "hour": hour,
                "abnormal_period": abnormal_period,
                "weekday": weekday,
                "month": month,
            }
            # Contact backend by API
            prediction = round(predict_trip_duration(data)/60, 1)
    
    if prediction:
        st.subheader(f"Le trajet va durer environ {prediction} minutes.", divider=True)
    else:
        st.subheader("Veuillez renseigner les informations pour obtenir une prédiction.", divider=True)
            

if __name__ == "__main__":
    body()