import csv

from contextlib import contextmanager
from typing import List

from benchmark.core.ports.metric_repository_port import MetricRepositoryPort
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.types import Id


HEADERS = ["benchmark_id", "request_id", "start", "end"]


class MetricRepositoryAdapter(MetricRepositoryPort):
    def __init__(self, filename: str):
        self.filename = filename

    @contextmanager
    def __open(self):
        with open(self.filename, "a+") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(HEADERS)
            yield writer

    def save(
        self, benchmark_id: Id, benchmark_results: List[PredictionRequest]
    ) -> None:
        with self.__open() as csvfile:
            for request in benchmark_results:
                csvfile.writerow(
                    [
                        benchmark_id,
                        request.request_id,
                        request.start,
                        request.end,
                    ]
                )
