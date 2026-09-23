import os

DB_NAME = "potholes.db"

if os.path.exists(DB_NAME):
    os.remove(DB_NAME)
    print("Old potholes.db deleted successfully.")
else:
    print("No existing potholes.db was found.")

print("Start RoadPulse again. A new database will be created automatically.")
