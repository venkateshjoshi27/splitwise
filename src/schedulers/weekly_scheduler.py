# scheduling.py

import schedule
import time
from service import helpers

class Scheduler:
    @staticmethod
    def schedule_task():
        # Schedule the task to run every Monday at 11 AM
        schedule.every().monday.at("11:00").do(helpers.weekly_report)

    @staticmethod
    def run_scheduler():
        # Continuously check and run scheduled tasks
        while True:
            schedule.run_pending()
            time.sleep(1)  # Sleep for 1 second to prevent high CPU usage
