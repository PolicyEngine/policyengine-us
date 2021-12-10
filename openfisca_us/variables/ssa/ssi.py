from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *


class is_ssi_disabled(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Indicates whether a person is disabled for the Supplemental Security Income program"
    label = "SSI disabled"
