# ============================================================
# NEONATAL CLINICAL DATA DASHBOARD
# Interactive Dashboard built with Panel + HVPlot
# ============================================================

import panel as pn
import pandas as pd
import hvplot.pandas
import warnings

# ------------------------------------------------------------
# 1. INITIAL CONFIGURATION
# ------------------------------------------------------------

warnings.filterwarnings("ignore")

pn.extension(
    'tabulator',   # interactive tables
    'echarts'      # modern charts
)

PRIMARY_COLOR = "#BDA623"
# ------------------------------------------------------------
# 2. LOAD AND PREPARE DATA
# ------------------------------------------------------------

file_path = "clinical_neonatal.csv"

df = pd.read_csv(file_path)

# Remove unnecessary column if it exists
df = df.drop(columns=["Unnamed: 0"], errors="ignore")

# Convert reporting date to datetime
df["reporting_month"] = pd.to_datetime(df["reporting_month"])

# Extract useful time components
df["year"] = df["reporting_month"].dt.year.astype(str)
df["month"] = df["reporting_month"].dt.month.astype(str)
df["month name"] = df["reporting_month"].dt.month_name()

df["day"] = df["reporting_month"].dt.day
df["day name"] = df["reporting_month"].dt.day_name()

# Dataset used for interactive table
data = df[
    [
        "facility_id",
        "total_deliveries",
        "live_births",
        "neonatal_deaths_0_7d",
        "neonatal_deaths_8_28d",
        "stillbirths",
        "death_birth_asphyxia",
        "death_prematurity",
    ]
]

# ------------------------------------------------------------
# 3. PAGE NAVIGATION SYSTEM
# ------------------------------------------------------------

def show_page(page_key):
    """Switch dashboard page dynamically"""
    main_area.clear()
    main_area.append(mapping[page_key])

# ------------------------------------------------------------
# 4. SIDEBAR MENU BUTTONS
# ------------------------------------------------------------

page1_btn = pn.widgets.Button(
    name="Neonatal Clinical Details",
    button_type="primary",
    styles={"width": "100%"}
)

page2_btn = pn.widgets.Button(
    name="Scatter Data Analysis",
    button_type="primary",
    styles={"width": "100%"}
)

page3_btn = pn.widgets.Button(
    name="Facility Performance",
    button_type="primary",
    styles={"width": "100%"}
)

page1_btn.on_click(lambda e: show_page("Page1"))
page2_btn.on_click(lambda e: show_page("Page2"))
page3_btn.on_click(lambda e: show_page("Page3"))

# ------------------------------------------------------------
# 5. DASHBOARD DIMENSIONS
# ------------------------------------------------------------

FULL_WIDTH = 1180
FULL_HEIGHT = 400

CHART_WIDTH = 560
CHART_HEIGHT = 330

# ------------------------------------------------------------
# 6. INTERACTIVE TABLE
# ------------------------------------------------------------

def create_data_table():
    """Interactive table showing raw clinical neonatal data"""
    return pn.widgets.Tabulator(
        data,
        show_index=False,
        width=FULL_WIDTH,
        height=FULL_HEIGHT
    )

# ------------------------------------------------------------
# 7. DASHBOARD FILTERS
# ------------------------------------------------------------

year = df['year'].max()

month_names = [
    "January","February","March","April","May","June",
    "July","August","September","October","November","December"
]

day_names = [
    "Monday","Tuesday","Wednesday","Thursday",
    "Friday","Saturday","Sunday"
]

years = sorted(df["year"].unique())
facilities = sorted(df["facility_id"].unique())

# Filters
month_filter = pn.widgets.Select(name="Month", options=month_names)
day_filter = pn.widgets.Select(name="Day", options=day_names)
year_filter = pn.widgets.Select(name="Year", options=years)
facility_filter = pn.widgets.Select(name="Facility", options=facilities)

# Data indicators available
metrics = [
    "total_deliveries",
    "live_births",
    "neonatal_deaths_0_7d",
    "neonatal_deaths_8_28d",
    "stillbirths",
    "death_birth_asphyxia",
    "death_prematurity",
]

metrics_width = [
    "total_deliveries",
    "live_births",
    "neonatal_deaths_0_7d",
    "neonatal_deaths_8_28d",
    "stillbirths",
    "death_birth_asphyxia",
    "death_prematurity",
]

metrics_heigth = [
    "death_prematurity",
    "total_deliveries",
    "live_births",
    "neonatal_deaths_0_7d",
    "neonatal_deaths_8_28d",
    "stillbirths",
    "death_birth_asphyxia",
]

metric_x = pn.widgets.Select(name="X Variable", options=metrics_width)
metric_y = pn.widgets.Select(name="Y Variable", options=metrics_heigth)

metric_bar = pn.widgets.Select(name="Indicator", options=metrics)

# ------------------------------------------------------------
# 8. KPI INDICATORS
# ------------------------------------------------------------

