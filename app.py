import pandas as pd 
import streamlit as st 
import altair as alt

def load_data():
    df = pd.read_csv("cleaned_aircrash_data.csv")
    return df
try:
    df = load_data()
    
    df = df.replace(r'\(\?\)', '', regex=True)   # removes "(?)"
    df = df.replace(r'\?', '', regex=True)       # removes "?" anywhere
    
    for col in df.select_dtypes(include='object').columns:
        df[col] = df[col].map(lambda x: x.strip() if isinstance(x, str) else x)

        df["Country"] = df["Country"].replace("New", "USA")



    st.title("Air Crash Dashboard")

    filters = {
        "Year": df["Year"].unique(),
        "Month": df["Month"].unique(),
        "Manufacturer": df["Manufacturer"].unique(),
        "Country": df["Country"].unique(),
    }

    selected_filters = {}

    # Creatng filters in sidebar dyramacally
    for key, options in filters.items():
        selected_filters[key] = st.sidebar.multiselect(key, sorted(options))

    #Filtered data
    filtered_df = df.copy()
    for key, selected_values in selected_filters.items():
        if selected_values:
             filtered_df = filtered_df[filtered_df[key].isin(selected_values)]
        
    # KPIs
    total_crashes = len(filtered_df)
    total_aboard = filtered_df["Aboard"].sum()
    total_deaths = filtered_df["Total_Deaths"].sum()
    total_survivors = filtered_df["Survived"].sum()
    
    # streamiit column components
    coll, col2, col3, col4 = st.columns (4)
    with coll:
        st.metric("Total Crashes", total_crashes)
        
    with col2:
        st.metric("Total Aboard", f"{total_aboard:,}")
    
    with col3:
        st. metric("Total Deaths", f"{total_deaths:,}")
        
    with col4:
        st.metric("Total survivors", f"{total_survivors:,}")

    #display the Filtered Table
    st.dataframe(filtered_df)

    st.write("### Analysis Finding")

    st.subheader("1️⃣ Aircraft with Highest Survivors")
    top_survivors = df.groupby("Aircraft")["Survived"].sum().reset_index().sort_values(by="Survived", ascending=False).head(10)
    chart1 = alt.Chart(top_survivors).mark_bar().encode(
        x="Survived:Q",
        y=alt.Y("Aircraft:N", sort="-x"),
        tooltip=["Aircraft", "Survived"]
    )
    st.altair_chart(chart1, use_container_width=True)

    st.subheader("2️⃣ Number of Crashes per Country")
    
    top_crashes = (
        df["Country"]
        .value_counts()
        .reset_index()
        .head(10)
    )
    if "index" in top_crashes.columns:
        top_crashes = top_crashes.rename(columns={"index": "Country", "Country": "Crashes"})
    elif "count" in top_crashes.columns:
        top_crashes = top_crashes.rename(columns={"count": "Crashes"})
        
    top_crashes.columns = top_crashes.columns.str.strip()
    
    st.write("🔍 Debug - top_crashes DataFrame")
    st.write(top_crashes.head())
    st.write(top_crashes.columns.tolist())
    
    chart2 = alt.Chart(top_crashes).mark_bar(color="orange").encode(
        x=alt.X("Crashes:Q", title="Number of Crashes"),
        y=alt.Y("Country:N", sort="-x", title="Country"),
        tooltip=["Country", "Crashes"]
    )
    
    st.altair_chart(chart2, use_container_width=True)

    st.subheader("3️⃣ Operators with Highest Fatalities (Top 5)")
    top_operators = (
        df.groupby("Operator")["Total_Fatalities"]
        .sum()
        .reset_index()
        .sort_values(by="Total_Fatalities", ascending=False)
        .head(5)
    )
    
    chart3 = (
        alt.Chart(top_operators)
        .mark_rect()
        .encode(
            x="Operator:N",
            y="Total_Fatalities:Q",
            color="Total_Fatalities:Q",
            tooltip=["Operator", "Total_Fatalities"]
        )
    )
    st.altair_chart(chart3, use_container_width=True)

    st.subheader("4️⃣ Trend in Number of Crashes Over Time")
    df["Year"] = pd.to_datetime(df["Date"], errors="coerce").dt.year
    crash_trend = df.groupby("Year").size().reset_index(name="Crashes")
    
    chart4 = (
        alt.Chart(crash_trend)
        .mark_line(point=True, color="orange")
        .encode(
            x="Year:O",
            y="Crashes:Q",
            tooltip=["Year", "Crashes"]
        )
    )
    st.altair_chart(chart4, use_container_width=True)

    st.subheader("5️⃣ Countries with Highest Fatalities")
    country_fatalities = (
        df.groupby("Country")["Total_Fatalities"]
        .sum()
        .reset_index()
        .sort_values(by="Total_Fatalities", ascending=False)
        .head(10)
    )
    
    chart5 = (
        alt.Chart(country_fatalities)
        .mark_circle()
        .encode(
            x="Country:N",
            y="Total_Fatalities:Q",
            size="Total_Fatalities:Q",
            color="Country:N",
            tooltip=["Country", "Total_Fatalities"]
        )
    )
    st.altair_chart(chart5, use_container_width=True)

    st.subheader("6️⃣ Monthly Crash Trends")
    df["Month"] = pd.to_datetime(df["Date"], errors="coerce").dt.month
    monthly_trend = df.groupby("Month").size().reset_index(name="Crashes")
    
    chart6 = (
        alt.Chart(monthly_trend)
        .mark_area(opacity=0.6, color="green")
        .encode(
            x="Month:O",
            y="Crashes:Q",
            tooltip=["Month", "Crashes"]
        )
    )
    st.altair_chart(chart6, use_container_width=True)

    st.header("📊 Findings")
    
    st.markdown("""
    - Some aircraft models recorded **higher survival rates** compared to others.  
    - Certain countries (e.g., **Russia, Brazil, Colombia**) experienced the **highest crash frequencies**.  
    - A few operators accounted for **disproportionately high fatalities**.  
    - The **number of crashes peaked in certain decades**, but has declined in recent years.  
    - Fatalities were **concentrated in a few countries**, highlighting regional safety gaps.  
    - **Monthly crash patterns** suggest weather and seasonal effects may contribute to risks.  
    """)

    st.header("✅ Recommendations")
    
    st.subheader("Strengthen Aviation Safety Regulations")
    st.markdown("""
    - Countries with high crash/fatality rates should review and enforce **stricter aviation safety standards**.  
    - Regulatory bodies should increase **inspections** for operators with poor safety records.  
    """)
    
    st.subheader("Fleet Modernization")
    st.markdown("""
    - Encourage replacement of **older aircraft** with newer models equipped with modern safety technology.  
    - Provide **incentives** for operators to upgrade fleets.  
    """)
    
    st.subheader("Pilot and Crew Training")
    st.markdown("""
    - Enhance **emergency preparedness training** to improve survival rates.  
    - Standardize **global best practices** in crew resource management.  
    """)
    
    st.subheader("Geography & Weather Risk Mitigation")
    st.markdown("""
    - Invest in **advanced weather monitoring** and air traffic control systems, especially in regions prone to adverse conditions.  
    """)
    
    st.subheader("Global Collaboration")
    st.markdown("""
    - Share **crash investigation data internationally** to identify patterns and prevent future accidents.  
    """)
    
    st.subheader("Passenger Awareness")
    st.markdown("""
    - Increase awareness about **safety procedures**, since survival also depends on passenger compliance during emergencies.  
    """)

except Exception as e:
    st.error("Error: check error details")

    with st.expander("Error Details"):
        st.code(str(e))
        # st.code (traceback.format.exc())

    