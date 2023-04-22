import os

import pytz
import streamlit as st
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

from metrolink_lines import get_metrolink_line_status
from trams import get_tram_departures

NO_TRAM_SCHEDULED_MESSAGE = "No trams currently scheduled to depart."

tz = pytz.timezone('Europe/London')
current_time = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)

st.set_page_config(layout="wide")
st.markdown(
    """
        <style>
            .appview-container .main .block-container {{
                padding-top: {padding_top}rem;
                padding-bottom: {padding_bottom}rem;
                }}

        </style>""".format(
        padding_top=0, padding_bottom=1
    ),
    unsafe_allow_html=True,
)

# st_autorefresh(interval=60 * 1000)
st_autorefresh(interval=15 * 1000)

#if before 11am
if datetime.now().hour < 11:
    from_container = st.container()
    # Display tram information in a table
    from_container.subheader(f'[{os.environ["morning_name"]}]({os.environ["morning_url"]})')
    tramDepartureInfo = get_tram_departures(os.environ["morning_ids"].split(","))
    trams = tramDepartureInfo[0]
    if len(trams) > 0:
        for tram in trams:
            if tram['expected'] == 0:
                tramExpectedText = "NOW"
            else:
                tramExpectedText = f"in **{tram['expected']}** minutes."
            from_container.markdown(f"**{tram['destination']}**  ({tram['carriages']}) **{tramExpectedText}**")
    else:
        from_container.markdown(NO_TRAM_SCHEDULED_MESSAGE)

to_container = st.container()
to_container.subheader(f'[{os.environ["afternoon_name"]}]({os.environ["afternoon_url"]})')
tramDepartureInfo = get_tram_departures(os.environ["afternoon_ids"].split(","))
trams = tramDepartureInfo[0]
if len(trams) > 0:
    for tram in trams:
        if tram['expected'] == 0:
            tramExpectedText = "NOW"
        else:
            tramExpectedText = f"in **{tram['expected']}** minutes."
        to_container.markdown(f"**{tram['destination']}**  ({tram['carriages']}) **{tramExpectedText}**")
else:
    to_container.markdown(NO_TRAM_SCHEDULED_MESSAGE)


#if after 11am
if datetime.now().hour >= 11:
    from_container = st.container()
    # Display tram information in a table
    from_container.subheader(f'[{os.environ["morning_name"]}]({os.environ["morning_url"]})')
    tramDepartureInfo = get_tram_departures(os.environ["morning_ids"].split(","))
    trams = tramDepartureInfo[0]
    if len(trams) > 0:
        for tram in trams:
            if tram['expected'] == 0:
                tramExpectedText = "NOW"
            else:
                tramExpectedText = f"in **{tram['expected']}** minutes."
            from_container.markdown(f"**{tram['destination']}**  ({tram['carriages']}) **{tramExpectedText}**")
    else:
        from_container.markdown(NO_TRAM_SCHEDULED_MESSAGE)


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
