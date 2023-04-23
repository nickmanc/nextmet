import os
import logging

import pytz
import streamlit as st
import json
from datetime import datetime
from streamlit_autorefresh import st_autorefresh
from streamlit_cookies_manager import CookieManager

from metrolink_lines import get_metrolink_line_status
from trams import get_tram_departures

SELECTED_MORNING_TRAM_STOP_KEY = "selected_morning_tram_stop"

SELECTED_AFTERNOON_TRAM_STOP_KEY = "selected_afternoon_tram_stop"

NEXTMET_DATA_KEY = "nm-data-v0.0.1"


def get_value_from_cookie_or_default(key, default):
    if NEXTMET_DATA_KEY not in cookies or cookies[NEXTMET_DATA_KEY] is None:
        return default
    cookie = json.loads(cookies[NEXTMET_DATA_KEY])
    if key not in cookie:
        return default
    else:
        return cookie[key]


def save_user_settings():
    cookies[NEXTMET_DATA_KEY] = json.dumps(
        {
            SELECTED_MORNING_TRAM_STOP_KEY: st.session_state.morning_stop,
            SELECTED_AFTERNOON_TRAM_STOP_KEY: st.session_state.afternoon_stop
        })
    cookies.save()


def renew_cookie():
    if ('renewed_cookie' not in st.session_state):
        logging.info("Renewing cookie")
        cookies.save()
        st.session_state['renewed_cookie'] = True


@st.cache_data
def get_tram_stations():
    with open("resources/tram_stop.json", "r") as test_data_file:
        station_map = json.load(test_data_file)
        return station_map


NO_TRAM_SCHEDULED_MESSAGE = "No trams currently scheduled to depart."
tz = pytz.timezone('Europe/London')
current_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)

tz = pytz.timezone('Europe/London')
current_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)

st.set_page_config(layout="wide")
cookies = CookieManager(  # TODO - switch to encrypted cookies
    prefix="www.nextmet.co.uk"
    # You should really setup a long cookies_password secret if you're running on Streamlit Cloud.
    # password=os.environ.get("cookies_password", "default password")
)
if not cookies.ready():
    # Wait for the component to load and send us current cookies.
    st.stop()

st.markdown(
    f"""
        <style>
            .appview-container .main .block-container {{
                padding-top: {0}rem;
                padding-bottom: {1}rem;
                }}
        </style>""",
    unsafe_allow_html=True,
)

# st_autorefresh(interval=60 * 1000)
st_autorefresh(interval=15 * 1000)


selected_morning_tram_stop_name = get_value_from_cookie_or_default(SELECTED_MORNING_TRAM_STOP_KEY, 'Trafford Bar')
selected_afternoon_tram_stop_name = get_value_from_cookie_or_default(SELECTED_AFTERNOON_TRAM_STOP_KEY, 'Stretford')
tram_stops = get_tram_stations()


def from_schedule():
    from_container = st.container()
    # Display tram information in a table
    morning_tram_stop_ids = tram_stops[selected_morning_tram_stop_name]["location_ids"]
    from_container.subheader(
        f"[{selected_morning_tram_stop_name}](https://tfgm.com{tram_stops[selected_morning_tram_stop_name]['href']})")
    tram_departure_info = get_tram_departures(morning_tram_stop_ids)
    trams = tram_departure_info[0]
    if len(trams) > 0:
        for tram in trams:
            if tram['expected'] == 0:
                tram_expected_text = "NOW"
            else:
                tram_expected_text = f"in **{tram['expected']}** minutes."
            from_container.markdown(f"**{tram['destination']}**  ({tram['carriages']}) **{tram_expected_text}**")
    else:
        from_container.markdown(NO_TRAM_SCHEDULED_MESSAGE)


def to_schedule():
    to_container = st.container()
    to_tram_stop_ids = tram_stops[selected_afternoon_tram_stop_name]["location_ids"]
    to_container.subheader(
        f"[{selected_afternoon_tram_stop_name}](https://tfgm.com{tram_stops[selected_afternoon_tram_stop_name]['href']})")
    tram_departure_info = get_tram_departures(to_tram_stop_ids)
    trams = tram_departure_info[0]
    if len(trams) > 0:
        for tram in trams:
            if tram['expected'] == 0:
                tram_expected_text = "NOW"
            else:
                tram_expected_text = f"in **{tram['expected']}** minutes."
            to_container.markdown(f"**{tram['destination']}**  ({tram['carriages']}) **{tram_expected_text}**")
    else:
        to_container.markdown(NO_TRAM_SCHEDULED_MESSAGE)


# if before 11am
if datetime.now().hour < 12:
    from_schedule()
    to_schedule()
else:
    to_schedule()
    from_schedule()

st.subheader("[Metrolink Status](https://tfgm.com/live-updates)")
metrolinkLineStatuses = get_metrolink_line_status()
if len(metrolinkLineStatuses) > 0:
    for metrolinkLineStatus in metrolinkLineStatuses:
        if metrolinkLineStatus.get('severity') == 'danger':
            statusColour = "red"
        elif metrolinkLineStatus.get('severity') == 'warning':
            statusColour = "orange"
        else:
            statusColour = "green"
        st.markdown(f"**{metrolinkLineStatus['name']}** - :{statusColour}[{metrolinkLineStatus['status']}]")
else:
    st.write("No line status available")

with st.expander("Preferences: "):
    with st.form(key='preferences_form'):
        tram_stop_names = sorted(list(tram_stops.keys()))
        selected_morning_tram_stop_name = st.selectbox(
            'Select a Metrolink stop for the morning', tram_stop_names,
            index=tram_stop_names.index(selected_morning_tram_stop_name), key="morning_stop")
        selected_afternoon_tram_stop_name = st.selectbox(
            'Select a Metrolink stop for the afternoon', tram_stop_names,
            index=tram_stop_names.index(selected_afternoon_tram_stop_name), key="afternoon_stop")
        submit_button = st.form_submit_button(label='Save', on_click=save_user_settings)

footer = f"""<style>
  .footer {{
    display: flex; /* display the elements in a row */
    justify-content: space-between; /* space the elements evenly */
    align-items: center; /* center the items vertically */
    padding: 10px 0; /* add some padding to the top and bottom */
    width: 100%; /* set the width to 100% */
    color: grey;
    justify-content: space-around;
  }}
  
  .footer td {{
    border: none; /* remove the borders from the table cells */
  }}
</style>
<div class="footer">
  <table>
    <tr>
      <td>{current_time.strftime('%H:%M:%S')}</td>
      <td>Contains <a href="https://www.tfgm.com">TfGM</a> data</td>      
      <td>{os.getenv("RENDER_GIT_COMMIT", "local")[:7]}</td>
    </tr>
  </table>
</div>
"""
st.markdown(footer, unsafe_allow_html=True)

renew_cookie()  # this is to ensure that the cookie is renewed once per session
