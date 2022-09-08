import csv
from datetime import datetime
from benchmark.core.ports.metric_repository_port import MetricRepositoryPort
from benchmark.core.domain.prediction_request import PredictionRequest
from benchmark.core.types import Id


class MetricRepositoryAdapter(MetricRepositoryPort):
    @staticmethod
    def save(benchmark_id: Id, benchmark_results: PredictionRequest) -> None:
        date_fmt = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
        with open(f"{date_fmt}_{benchmark_id}.csv", "w") as csvfile:
            writer = csv.writer(csvfile, delimiter=",")
            writer.writerow(["benchmark_id", "request_id", "start", "end"])
            for request in benchmark_results:
                writer.writerow(
                    [
                        benchmark_id,
                        request.request_id,
                        request.start,
                        request.end,
                    ]
                )
