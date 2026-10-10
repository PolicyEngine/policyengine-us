from policyengine_us.model_api import *


class va_claim_of_right_prior_year_tax_decrease(Variable):
    value_type = float
    entity = Person
    label = "Virginia prior-year tax attributable to repaid claim of right income"
    unit = USD
    documentation = (
        "Virginia income tax for the earlier year or years that was "
        "attributable to including the income repaid this year "
        "(claim_of_right_repayment): the Virginia tax consequences of the "
        "repayment, computed on the schedule the filer attaches to the "
        "return. The tax unit uses the sum for its head and spouse."
    )
    definition_period = YEAR
    reference = (
        "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/16-183",
        "https://www.tax.virginia.gov/laws-rules-decisions/rulings-tax-commissioner/20-35",
    )
    defined_for = StateCode.VA
