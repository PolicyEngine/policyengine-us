from policyengine_us.model_api import *


class nm_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico income exemptions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = "gov.states.nm.tax.income.exemptions.exemptions"
