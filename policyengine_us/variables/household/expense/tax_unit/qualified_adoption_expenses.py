from policyengine_us.model_api import *


class qualified_adoption_expenses(Variable):
    value_type = float
    entity = TaxUnit
    label = "Qualified adoption expenses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Unreimbursed qualifying adoption expenses including medical and "
        "hospital costs, adoption counseling fees, legal fees, agency fees, "
        "and other nonrecurring costs directly related to the legal adoption "
        "of a child. Used by state adoption tax benefits. For federal adoption "
        "credit and exclusion purposes, see qualified_adoption_assistance_expense."
    )
    reference = "https://www.law.cornell.edu/uscode/text/26/23#d"
