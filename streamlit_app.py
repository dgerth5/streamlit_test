import pandas as pd
import random
import streamlit as st

@st.cache_data
def generate_data():
    # Generate first dataset: Agents with their regions
    positions = ["Pitcher", "Catcher", "Infielder", "Outfielder"]
    regions = ["Northwest", "Southwest", "Midwest", "Northeast", "Southeast"]
    
    # Assign each agent a specific region
    agents = []
    for i in range(1, 13):
        agents.append({
            "AgentName": f"Agent {i}",
            "Region": random.choice(regions)
        })
    agents_df = pd.DataFrame(agents)
    
    draft_years = [2025, 2026, 2027]

    # Generate players and assign them to agents
    players = []
    for i in range(1, 1001):
        agent_data = random.choice(agents)
        players.append({
            "Name": f"Player {i}",
            "Position": random.choice(positions),
            "DraftYear": random.choice(draft_years),
            "AgentName": agent_data["AgentName"]
        })

    players_df = pd.DataFrame(players)
    # Merge with agents_df to get agent regions when needed
    players_df = players_df.merge(agents_df, on="AgentName", how="left")

    # Generate second dataset: Contracts
    contracts = []
    for i in range(1, 101):
        agent_data = random.choice(agents)
        total_signed = round(random.uniform(1, 50), 2)  # Signed in $MM
        expected_signed = round(total_signed + random.uniform(-5, 10), 2)
        contracts.append({
            "Name": f"Player {1000 + i}",
            "AgentName": agent_data["AgentName"],
            "TotalSigned": total_signed,
            "ExpectedSigned": expected_signed,
        })

    contracts_df = pd.DataFrame(contracts)

    return players_df, contracts_df, agents_df

def calculate_similarity(players_df, agents_df, position, draft_year, region, same_region, more_than_5, more_than_3):
    agent_scores = {agent: 0 for agent in agents_df["AgentName"].unique()}

    for agent in agent_scores:
        # Check if agent is in the same region
        if same_region:
            agent_region = agents_df[agents_df["AgentName"] == agent]["Region"].iloc[0]
            if agent_region == region:
                agent_scores[agent] += 1

        # Check if agent has more than 5 players in the draft class
        if more_than_5:
            draft_class_count = players_df[
                (players_df["AgentName"] == agent) & 
                (players_df["DraftYear"] == draft_year)
            ].shape[0]
            if draft_class_count > 5:
                agent_scores[agent] += 1

        # Check if agent has more than 3 players in the same position in the draft class
        if more_than_3:
            position_count = players_df[
                (players_df["AgentName"] == agent) & 
                (players_df["DraftYear"] == draft_year) & 
                (players_df["Position"] == position)
            ].shape[0]
            if position_count > 3:
                agent_scores[agent] += 1

    # Convert to DataFrame
    scores_df = pd.DataFrame(agent_scores.items(), columns=["AgentName", "SimilarityScore"])
    # Merge with agents_df to include region information
    scores_df = scores_df.merge(agents_df[["AgentName", "Region"]], on="AgentName", how="left")
    return scores_df.sort_values(by="SimilarityScore", ascending=False)

def app():
    players_df, contracts_df, agents_df = generate_data()

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
        # Merge with agents_df to include region information
        summary_df = summary_df.merge(agents_df[["AgentName", "Region"]], on="AgentName", how="left")

        st.dataframe(
            summary_df,
            use_container_width=True,
            column_config={
                "TotalSigned": st.column_config.NumberColumn(format="%.2f"),
                "ExpectedSigned": st.column_config.NumberColumn(format="%.2f"),
                "Difference": st.column_config.NumberColumn(format="%.2f")
            },
            hide_index=True
        )

    elif page == "Position Analysis":
        st.title("Position Analysis")
        position = st.selectbox("Select Position:", players_df["Position"].unique(), key="position_analysis")

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
        position = st.selectbox("Select your position:", players_df["Position"].unique(), key="position_questionnaire")
        draft_year = st.selectbox("Select your draft class:", sorted(players_df["DraftYear"].unique()), key="draft_year_questionnaire")
        region = st.selectbox("Select your region:", agents_df["Region"].unique(), key="region_questionnaire")

        same_region = st.checkbox("Do you want an agent in the same region?", key="same_region_questionnaire")
        more_than_5 = st.checkbox("Do you want an agent to have more than 5 players in your draft class?", key="more_than_5_questionnaire")
        more_than_3 = st.checkbox("Do you want an agent to have more than 3 players at your position in your draft class?", key="more_than_3_questionnaire")

        if st.button("Calculate Similarity Score", key="calculate_button_questionnaire"):
            similarity_df = calculate_similarity(
                players_df, agents_df, position, draft_year, region, same_region, more_than_5, more_than_3
            )
            st.write("### Agent Similarity Scores")
            st.dataframe(similarity_df, use_container_width=True)

if __name__ == "__main__":
    app()
