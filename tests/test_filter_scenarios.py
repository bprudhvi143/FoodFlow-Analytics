"""
Automated validation of the 5 requested filter combinations against FastAPI backend.
"""

import urllib.request
import urllib.parse
import json

BASE_URL = "http://localhost:8000/api/analytics/overview"

def fetch_overview(params=None):
    if params:
        query = urllib.parse.urlencode({k: v for k, v in params.items() if v})
        url = f"{BASE_URL}?{query}"
    else:
        url = BASE_URL
    req = urllib.request.urlopen(url)
    return json.loads(req.read().decode())

def run_tests():
    print("===============================================================")
    print("STEP 6 ANALYTICS FILTER VALIDATION RESULTS")
    print("===============================================================\n")

    # Test 1: City = Cairo
    p1 = {"city": "Cairo"}
    res1 = fetch_overview(p1)
    print(f"TEST 1: City = Cairo")
    print(f"  - Total Orders: {res1['total_orders']:,}")
    print(f"  - Delivered Orders: {res1['delivered_orders']:,}")
    print(f"  - Fulfillment Rate: {res1['delivery_completion_rate']}%")
    print(f"  - Delay Rate: {res1['delay_rate']}%")
    print(f"  - Avg Duration: {res1['average_delivery_duration']} min")
    print(f"  - Avg Order Value: EGP {res1['average_order_value']}\n")

    # Test 2: Traffic Level = Medium
    p2 = {"traffic_level": "Medium"}
    res2 = fetch_overview(p2)
    print(f"TEST 2: Traffic Level = Medium")
    print(f"  - Total Orders: {res2['total_orders']:,}")
    print(f"  - Delivered Orders: {res2['delivered_orders']:,}")
    print(f"  - Fulfillment Rate: {res2['delivery_completion_rate']}%")
    print(f"  - Delay Rate: {res2['delay_rate']}%")
    print(f"  - Avg Duration: {res2['average_delivery_duration']} min")
    print(f"  - Avg Order Value: EGP {res2['average_order_value']}\n")

    # Test 3: City = Cairo + Traffic = Medium + Vehicle = Motorbike
    p3 = {"city": "Cairo", "traffic_level": "Medium", "vehicle": "Motorbike"}
    res3 = fetch_overview(p3)
    print(f"TEST 3: City = Cairo + Traffic = Medium + Vehicle = Motorbike")
    print(f"  - Total Orders: {res3['total_orders']:,}")
    print(f"  - Delivered Orders: {res3['delivered_orders']:,}")
    print(f"  - Fulfillment Rate: {res3['delivery_completion_rate']}%")
    print(f"  - Delay Rate: {res3['delay_rate']}%")
    print(f"  - Avg Duration: {res3['average_delivery_duration']} min")
    print(f"  - Avg Order Value: EGP {res3['average_order_value']}\n")

    # Test 4: Zero result combination
    p4 = {
        "city": "Alexandria",
        "vehicle": "Bicycle",
        "order_value_tier": "Luxury (>500)",
        "distance_bin": "Very Long (>5km)"
    }
    res4 = fetch_overview(p4)
    print(f"TEST 4: Zero Results Combination ({p4})")
    print(f"  - Total Orders: {res4['total_orders']:,}")
    print(f"  - Delivered Orders: {res4['delivered_orders']:,}")
    print(f"  - Delay Rate: {res4['delay_rate']}%")
    print(f"  - Avg Duration: {res4['average_delivery_duration']} min\n")

    # Test 5: Reset Filters (Full dataset baseline)
    p5 = {}
    res5 = fetch_overview(p5)
    print(f"TEST 5: Reset Filters (Complete Dataset Baseline)")
    print(f"  - Total Orders: {res5['total_orders']:,}")
    print(f"  - Delivered Orders: {res5['delivered_orders']:,}")
    print(f"  - Fulfillment Rate: {res5['delivery_completion_rate']}%")
    print(f"  - Delay Rate: {res5['delay_rate']}%")
    print(f"  - Avg Duration: {res5['average_delivery_duration']} min")
    print(f"  - Avg Order Value: EGP {res5['average_order_value']}\n")

if __name__ == "__main__":
    run_tests()
