"""
Logistics Dummy data generator made by Dallin Packer of DGPAnalytics for
Daily Dashboard Showcase
"""

import pandas as pd
import numpy as np
import random
from faker import Faker
from datetime import datetime, timedelta
from sqlalchemy import create_engine

###########################
####### PARAMETERS ########
###########################

SEED = 42
random.seed(SEED)
np.random.seed(SEED)
Faker.seed(SEED)
fake = Faker()

start_date = datetime(2023, 1, 1)
end_date = datetime(2026, 2, 15)
days_range = (end_date - start_date).days

#### Row Count Settings ####
num_parts = 500
num_locations = 300
num_employees = 120
num_orders_inbound = 90000
num_orders_outbound = 110000
num_cycle_counts = 40000
num_hours = 210000

#### SLA Settings ####
INBOUND_SLA_HOURS = {"Low": 24.0, "Normal": 8.0, "High": 1.0}
OUTBOUND_SLA_HOURS = {"Low": 48.0, "Normal": 24.0, "High": 2.0}

###### Probability Settings ######
# Determine the probability of a line being on time or late
INBOUND_ONTIME_PROB = {"High": 0.995, "Normal": 0.93, "Low": 0.95}
OUTBOUND_ONTIME_PROB = {"High": 0.95, "Normal": 0.90, "Low": 0.99}

# Distribution parameters for internal steps (in hours)
PUTAWAY_MIN_HOURS = 0.0833
PUTAWAY_MAX_HOURS = 8.0

PICK_MIN_HOURS = 0.01
PICK_MAX_HOURS = 6.0

PACK_MIN_HOURS = 0.01
PACK_MAX_HOURS = 4.0

SHIP_MIN_AFTER_LOAD_HOURS = 0.25
SHIP_MAX_AFTER_LOAD_HOURS = 48.0

# PostgreSQL connection
PG_USER = "postgres"
PG_PASSWORD = "dGp1998rJs1989!"
PG_HOST = "localhost"
PG_PORT = "5432"
PG_DATABASE = "postgres"

###########################
##### HELPER FUNCTIONS ####
###########################
def random_datetime_within_range(start=start_date, days=days_range):
    """Random datetime between start and start+days"""
    day_offset = random.randint(0, days)
    hour = random.randint(0, 23)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    return start + timedelta(days=day_offset, hours=hour, minutes=minute, seconds=second)

def hours_to_timedelta(hours):
    return timedelta(seconds=round(hours * 3600))

###########################
####### DIM BUILDER #######
###########################
order_type_data = [
    ("DIST", "Inbound", "Distribution"),
    ("600", "Inbound", "Direct Import"),
    ("RET", "Inbound", "Return"),
    ("W2W", "Outbound", "Warehouse Transfer"),
    ("ECOM", "Outbound", "E-commerce"),
    ("STO", "Outbound", "Store Order"),
]
order_type_dim = pd.DataFrame(order_type_data, columns=["Order_Type_ID", "Inbound_Outbound_Indicator", "Order_Type"])

count_type_data = [("FC", "First Count"), ("SC", "Second Count"), ("FCN", "Final Count")]
count_type_dim = pd.DataFrame(count_type_data, columns=["Count_Type_ID", "Count_Type"])

part_dim = pd.DataFrame({
    "Part_ID": [f"P{str(i).zfill(5)}" for i in range(1, num_parts+1)],
    "Part_Num": [f"PN-{i}" for i in range(1, num_parts+1)],
    "Part_Description": [fake.word().capitalize() + " Part" for _ in range(num_parts)],
    "Temp_Control_Flag": np.random.choice(["Y", "N"], num_parts),
    "Part_Type": np.random.choice(["Raw", "Finished", "Component"], num_parts),
    "Last_Count_Date": [start_date + timedelta(days=random.randint(0, days_range)) for _ in range(num_parts)],
    "Width_CM": np.round(np.random.uniform(5, 200, num_parts), 2),
    "Length_CM": np.round(np.random.uniform(5, 200, num_parts), 2),
    "Depth_CM": np.round(np.random.uniform(5, 200, num_parts), 2),
    "Part_Size": np.random.choice(["S", "M", "L"], num_parts)
})

location_dim = pd.DataFrame({
    "Location_ID": [f"L{str(i).zfill(4)}" for i in range(1, num_locations+1)],
    "Location_Num": [f"LOC-{i}" for i in range(1, num_locations+1)],
    "Location_Description": [f"Aisle {random.randint(1,50)} Bin {random.randint(1,20)}" for _ in range(num_locations)],
    "Area": np.random.choice(["Inbound Dock", "Outbound Dock", "Storage", "Picking"], num_locations),
    "Aisle": [f"A{random.randint(1,50)}" for _ in range(num_locations)],
    "Bay": [f"B{random.randint(1,30)}" for _ in range(num_locations)],
    "Bin": [f"Bin{random.randint(1,20)}" for _ in range(num_locations)],
    "Location_Type": np.random.choice(["Pallet", "Shelf", "Bin"], num_locations),
    "Temp_Control_Flag": np.random.choice(["Y", "N"], num_locations),
    "Location_Size": np.random.choice(["S", "M", "L"], num_locations),
    "Width_CM": np.round(np.random.uniform(50, 300, num_locations), 2),
    "Length_CM": np.round(np.random.uniform(50, 300, num_locations), 2),
    "Depth_CM": np.round(np.random.uniform(50, 300, num_locations), 2),
})

