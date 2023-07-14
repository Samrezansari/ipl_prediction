
import streamlit as st
import pickle
import pandas as pd
import folium
from streamlit_folium import folium_static
import matplotlib.pyplot as plt

ipl_df = pd.read_csv('finaldata.csv')

teams = ['Sunrisers Hyderabad',
 'Mumbai Indians',
 'Royal Challengers Bangalore',
 'Kolkata Knight Riders',
 'Kings XI Punjab',
 'Chennai Super Kings',
 'Rajasthan Royals',
 'Delhi Capitals']

cities = ['Hyderabad', 'Bangalore', 'Mumbai', 'Indore', 'Kolkata', 'Delhi',
       'Chandigarh', 'Jaipur', 'Chennai', 'Cape Town', 'Port Elizabeth',
       'Durban', 'Centurion', 'East London', 'Johannesburg', 'Kimberley',
       'Bloemfontein', 'Ahmedabad', 'Cuttack', 'Nagpur', 'Dharamsala',
       'Visakhapatnam', 'Pune', 'Raipur', 'Ranchi', 'Abu Dhabi',
       'Sharjah', 'Mohali', 'Bengaluru']

pipe = pickle.load(open('pipe.pkl','rb'))
st.title('IPL Win Predictor')


# Create a new column to store the match pairs in sorted order
ipl_df['match_pairs'] = ipl_df.apply(lambda x: tuple(sorted([x['team1'], x['team2']])), axis=1)

# Filter the DataFrame to include only the matches won by each team
team1_wins = ipl_df[ipl_df['winner'] == ipl_df['team1']]
team2_wins = ipl_df[ipl_df['winner'] == ipl_df['team2']]

# Calculate the count of matches won by each team against each other
team1_vs_team2 = team1_wins.groupby('match_pairs').size().reset_index(name='team1_wins_count')
team2_vs_team1 = team2_wins.groupby('match_pairs').size().reset_index(name='team2_wins_count')

# Merge the counts for both teams
team_wins = pd.merge(team1_vs_team2, team2_vs_team1, on='match_pairs', how='outer').fillna(0)



col1, col2 = st.columns(2)

with col1:
    batting_team = st.selectbox('Select the batting team',sorted(teams))
with col2:
    bowling_team = st.selectbox('Select the bowling team',sorted(teams))

selected_city = st.selectbox('Select Host City',sorted(cities))

target = st.number_input('Target',min_value=0, step=1,)

col3,col4,col5 = st.columns(3)

with col3:
    score = st.number_input('Score',min_value=0, step=1,)

with col4:
    overs = st.number_input('Overs Completed',min_value=1, max_value=19)

with col5:
    wickets = st.number_input('Wickets Out', min_value=0, step=1, max_value=9)

if st.button('Predict Probability'):
    runs_left = target - score
    ball_left = 120 - (overs*6)
    wickets = 10 - wickets
    crr = score/overs
    rrr = (runs_left*6)/ball_left

    input_df = pd.DataFrame({'batting_team':[batting_team],'bowling_team':[bowling_team],'city':[selected_city],'runs_left':[runs_left],
                             'ball_left':[ball_left],'wickets':[wickets],'total_runs_x':[target],'crr':[crr],'rrr':[rrr]})
    
    # st.table(input_df)

    result = pipe.predict_proba(input_df)
    loss = result[0][0]
    win = result[0][1]
    st.markdown('---')
    st.header('WIN PROBABILITY')
    st.header(batting_team + "-" + str(round(win*100)) + "%")
    if wickets <= 4:
        st.text("The " + batting_team + " team needs to go for an effective partnership.")
    if rrr >= 10:
        st.text("The " + batting_team + " team needs to pace up their run speed.")
    st.header(bowling_team + "-" + str(round(loss*100)) + "%")
    if wickets >= 6:
        st.text("The " + bowling_team + " team needs an attacking plan to take wickets.")
    if rrr <= 7:
        st.text("The " + bowling_team + " team needs to slowdown the run flow.")



