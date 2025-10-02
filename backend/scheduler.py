from apscheduler.schedulers.blocking import BlockingScheduler
from services.spacetrack_service import fetch_and_cache_debris_data

def scheduled_job():
    print("Running scheduled job: Fetching latest debris data...")
    fetch_and_cache_debris_data()
    print("Job finished.")

if __name__ == "__main__":
    scheduler = BlockingScheduler()
    # Schedule job to run every 4 hours
    scheduler.add_job(scheduled_job, 'interval', hours=4)
    
    print("Scheduler started. Running the job once immediately.")
    # Run the job once on startup
    scheduled_job()
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass