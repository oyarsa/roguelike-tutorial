"""Auxiliary types to pass `mypy --strict` typechecking."""
from typing import Any

import numpy as np

# Everyone under the sun uses `np.ndarray` without the parameters, but mypy strict
# requires every type parameter to be specified. This is good overall, but a PIA here.
ndarray = np.ndarray[Any, Any]
