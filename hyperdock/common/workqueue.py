from datetime import datetime


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
            query={'start_time': -1},
            sort=[('priority', -1), ('created_on', 1)],
            update={'$set': {'start_time': t,
                             'last_update': t,
                             'worker': worker_id}},
            new=True
        )
        return job

    def add_job(self, payload, priority=0):
        """
        Adds new work to the workqueue.
        """
        id = self.collection.insert({
            'start_time': -1,
            'end_time': -1,
            'last_update': -1,
            'created_on': datetime.utcnow(),
            'priority': priority,
            'payload': payload,
            'worker': None,
            'result': {},
        })
        return id

    def update_job(self, _id):
        """
        Marks the job as alive.
        """
        t = datetime.utcnow()
        self.collection.update({'_id': _id}, {'$set': {'last_update': t}})

    def finish_job(self, _id, result):
        """
        Marks the job as finished and attach the result.
        """
        t = datetime.utcnow()
        self.collection.update_one({'_id': _id}, {'$set':
                                                  {'end_time': t,
                                                   'last_update': t,
                                                   'result': result}})