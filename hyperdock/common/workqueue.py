from datetime import datetime, timedelta

from bson.objectid import ObjectId

WORK_TIMEOUT = 300


class WorkQueue:
    """
    A simple MongoDB priority work queue that handles the queue
    of experiment.
    """

    def __init__(self, mongodb):
        super().__init__()

        self._mongodb = mongodb
        self.collection = mongodb.workqueue

    def assign_next_job(self, worker_id):
        """
        Assigns the next free job to worker.
        Returns the object from the mongodb.
        """
        t = datetime.utcnow()
        job = self.collection.find_and_modify(
            query={'start_time': -1, 'cancelled': False},
            sort=[('priority', -1), ('created_on', 1)],
            update={'$set': {'start_time': t,
                             'last_update': t,
                             'worker': worker_id}},
            new=True
        )
        return job

    def add_job(self, parameters, data, trial_id, trial_name, priority=0):
        """
        Adds new work to the workqueue.
        """
        id = self.collection.insert({
            'start_time': -1,
            'end_time': -1,
            'last_update': -1,
            'created_on': datetime.utcnow(),
            'priority': priority,
            'parameters': parameters,
            'data': data,
            'worker': None,
            'result': {},
            'trial': trial_id,
            'trial_name': trial_name,
            '_id': str(ObjectId()),
            'cancelled': False,
        })
        return id

    def update_job(self, _id, update=None):
        """
        Marks the job as alive and post an update from the job.
        """
        t = datetime.utcnow()
        self.collection.update({'_id': _id}, {'$set': {'last_update': t,
                                                       'update': update}})

    def is_job_cancelled(self, _id):
        """
        Checks if a certain job has been explicitly cancelled.
        """
        return (self.collection.find_one({'_id': _id, 'cancelled': True})
                is not None)

    def finish_job(self, _id, result):
        """
        Marks the job as finished and attach the result.
        """
        t = datetime.utcnow()
        self.collection.update_one({'_id': _id}, {'$set':
                                                  {'end_time': t,
                                                   'last_update': t,
                                                   'result': result}})

    def purge_dead_jobs(self):
        """
        Returns jobs that have timed out due to worker death and cancel them.
        """
        now = datetime.utcnow()
        deadline = now - timedelta(seconds=WORK_TIMEOUT)
        jobs = []
        while True:
            job = self.collection.find_and_modify(
                query={'start_time': {'$ne': -1},
                       'end_time': -1,
                       'last_update': {'$lt': deadline}},
                sort=[('priority', -1), ('last_update', 1)],
                update={'$set': {'cancelled': True,
                                 'last_update': now,
                                 'end_time': now,
                                 'result': {'state': 'fail', 'msg': 'Timed out!'},
                        }},
                new=True)

            if job is not None:
                jobs.append(job)
            else:
                return jobs
