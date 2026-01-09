from policyengine_us.model_api import *


class pre_subsidy_qualified_adoption_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Pre-subsidy qualified adoption expenses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Unreimbursed qualifying adoption expenses including medical and "
        "hospital costs, adoption counseling fees, legal fees, agency fees, "
        "and other nonrecurring costs directly related to the legal adoption "
        "of a child, before any subsidies or tax benefits are applied."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/23#d"
