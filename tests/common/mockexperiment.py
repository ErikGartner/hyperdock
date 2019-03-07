from hyperdock.common.experiment import Experiment


class MockExperiment(Experiment):
    """
    A mock experiment that doesn't actually run any experiment.
    It runs for one check then finishes. Returns a loss of 1.0.
    """

    def __init__(self, job, worker_env, privileged):
        super().__init__(job, worker_env)
        self.running = False
        self.failure = False

    def start(self):
        self.running = True
        self.failure = False

    def is_running(self):
        r = self.running
        self.running = False
        return r

    def stop(self):
        self.running = False
        self.failure = True

    def get_result(self):
        state = "ok" if not self.failure else "failure"
        return {"loss": 1.0, "state": state}

    def cleanup(self):
        self.running = False
