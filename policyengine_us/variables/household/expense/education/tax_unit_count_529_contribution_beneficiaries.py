from policyengine_us.model_api import *


class tax_unit_count_529_contribution_beneficiaries(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of beneficiaries to the head's and spouse's 529 plan contributions"
    documentation = (
        "The head's and spouse's counts of the beneficiaries of their 529 plan "
        "contributions, added together. A dependent's count is for their own "
        "contributions and is left out."
    )
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        return tax_unit_non_dep_sum(
            "count_529_contribution_beneficiaries", tax_unit, period
        )
