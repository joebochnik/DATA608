import pandas as pd
import plotly.express as px
import streamlit as st

# Streamlit app title
st.title("NFL 2024 Cumulative Point Differential Rankings")

# Load the dataset
file_path = 'spreadspoke_scores.csv'
df = pd.read_csv(file_path)

weeks = ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11']

# Filter for the 2024 regular season
df_2024 = df[
    (df['schedule_season'] == 2024) &
    (df['schedule_playoff'] == False) &
    (df['schedule_week'].astype(str).isin(weeks))
]

# Calculate point differentials for home and away teams
home_diff = df_2024[['schedule_week', 'team_home', 'score_home', 'score_away']].copy()
home_diff['Point_Differential'] = home_diff['score_home'] - home_diff['score_away']
home_diff = home_diff.rename(columns={'schedule_week': 'Week', 'team_home': 'Team'})

away_diff = df_2024[['schedule_week', 'team_away', 'score_home', 'score_away']].copy()
away_diff['Point_Differential'] = away_diff['score_away'] - away_diff['score_home']
away_diff = away_diff.rename(columns={'schedule_week': 'Week', 'team_away': 'Team'})

# Combine home and away differentials
point_diff_data = pd.concat([home_diff[['Week', 'Team', 'Point_Differential']],
                             away_diff[['Week', 'Team', 'Point_Differential']]])

# Ensure the week is integer for sorting
point_diff_data['Week'] = point_diff_data['Week'].astype(int)

# Calculate cumulative point differentials for each team
point_diff_data['Cumulative_Point_Differential'] = point_diff_data.groupby('Team')['Point_Differential'].cumsum()

# Ensure all teams are present in every week
all_teams = point_diff_data['Team'].unique()
all_weeks = point_diff_data['Week'].unique()
full_index = pd.MultiIndex.from_product([all_weeks, all_teams], names=['Week', 'Team'])

# Reindex the dataframe to include all combinations of weeks and teams
point_diff_data = point_diff_data.set_index(['Week', 'Team']).reindex(full_index, fill_value=0).reset_index()

# Recalculate cumulative point differentials after reindexing
point_diff_data['Cumulative_Point_Differential'] = point_diff_data.groupby('Team')['Point_Differential'].cumsum()

# Sort and prepare data for visualization
point_diff_data = point_diff_data.sort_values(by=['Week', 'Cumulative_Point_Differential'], ascending=[True, False])

# Create the Plotly animated bar chart
fig = px.bar(
    point_diff_data,
    x="Cumulative_Point_Differential",
    y="Team",
    color="Team",
    animation_frame="Week",
    orientation="h",
    title="NFL 2024 Cumulative Point Differential Rankings",
    labels={"Cumulative_Point_Differential": "Cumulative Differential", "Team": "NFL Teams"}
)

# Adjust animation speed for better visualization
fig.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 1500  # 1.5 seconds per frame

# Sort the legend alphabetically
fig.update_layout(
    xaxis_title="Cumulative Point Differential",
    yaxis_title="Team",
    yaxis=dict(categoryorder="total ascending"),  # Ensure sorting by total at each frame
    legend=dict(traceorder="grouped")  # Sort alphabetically by team name
)

# Display the Plotly chart in Streamlit
st.plotly_chart(fig, use_container_width=True)
