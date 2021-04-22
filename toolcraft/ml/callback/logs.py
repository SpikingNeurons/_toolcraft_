import typing as t


class EpochStartLogs:
    """
    Currently no fields here but that may change in the future.
    """
    ...


class EpochEndLogs:
    """
    metric results for this training epoch,  and for the validation epoch if
    validation is performed.
    """
    
    def __init__(
        self,
        fit_results: t.Dict,
        validate_results: t.Optional[t.Dict],
    ):
        self.fit_results = fit_results
        self.validate_results = validate_results
        
        
class PhaseStartLogs:
    """
    Currently no fields here but that may change in the future.
    """
    ...
    
    
class PhaseEndLogs:
    """
    Currently no fields here but that may change in the future.
    """
    ...
        
        
class BatchStartLogs:
    """
    Has key `batch` representing the current batch number in a epoch ...
    """
    def __init__(self, batch: int):
        self.batch = batch
        
        
class BatchEndLogs:
    """
    Metric results for this batch
    """
    def __init__(self, batch_results: t.Dict):
        self.batch_results = batch_results
