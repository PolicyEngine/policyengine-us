from typing import Callable, Tuple

from numpy.typing import ArrayLike
from policyengine_core.parameters import ParameterNode
from policyengine_core.periods import Period
from policyengine_core.populations import Population

Formula = Callable[[Tuple[Population, Period, ParameterNode]], ArrayLike]
