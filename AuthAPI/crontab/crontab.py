from AuthAPI import app, db, celery, config, common
from AuthAPI import redis_client
from datetime import datetime
from celery.schedules import crontab
from dateutil import parser

@celery.on_after_configure.connect
def setup_tasks(sender, **kwargs):

    sender.add_periodic_task(
        crontab(minute='*/1'),
        checkRedis.s()
    )

@celery.task
def checkRedis():
    # """Background task to send an email with Flask-Mail."""
    for key in redis_client.scan_iter():
        time_logout = parser.parse(redis_client.get(key))
        if((datetime.now() - time_logout).seconds > 86400):
            redis_client.delete(key)