employee_dim = pd.DataFrame({
    "Employee_ID": [f"E{str(i).zfill(4)}" for i in range(1, num_employees+1)],
    "Employee_First_Name": [fake.first_name() for _ in range(num_employees)],
    "Employee_Last_Name": [fake.last_name() for _ in range(num_employees)],
    "Job_Title": np.random.choice(["Associate", "Supervisor", "Manager"], num_employees),
    "Home_Function_ID": np.random.choice(["INB", "OUT", "CYCLE", "GEN"], num_employees),
    "Hire_Date": [start_date - timedelta(days=random.randint(30, 1000)) for _ in range(num_employees)]
})

function_data = [("INB", "Inbound Processing", "Inbound"), ("OUT", "Outbound Processing", "Outbound"),
                 ("CYCLE", "Cycle Counting", "Inventory"), ("GEN", "General Labor", "Support")]
function_dim = pd.DataFrame(function_data, columns=["Function_ID", "Function_Name", "Function_Department"])

pay_data = [("WRK", "Worked Hours"), ("PTO", "Paid Time Off"), ("OT", "Overtime")]
pay_dim = pd.DataFrame(pay_data, columns=["Pay_ID", "Pay_Name"])

metric_data = [("ACT", "Actual Hours"), ("PLN", "Planned Hours")]
metric_dim = pd.DataFrame(metric_data, columns=["Metric_ID", "Metric_Name"])

###########################
###### FACT BUILDER #######
###########################

# Helper to pick priority with realistic distribution
def pick_priority():
    return random.choices(["High", "Normal", "Low"], weights=[0.10, 0.60, 0.30], k=1)[0]

inbound_rows = []
for i in range(num_orders_inbound):
    order_line_id = f"IL{str(i+1).zfill(7)}"
    order_id = f"INB{random.randint(1000,9999)}"
    order_type = random.choice(order_type_dim[order_type_dim["Inbound_Outbound_Indicator"]=="Inbound"]["Order_Type_ID"].tolist())
    origin_country = random.choice(["US","MX","CN","CA","GR"])
    truck_arrival = random_datetime_within_range()
    priority = pick_priority()
    sla_hours = INBOUND_SLA_HOURS[priority]
    ontime_prob = INBOUND_ONTIME_PROB[priority]
    is_on_time = random.random() < ontime_prob

    if is_on_time:
        max_inside = max(0.016, sla_hours * 0.7)
        receipt_delta_hours = random.uniform(1/60.0, max_inside)
    else:
        late_min = sla_hours * 1.05
        late_max = min(sla_hours * 5.0, 168.0)
        r = np.random.beta(a=1.5, b=4.0)
        receipt_delta_hours = late_min + r * (late_max - late_min)

    receipt_time = truck_arrival + hours_to_timedelta(receipt_delta_hours)

    putaway_delta_hours = random.uniform(PUTAWAY_MIN_HOURS, PUTAWAY_MAX_HOURS)
    putaway_time = receipt_time + hours_to_timedelta(putaway_delta_hours)

    part_id = random.choice(part_dim["Part_ID"].tolist())
    lpn_id = f"LPN{random.randint(100000,999999)}"
    qty = float(np.random.randint(1, 500))
    inbound_rows.append({
        "Order_ID": order_id,
        "Order_Line_ID": order_line_id,
        "Order_Type_ID": order_type,
        "Origin_Country": origin_country,
        "Truck_Arrival_Time": truck_arrival,
        "Receipt_Time": receipt_time,
        "Putaway_Time": putaway_time,
        "Part_ID": part_id,
        "LPN_ID": lpn_id,
        "Total_Order_Qty": qty,
        "Order_Priority_ID": priority
    })

inbound_fact = pd.DataFrame(inbound_rows)

outbound_rows = []
for i in range(num_orders_outbound):
    order_line_id = f"OL{str(i+1).zfill(7)}"
    order_id = f"OUT{random.randint(1000,9999)}"
    order_type = random.choice(order_type_dim[order_type_dim["Inbound_Outbound_Indicator"]=="Outbound"]["Order_Type_ID"].tolist())
    dest_country = random.choice(["US","MX","CA","BR","FR"])
    drop_time = random_datetime_within_range()
    priority = pick_priority()
    sla_hours = OUTBOUND_SLA_HOURS[priority]
    ontime_prob = OUTBOUND_ONTIME_PROB[priority]
    is_on_time = random.random() < ontime_prob

    if is_on_time:
        max_inside = max(0.016, sla_hours * 0.7)
        load_delta_hours = random.uniform(1/60.0, max_inside)
    else:
        late_min = sla_hours * 1.05
        late_max = min(sla_hours * 5.0, 168.0)
        r = np.random.beta(a=1.5, b=4.0)
        load_delta_hours = late_min + r * (late_max - late_min)

    load_time = drop_time + hours_to_timedelta(load_delta_hours)

    window_hours = max((load_time - drop_time).total_seconds() / 3600.0, 0.016)
    pick_frac = random.uniform(0.05, 0.45)
    pack_frac = random.uniform(pick_frac + 0.01, min(0.95, pick_frac + 0.45))
    pick_time = drop_time + hours_to_timedelta(window_hours * pick_frac)
    pack_time = drop_time + hours_to_timedelta(window_hours * pack_frac)
    if pack_time >= load_time:
        pack_time = load_time - hours_to_timedelta(1/60.0)

    ship_delta = random.uniform(SHIP_MIN_AFTER_LOAD_HOURS, SHIP_MAX_AFTER_LOAD_HOURS)
    ship_time = load_time + hours_to_timedelta(ship_delta)

    pick_location = random.choice(location_dim["Location_ID"].tolist())
    part_id = random.choice(part_dim["Part_ID"].tolist())
    lpn_id = f"LPN{random.randint(100000,999999)}"
    qty = float(np.random.randint(1, 500))

    outbound_rows.append({
        "Order_ID": order_id,
        "Order_Line_ID": order_line_id,
        "Order_Type_ID": order_type,
        "Destination_Country": dest_country,
        "Order_Drop_Time": drop_time,
        "Order_Pick_Time": pick_time,
        "Pick_Location_ID": pick_location,
        "Order_Pack_Time": pack_time,
        "Order_Load_Time": load_time,
        "Order_Ship_Time": ship_time,
        "Part_ID": part_id,
        "LPN_ID": lpn_id,
        "Total_Order_Qty": qty,
        "Order_Priority_ID": priority
    })

outbound_fact = pd.DataFrame(outbound_rows)

cycle_count_fact = pd.DataFrame({
    "Cycle_Count_ID": [f"CYC{str(i).zfill(6)}" for i in range(1, num_cycle_counts+1)],
    "Count_Type_ID": np.random.choice(count_type_dim["Count_Type_ID"], num_cycle_counts),
    "Part_ID": np.random.choice(part_dim["Part_ID"], num_cycle_counts),
    "LPN_ID": [f"LPN{random.randint(100000,999999)}" for _ in range(num_cycle_counts)],
    "Location_ID": np.random.choice(location_dim["Location_ID"], num_cycle_counts),
    "Count_Time": [random_datetime_within_range() for _ in range(num_cycle_counts)],
    "Expected_Qty": np.random.randint(1, 500, num_cycle_counts).astype(float),
    "Counted_Qty": np.random.randint(1, 500, num_cycle_counts).astype(float)
})

hours_fact = pd.DataFrame({
    "Hours_ID": [f"H{str(i).zfill(7)}" for i in range(1, num_hours+1)],
    "Employee_ID": np.random.choice(employee_dim["Employee_ID"], num_hours),
    "Function_ID": np.random.choice(function_dim["Function_ID"], num_hours),
    "Metric_ID": np.random.choice(metric_dim["Metric_ID"], num_hours),
    "Pay_ID": np.random.choice(pay_dim["Pay_ID"], num_hours),
    "Work_Date": [start_date + timedelta(days=random.randint(0, days_range)) for _ in range(num_hours)],
    "Clock_In_Time": [random_datetime_within_range() for _ in range(num_hours)],
    "Clock_Out_Time": [random_datetime_within_range() for _ in range(num_hours)],
    "Hours": np.round(np.random.uniform(2, 12, num_hours), 2)
})

###########################
####### WRITE TO DB #######
###########################
engine = create_engine(f"postgresql+psycopg2://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}")

tables = {
    "Order_Type_Dim": order_type_dim,
    "Count_Type_Dim": count_type_dim,
    "Part_Dim": part_dim,
    "Location_Dim": location_dim,
    "Employee_Dim": employee_dim,
    "Function_Dim": function_dim,
    "Pay_Dim": pay_dim,
    "Metric_Dim": metric_dim,
    "Inbound_Fact": inbound_fact,
    "Outbound_Fact": outbound_fact,
    "Cycle_Count_Fact": cycle_count_fact,
    "Hours_Fact": hours_fact
}

for name, df in tables.items():
    print(f"Loading {name} ({len(df)} rows) ...")
    df.to_sql(name, engine, if_exists="replace", index=False)
    print(f"Loaded {name}")

print("All tables generated and loaded into PostgreSQL.")