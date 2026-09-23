import db

reports = db.get_all_potholes()

print("Total reports:", len(reports))

print("\n--- Pothole Reports ---")

for report in reports:
    print(report)