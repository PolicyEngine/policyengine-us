from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class ssdi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Social Security Disability Insurance amount"
    label = "Social Security Disability Insurance"
