from pathlib import Path
from openfisca_core.parameters import ParameterNode

default_parameters = ParameterNode(directory_path=Path(__file__).parent)
