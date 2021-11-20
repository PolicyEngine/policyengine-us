from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *


class ssi(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income"

    def formula(person, period, parameters):
        # Obtain eligibility.
        eligible = person("is_ssi_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = person("ssi_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)


class is_ssi_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    documentation = "Eligibility for Supplemental Security Income"


class ssi_amount_if_eligible(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    documentation = "Supplemental Security Income amount if someone is eligible"