from datetime import datetime


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
        param_space: {
            ...
        },
    }

    """

    def __init__(self, mongodb):
        super().__init__()

        self._mongodb = mongodb
        self.collection = mongodb.trialqueue

    def next_trial(self):
        """
        Takes the next trial from the database.
        """
        t = datetime.utcnow()
        job = self.collection.find_and_modify(
            query={'start_time': -1},
            sort=[('priority', -1), ('created_on', 1)],
            update={'$set': {'start_time': t}},
            new=True
        )
        return job
