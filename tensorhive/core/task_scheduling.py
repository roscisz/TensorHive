from tensorhive.core import task_nursery
from tensorhive.controllers.task import spawn, terminate, synchronize
from tensorhive.models.Task import Task, TaskStatus
from tensorhive.models.User import User
from tensorhive.models.Role import Role
from sqlalchemy import and_, not_, or_, between
from datetime import datetime
import threading
import sched
import time

# require that terminate_at must be after spawns_at
# FIXME Relies on controller (sync, exceptions)


def spawn_scheduled(now: datetime):
    is_scheduled = Task.spawn_at is not None
    before_terminate = or_(Task.terminate_at is None, Task.spawn_at < Task.terminate_at)
    can_spawn_now = Task.spawn_at < now
    tasks_to_spawn = Task.query.filter(is_scheduled, before_terminate, can_spawn_now).all()

    print('{} tasks should be running.'.format(len(tasks_to_spawn)))
    for task in tasks_to_spawn:
        print(task.spawn_at, task.terminate_at)
        print('Now: {} | Spawning task scheduled for {}'.format(
            now.strftime("%H:%M:%S"), task.spawn_at.strftime("%H:%M:%S")))
        content, status = spawn(task.id)
        if status == 200:
            print(content['pid'])
        else:
            print(content['msg'])


def terminate_scheduled(now: datetime):
    is_scheduled = Task.terminate_at is not None
    after_spawn = or_(Task.spawn_at < Task.terminate_at, Task.spawn_at is None)
    can_terminate_now = Task.terminate_at < now
    tasks_to_terminate = Task.query.filter(is_scheduled, after_spawn, can_terminate_now).all()

    print('{} tasks should be terminated.'.format(len(tasks_to_terminate)))
    for task in tasks_to_terminate:
        print(task.spawn_at, task.terminate_at)
        print('Now: {} | Terminating task scheduled for {}'.format(
            now.strftime("%H:%M:%S"), task.terminate_at.strftime("%H:%M:%S")))
        content, status = terminate(task.id)
        if status == 201:
            print(content['exit_code'])
        else:
            print(content['msg'])


def run_scheduler():
    while True:
        print()
        print('Waking up...')
        now = datetime.utcnow()
        print('=====================================')
        spawn_scheduled(now)
        print('=====================================')
        terminate_scheduled(now)
        print('=====================================')
        print('Going to sleep...')
        time.sleep(5)


t = threading.Thread(target=run_scheduler)
t.start()

# def pooling_scheduler(scheduler):
#     while True:
#         print('Pool started, checking queue...')
#         if not scheduler.empty():
#             scheduler.run()
#         else:
#             print('Queue empty, nothing to run')
#         print('Done, next pool for new events in 5s...')
#         time.sleep(5)

# # Run scheduler loop in thread, so it listens for new events added to queue
# scheduler = sched.scheduler(time.time, time.sleep)
# t = threading.Thread(target=pooling_scheduler, args=(scheduler, ))
# t.start()

# # Emulates real spawn method
# def spawn_mock(scheduled_for):
#     now = datetime.datetime.now().strftime("%H:%M:%S")
#     print('Now: {} | Spawning task scheduled for {}'.format(now, scheduled_for))
#     time.sleep(2)

# # Multiple users wants to schedule their tasks
# # We add them to scheduler's queue
# # Spawn following the rules of FIFO
# now = time.time()
# print('Adding 10 events to scheduler...')
# for offset in range(10):
#     scheduled_for = datetime.datetime.now() + datetime.timedelta(seconds=offset)
#     scheduled_for = scheduled_for.strftime("%H:%M:%S")

#     # Schedule spawns in 1s intervals
#     # All tasks have same priority
#     scheduler.enterabs(now + offset, priority=1, action=spawn_mock, argument=(scheduled_for, ))

# print('Noone wants to schedule task for 5s...')
# time.sleep(5)
# # Scheduler should execute some of queued events and get them done until this point
# # But queue won't be empty here

# # Adding new event to queue
# print('Now someone wants to schedule some spawn')
# now = time.time()
# try:
#     priorities = [event.priority for event in scheduler.queue]
#     lowest_priority = max(priorities) + 2
# except IndexError:
#     lowest_priority = 0
# scheduler.enterabs(
#     now, priority=lowest_priority, action=spawn_mock, argument=('last request ' + str(lowest_priority), ))
