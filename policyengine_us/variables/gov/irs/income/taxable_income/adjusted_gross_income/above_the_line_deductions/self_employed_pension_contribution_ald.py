from policyengine_us.model_api import *


class self_employed_pension_contribution_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Self-employed pension contribution ALD"
    unit = USD
    documentation = (
        "Above-the-line deduction for the head's and spouse's self-employed "
        "SEP, SIMPLE and qualified plan contributions (Schedule 1, line 16). "
        "A tax unit dependent who is self-employed takes this deduction on "
        "their own return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_6",
        "https://www.law.cornell.edu/uscode/text/26/404",
    )

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(
            "self_employed_pension_contribution_ald_person", tax_unit, period
        )
