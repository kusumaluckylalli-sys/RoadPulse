def calculate_priority(size, depth, road_type, traffic_problem, accident_reported, pothole_count, water_filled, urgency):
    score = 0

    score += {"Large": 30, "Medium": 20, "Small": 10}.get(size, 0)
    score += {"Deep": 30, "Moderate": 20, "Shallow": 10}.get(depth, 0)

    if road_type in ["Highway", "Main Road"]:
        score += 20
    elif road_type in ["School Zone", "Hospital Area"]:
        score += 15
    elif road_type == "Market Area":
        score += 10
    else:
        score += 5

    score += {"Yes": 10, "Sometimes": 5, "No": 0}.get(traffic_problem, 0)
    score += 10 if accident_reported == "Yes" else 0
    score += {"More than 5": 10, "2-5": 5, "1": 0}.get(pothole_count, 0)
    score += 5 if water_filled == "Yes" else 0
    score += int(urgency) * 2

    if score >= 70:
        level = "High"
    elif score >= 40:
        level = "Medium"
    else:
        level = "Low"
    return score, level
