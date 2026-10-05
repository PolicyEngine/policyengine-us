from policyengine_us.model_api import *


class ny_agi(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY adjusted gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/new-york/20-NYCRR-132.1"
    defined_for = StateCode.NY

    adds = ["adjusted_gross_income", "ny_additions"]
    subtracts = ["ny_agi_subtractions"]
