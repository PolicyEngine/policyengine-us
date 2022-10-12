from numpy.typing import ArrayLike
from typing import Callable, Tuple
from openfisca_core.populations import Population
from openfisca_core.periods import Period
from openfisca_core.parameters import ParameterNode

Formula = Callable[[Tuple[Population, Period, ParameterNode]], ArrayLike]
