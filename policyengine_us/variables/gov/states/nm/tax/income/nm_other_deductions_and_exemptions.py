from policyengine_us.model_api import *


class nm_other_deductions_and_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico other income deductions and subtractions"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM

    adds = "gov.states.nm.tax.income.other_deductions_and_exemptions"