#--------------------------------- Match Details ---------------------------------------------------------------
    st.markdown('---')

    st.header('MATCH DETAILS')
    st.table(input_df)
    # Filter the team_wins DataFrame based on user-selected teams
    filtered_data = team_wins[
        ((team_wins['match_pairs'].str[0] == batting_team) & (team_wins['match_pairs'].str[1] == bowling_team)) |
        ((team_wins['match_pairs'].str[0] == bowling_team) & (team_wins['match_pairs'].str[1] == batting_team))
    ]

    # # Display the filtered DataFrame
    # st.write(filtered_data)

    # # Create a bar plot to visualize the match wins for both teams
    # filtered_data.plot(x='match_pairs', y=['team1_wins_count', 'team2_wins_count'], kind='bar')

    # # Set plot labels and title
    # # plt.xlabel('Team Pairs')
    # plt.ylabel('Number of Matches Won')
    # plt.title('Number of Matches Won by Each Team against Each Other')

    # # Display the plot in Streamlit
    # st.pyplot(plt)


    if not filtered_data.empty:
        # Plot the match wins for both teams
        fig, ax = plt.subplots(figsize=(10, 6))
        x = [1, 2]  # x-axis positions for the bars
        team1_wins = filtered_data['team1_wins_count'].values[0]
        team2_wins = filtered_data['team2_wins_count'].values[0]
        ax.bar(x[0], team1_wins, label=batting_team)
        ax.bar(x[1], team2_wins, label=bowling_team)
        ax.set_xticks(x)
        ax.set_xticklabels([batting_team, bowling_team])
        ax.set_xlabel('Teams')
        ax.set_ylabel('Number of Matches Won')
        ax.set_title('Number of Matches Won by Each Team against Each Other')
        ax.legend()

        # Display the plot in Streamlit
        st.pyplot(fig)
    else:
        st.write('No match data available for the selected teams.')



# ---------------VENUE DETAILS --------------------------------------------------------------------------
    st.markdown('---')

    st.header('VENUE DETAILS')
    
    col6,col7=st.columns(2)
    if selected_city == 'Mumbai':
        with col6:
            st.header('Mumbai Wankhede stadium pitch is Good for batting, Strategically located near the sea .The Chasing team have higher chances of win')
        # Create a map centered around Mumbai
        with col7:
            mumbai_coords = (18.93389243996987, 72.8275601260855)
            map_mumbai = folium.Map(location=mumbai_coords, zoom_start=15)

    # Add a marker to the map
            marker_coords = (18.939005002711703, 72.82575326602901)  # Example coordinates
            folium.Marker(location=marker_coords, popup='Wankhede Stadium').add_to(map_mumbai)
        # Display the map using folium_static
            folium_static(map_mumbai,width=400)

    st.markdown('---')

    # Extract the year from the 'date' column
    ipl_df['year'] = pd.to_datetime(ipl_df['date'], format="%d-%m-%Y").dt.year
    # ipl_df['year'] = pd.to_datetime(ipl_df['date']).dt.year
    # Filter the DataFrame based on the user-selected city
    filtered_df = ipl_df[ipl_df['city'] == selected_city]

    # Calculate the average score in the selected city year by year
    average_score = filtered_df.groupby('year')['total_runs'].mean().reset_index()

    # Display the average score in the selected city
    # st.write(f'Average Score in {selected_city}:')
    # st.write(average_score)

    # Plot the average score in the selected city year by year
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(average_score['year'], average_score['total_runs'], marker='o')

    ax.set_xlabel('Year')
    ax.set_ylabel('Average Score')
    ax.set_title(f'Average Score in {selected_city} Year by Year')

    # Display the plot in Streamlit
    st.pyplot(fig)
    

    
    # # Filter the team_wins DataFrame based on user-selected teams
    # filtered_data = team_wins[
    #     ((team_wins['match_pairs'].str[0] == batting_team) & (team_wins['match_pairs'].str[1] == bowling_team)) |
    #     ((team_wins['match_pairs'].str[0] == bowling_team) & (team_wins['match_pairs'].str[1] == batting_team))
    # ]

    # # # Display the filtered DataFrame
    # # st.write(filtered_data)

    # # # Create a bar plot to visualize the match wins for both teams
    # # filtered_data.plot(x='match_pairs', y=['team1_wins_count', 'team2_wins_count'], kind='bar')

    # # # Set plot labels and title
    # # # plt.xlabel('Team Pairs')
    # # plt.ylabel('Number of Matches Won')
    # # plt.title('Number of Matches Won by Each Team against Each Other')

    # # # Display the plot in Streamlit
    # # st.pyplot(plt)


    # if not filtered_data.empty:
    #     # Plot the match wins for both teams
    #     fig, ax = plt.subplots(figsize=(10, 6))
    #     x = [1, 2]  # x-axis positions for the bars
    #     team1_wins = filtered_data['team1_wins_count'].values[0]
    #     team2_wins = filtered_data['team2_wins_count'].values[0]
    #     ax.bar(x[0], team1_wins, label=batting_team)
    #     ax.bar(x[1], team2_wins, label=bowling_team)
    #     ax.set_xticks(x)
    #     ax.set_xticklabels([batting_team, bowling_team])
    #     ax.set_xlabel('Teams')
    #     ax.set_ylabel('Number of Matches Won')
    #     ax.set_title('Number of Matches Won by Each Team against Each Other')
    #     ax.legend()

    #     # Display the plot in Streamlit
    #     st.pyplot(fig)
    # else:
    #     st.write('No match data available for the selected teams.')



    # Create a sidebar at the bottom of the page
st.markdown('---')
st.text('© 2023 TEAM UNBEATABLE. All rights reserved.')