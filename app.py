import streamlit as st

from app_pages.multi_page import Multipage
from app_pages.hotels_page import page_hotels_body
from app_pages.activities_page import page_activities_body
from app_pages.housing_page import page_housing_body

app = Multipage("Decision Decipherer")

app.add_page("Housing", page_housing_body)
app.add_page("Vacation Homes / Hotels / Airbnb", page_hotels_body)
app.add_page("Activities", page_activities_body)

app.run()