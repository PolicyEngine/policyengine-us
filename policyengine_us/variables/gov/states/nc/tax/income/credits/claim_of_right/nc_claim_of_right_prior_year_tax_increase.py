from policyengine_us.model_api import *


class nc_claim_of_right_prior_year_tax_increase(Variable):
    value_type = float
    entity = Person
    label = "North Carolina prior-year tax increase from restored claim of right income"
    unit = USD
    documentation = (
        "Amount by which North Carolina individual income tax for the earlier "
        "year or years increased because the income repaid this year "
        "(claim_of_right_repayment) was included in gross income for that "
        "year. The tax unit uses the sum for its head and spouse."
    )
    definition_period = YEAR
    reference = "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-266.2.html"
    defined_for = StateCode.NC
