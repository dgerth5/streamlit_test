import pandas as pd
import numpy as np
import random
import streamlit as st

@st.cache_data
def generate_data():
    # Generate first dataset: Players
    positions = ["Pitcher", "Catcher", "Infielder", "Outfielder"]
    regions = ["Northwest", "Southwest", "Midwest", "Northeast", "Southeast"]
    agents = [f"Agent {i}" for i in range(1, 13)]
    draft_years = [2025, 2026, 2027]

    players = []
    for i in range(1, 1001):
        players.append({
            "Name": f"Player {i}",
            "Position": random.choice(positions),
            "DraftYear": random.choice(draft_years),
            "AgentName": random.choice(agents),
            "Region": random.choice(regions),
        })

    players_df = pd.DataFrame(players)

    # Generate second dataset: Contracts
    contracts = []
    for i in range(1, 101):
        agent = random.choice(agents)
        total_signed = round(random.uniform(1, 50), 2)  # Signed in $MM
        expected_signed = round(total_signed + random.uniform(-5, 10), 2)
        contracts.append({
            "Name": f"Player {1000 + i}",
            "AgentName": agent,
            "TotalSigned": total_signed,
            "ExpectedSigned": expected_signed,
        })

    contracts_df = pd.DataFrame(contracts)

    return players_df, contracts_df

def calculate_similarity(players_df, position, draft_year, region, same_region, more_than_5, more_than_3):
    agent_scores = {agent: 0 for agent in players_df["AgentName"].unique()}

    for agent in agent_scores:
        # Check if agent is in the same region
        if same_region:
            if region in players_df[players_df["AgentName"] == agent]["Region"].values:
                agent_scores[agent] += 1

        # Check if agent has more than 5 players in the draft class
        if more_than_5:
            if len(players_df[(players_df["AgentName"] == agent) & (players_df["DraftYear"] == draft_year)]) > 5:
                agent_scores[agent] += 1

        # Check if agent has more than 3 players in the same position in the draft class
        if more_than_3:
            if len(players_df[(players_df["AgentName"] == agent) & (players_df["DraftYear"] == draft_year) & (players_df["Position"] == position)]) > 3:
                agent_scores[agent] += 1

    # Convert to DataFrame
    scores_df = pd.DataFrame(agent_scores.items(), columns=["AgentName", "SimilarityScore"])
    return scores_df.sort_values(by="SimilarityScore", ascending=False)

def app():
    players_df, contracts_df = generate_data()

    # Sidebar navigation
    page = st.sidebar.selectbox("Choose a page", ["Agent Summary", "Position Analysis", "Questionnaire"])

    if page == "Agent Summary":
        st.title("Agent Summary")

        summary_df = (
            contracts_df.groupby("AgentName")
            .agg({"TotalSigned": "sum", "ExpectedSigned": "sum"})
            .reset_index()
        )
        summary_df["Difference"] = summary_df["TotalSigned"] - summary_df["ExpectedSigned"]

        st.dataframe(
            summary_df.sort_values(by="TotalSigned", ascending=False),
            use_container_width=True,
        )

    elif page == "Position Analysis":
        st.title("Position Analysis")
        position = st.selectbox("Select Position:", players_df["Position"].unique())

        filtered_df = players_df[players_df["Position"] == position]
        grouped = (
            filtered_df.groupby(["AgentName", "DraftYear"])
            .size()
            .reset_index(name="Count")
        )

        st.bar_chart(
            grouped.pivot(index="AgentName", columns="DraftYear", values="Count").fillna(0),
        )

    elif page == "Questionnaire":
        st.title("Agent Questionnaire")

        # User inputs
        position = st.selectbox("Select your position:", players_df["Position"].unique(), key="position")
        draft_year = st.selectbox("Select your draft class:", sorted(players_df["DraftYear"].unique()), key="draft_year")
        region = st.selectbox("Select your region:", players_df["Region"].unique(), key="region")

        same_region = st.checkbox("Do you want an agent in the same region?", key="same_region")
        more_than_5 = st.checkbox("Do you want an agent to have more than 5 players in your draft class?", key="more_than_5")
        more_than_3 = st.checkbox("Do you want an agent to have more than 3 players at your position in your draft class?", key="more_than_3")

        if st.button("Calculate Similarity Score", key="calculate_button"):
            similarity_df = calculate_similarity(
                players_df, position, draft_year, region, same_region, more_than_5, more_than_3
            )
            st.write("### Agent Similarity Scores")
            st.dataframe(similarity_df, use_container_width=True)

if __name__ == "__main__":
    app()