def kpi_cards():

    total_deliveries = int(df["total_deliveries"].sum())
    live_births = int(df["live_births"].sum())
    neonatal_early = int(df["neonatal_deaths_0_7d"].sum())
    neonatal_late = int(df["neonatal_deaths_8_28d"].sum())

    return pn.Row(

        pn.indicators.Number(
            name="Total Deliveries",
            value=total_deliveries,
            format="{value:,}"
        ),

        pn.indicators.Number(
            name="Total Live Births",
            value=live_births,
            format="{value:,}"
        ),

        pn.indicators.Number(
            name="Neonatal Deaths (0-7 days)",
            value=neonatal_early,
            format="{value:,}"
        ),

        pn.indicators.Number(
            name="Neonatal Deaths (8-28 days)",
            value=neonatal_late,
            format="{value:,}"
        ),
    )

# ------------------------------------------------------------
# 9. SCATTER ANALYSIS
# ------------------------------------------------------------

@pn.depends(month_filter, metric_x, metric_y)
def scatter_month(month_filter, metric_x, metric_y):

    filtered = df[df["month name"] == month_filter]

    return filtered.hvplot.scatter(
        x=metric_x,
        y=metric_y,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        by="year",
        title=f"Relationship {metric_x} & {metric_y} in {month_filter} by {year}"
    )


@pn.depends(day_filter, metric_x, metric_y)
def scatter_day(day_filter, metric_x, metric_y):

    filtered = df[df["day name"] == day_filter]

    return filtered.hvplot.scatter(
        x=metric_x,
        y=metric_y,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        by="year",
        title=f"Relationship {metric_x} & {metric_y} on {day_filter} by {year}"
    )

# ------------------------------------------------------------
# 10. FACILITY PERFORMANCE CHARTS
# ------------------------------------------------------------

@pn.depends(facility_filter, metric_bar)
def facility_month_bar(facility_filter, metric_bar):

    filtered = df[df["facility_id"] == facility_filter]

    return filtered.hvplot.bar(
        x="month name",
        y=metric_bar,
        rot=25,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        title=f"{metric_bar} distribution across months for facility {facility_filter}"
    )


@pn.depends(facility_filter, metric_bar)
def facility_day_bar(facility_filter, metric_bar):

    filtered = df[df["facility_id"] == facility_filter]

    return filtered.hvplot.bar(
        x="day name",
        y=metric_bar,
        rot=25,
        width=CHART_WIDTH,
        height=CHART_HEIGHT,
        title=f"{metric_bar} distribution across days for facility {facility_filter}"
    )

# ------------------------------------------------------------
# 11. PAGE 1 : DATA TABLE
# ------------------------------------------------------------

def CreatePage1():

    return pn.Column(

        "# Neonatal Clinical Dataset Overview",

        kpi_cards,

        create_data_table()
    )

# ------------------------------------------------------------
# 12. PAGE 2 : SCATTER ANALYSIS
# ------------------------------------------------------------

def CreatePage2():

    return pn.Column(

        "# Exploratory Data Analysis",

        kpi_cards,

        pn.Row(

            pn.Column(
                "### Monthly Relationship Analysis",
                metric_x,
                month_filter,
                scatter_month
            ),

            pn.Column(
                "### Daily Relationship Analysis",
                metric_y,
                day_filter,
                scatter_day
            ),
        )
    )

# ------------------------------------------------------------
# 13. PAGE 3 : FACILITY ANALYSIS
# ------------------------------------------------------------

def CreatePage3():

    return pn.Column(

        "# Facility Performance Analysis",

        kpi_cards,

        pn.Row(
            facility_filter,
            metric_bar
        ),

        pn.Row(
            facility_month_bar,
            facility_day_bar
        )
    )

# ------------------------------------------------------------
# 14. PAGE MAPPING
# ------------------------------------------------------------

mapping = {
    "Page1": CreatePage1(),
    "Page2": CreatePage2(),
    "Page3": CreatePage3(),
}

# ------------------------------------------------------------
# 15. LOGOUT BUTTON
# ------------------------------------------------------------

logout_btn = pn.widgets.Button(
    name="Logout",
    button_type="primary",
    styles={"width": "100%"}
)

logout_btn.js_on_click(
    code="window.location.href = './logout'"
)

# ------------------------------------------------------------
# 16. SIDEBAR
# ------------------------------------------------------------

sidebar = pn.Column(

    "## Dashboard Menu",

    page1_btn,
    page2_btn,
    page3_btn,

    logout_btn,

    styles={"width": "100%", "padding": "15px"}
)

# ------------------------------------------------------------
# 17. MAIN AREA
# ------------------------------------------------------------

main_area = pn.Column(
    mapping["Page2"],
    styles={"width": "100%"}
)

# ------------------------------------------------------------
# 18. TEMPLATE
# ------------------------------------------------------------

template = pn.template.FastListTemplate(

    title=f"Welcome {pn.state.user}",

    sidebar=[sidebar],
    main=[main_area],

    header_background=PRIMARY_COLOR,
    accent_base_color=PRIMARY_COLOR,

    site="Data Analysis of Clinical Neonatal Statistics Dashboard",

    logo="logo.png",

    sidebar_width=250,

    busy_indicator=None
)

template.servable()