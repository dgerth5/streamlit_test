import pandas as pd
import random
import streamlit as st

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

def app():
    players_df, contracts_df = generate_data()

    # Page 1: Agent Summary
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

    # Page 2: Position and Draft Year Analysis
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

if __name__ == "__main__":
    app()
