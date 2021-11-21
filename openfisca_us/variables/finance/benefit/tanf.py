from openfisca_core.model_api import *
from openfisca_us.entities import *
from openfisca_us.tools.general import *
from openfisca_us.variables.demographic.person import *


class tanf(Variable):
    value_type = float
    entity = Family
    definition_period = MONTH
    label = "Temporary Assistance for Needy Families"
    documentation = "Amount of Temporary Assistance for Needy Families benefit received."
    unit = "currency-USD"

    def formula(person, period, parameters):
        # Obtain eligibility.
        eligible = person("is_tanf_eligible", period)
        # Obtain amount they would receive if they were eligible.
        amount_if_eligible = person("tanf_amount_if_eligible", period)
        return where(eligible, amount_if_eligible, 0)


class is_tanf_eligible(Variable):
    value_type = bool
    entity = Family
    definition_period = MONTH
    label = "Eligibility for Temporary Assistance for Needy Families"
    documentation = "Whether the family is eligible for Temporary Assistance for Needy Families benefit."

class tanf_amount_if_eligible(Variable):
    value_type = float
    entity = Family
    definition_period = MONTH
    label = "Temporary Assistance for Needy Families amount if family is eligible"
    documentation = "How much a family would receive if they were eligible for Temporary Assistance for Needy Families benefit."
    unit = "currency-USD"
