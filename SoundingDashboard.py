import altair as alt
import streamlit as st
import pandas as pd
import numpy as np

#soundingfile = '/content/drive/My Drive/soundingdata_2008_2022_final.csv'
#plfile = '/content/drive/My Drive/precipltng_2008_2022.csv'

soundingfile = 'soundingdata_2008_2022_final.csv'
plfile = 'precipltng_2008_2022.csv'

df1 = pd.read_csv(soundingfile)
df2 = pd.read_csv(plfile)
df = pd.merge(df1, df2, how='left', left_on='date', right_on='Date')


columns = ['Platform', 'Lat', 'Lon', 'Elevation (m)', 'Minute', 'DST', 'Sounding Base', 'Sounting Top', 'Sounding Levels', 'Bulk Richardson Number', 'Precip?', 'Lightning?', 'date']
df.drop(columns, inplace=True, axis=1)

#df=df[(df['Month'] > 5) & (df['Month'] < 10)]
df=df[(df['PWAT'] <80) & (df['PWAT'] > 0)]

df.columns = [column.replace(' ', '_') for column in df.columns]

df['Cloud_Depth_Ratio'].fillna(0, inplace = True)
df['Equilibrium_Level'].fillna(0, inplace = True)

# Loading the cars dataset
#df = data.cars()

# List of quantitative data items
item_list = [
    col for col in df.columns if df[col].dtype in ['float64', 'int64']]

# List of Origins
origin_list = list(df['Lightning'].unique())

df['Month'] = df['Month'].astype(int)

# Create the column of YYYY 
#df['YYYY'] = df['Year'].apply(lambda x: x.year)
min_month = df['Month'].min().item()
max_month = df['Month'].max().item()

st.set_page_config(layout="wide")

# Sidebar
st.sidebar.title("Dashboard of KXMR Soundings 2008-2022")
st.sidebar.markdown('###')
st.sidebar.markdown("### *Settings*")
start_month, end_month = st.sidebar.slider(
    "Month",
    min_value=min_month, max_value=max_month,
    value=(min_month, max_month))

st.sidebar.markdown('###')
origins = st.sidebar.multiselect('Lightning?', origin_list,
                                 default= origin_list)
st.sidebar.markdown('###')
item1 = st.sidebar.selectbox('Item 1', item_list, index=5)
item2 = st.sidebar.selectbox('Item 2', item_list, index=6)

df_rng = df[(df['Month'] >= start_month) & (df['Month'] <= end_month)]
source = df_rng[df_rng['Lightning'].isin(origins)]

# Content
base = alt.Chart(source).properties(height=500)

bar = base.mark_bar().encode(
    x=alt.X('count(Origin):Q', title='Number of Days'),
    y=alt.Y('Lightning:N', title='Lightning?'),
    color=alt.Color('Lightning:N', legend=None)
)

point = base.mark_circle(size=50).encode(
    x=alt.X(item1 + ':Q', title=item1),
    y=alt.Y(item2 + ':Q', title=item2),
    color=alt.Color('Lightning:N', title='',
                    legend=alt.Legend(orient='bottom-left'))
)

reg_line = point.transform_regression(item1, item2).mark_line()

params = point.transform_regression(
    item1, item2, params=True
).mark_text(align='left').encode(
    x=alt.value(20),  # pixels from left
    y=alt.value(20),  # pixels from top
    text='rSquared:N'
)


hists = base.mark_bar(opacity=0.5, thickness=100).encode(
    x=alt.X(item1 + ':Q', title='')
        .bin(step = 3), # step keeps bin size the same

    y =alt.Y('count()')
        .stack(None),

    alt.Color('Lightning:N')
    
)



# Layout (Content)
left_column, right_column = st.columns(2)

left_column.markdown(
    '**Number of Records (' + str(start_month) + '-' + str(end_month) + ')**')
left_column.altair_chart(bar, theme = None, use_container_width=True)

right_column.markdown(
    '**Scatter Plot of _' + item1 + '_ and _' + item2 + '_**')
right_column.altair_chart(point+reg_line+params, theme = None, use_container_width=True)

left_column.altair_chart(hists, theme = None, use_container_width=True)
