from numpy.typing import ArrayLike
from typing import Callable, Tuple
from policyengine_core.populations import Population
from policyengine_core.periods import Period
from policyengine_core.parameters import ParameterNode

Formula = Callable[[Tuple[Population, Period, ParameterNode]], ArrayLike]
