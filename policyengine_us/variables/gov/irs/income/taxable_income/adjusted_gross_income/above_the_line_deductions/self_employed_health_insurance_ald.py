from policyengine_us.model_api import *


class self_employed_health_insurance_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed health insurance ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction for the head's and spouse's self-employed "
        "health insurance (Schedule 1, line 17). A tax unit dependent who is "
        "self-employed takes this deduction, limited to their own earned "
        "income, on their own return."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/162#l"

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(
            "self_employed_health_insurance_ald_person", tax_unit, period
        )
