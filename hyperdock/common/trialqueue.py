from datetime import datetime

from .utils import send_notifiction

class TrialQueue:
    """
    A simple MongoDB priority work queue that handles the queue
    of trials.

    A trial has the format:
    {
        start_time: <date>,
        end_time: <date>,
        created_on: <date>,
        priority: <int>,
        data: <dict>,
        param_space: {
            ...
        },
    }

    """

    def __init__(self, mongodb):
        super().__init__()

        self._mongodb = mongodb
        self._collection = mongodb.trialqueue

    def next_trial(self):
        """
        Takes the next trial from the database.
        """
        t = datetime.utcnow()
        trial = self._collection.find_and_modify(
            query={'start_time': -1},
            sort=[('priority', -1), ('created_on', 1)],
            update={'$set': {'start_time': t}},
            new=True
        )
        return trial

    def update_trials(self):
        """
        Call this periodically to mark Trials as finished.
        """
        end_time = datetime.utcnow()
        trials = self._collection.find({'end_time': -1})
        for trial in iter(trials):
            trial_id = trial['_id']
            unfinished_jobs = self._mongodb.workqueue.find({'trial': trial_id,
                                                            'end_time': -1}).count()
            if unfinished_jobs == 0:
                self._collection.update_one(
                    {'end_time': -1, '_id': trial_id},
                    {'$set': {'end_time': end_time}}
                )

                send_notifiction('Trial finished', trial['name'])

    def use_retry_ticket(self, trial_id):
        """
        Checks if the trial has retries left. If so, it decreases the counter
        and returns True, else return False.
        """
        trial = self._collection.find_and_modify(
            query={'_id': trial_id, 'retries': {'$gt': 0}},
            update={'$inc': {'retries': -1}},
            new=True
        )
        return True if trial is not None else False

    def get_trial(self, trial_id):
        """
        Retrieves the trial by id.
        """
        return self._collection.find_one({'_id': trial_id})
