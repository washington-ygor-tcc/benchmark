from typing import Callable, Dict, Any, Generator


Total = int
Current = int
Id = int | str
Features = Dict[str, Any]
Prediction = Dict[str, Any]
RequestGenerator = Generator[Features, None, None]
ProgressIndicator = Callable[[Current, Total], None]
