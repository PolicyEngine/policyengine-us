from policyengine_us.model_api import *


class nc_claim_of_right_prior_year_tax_increase(Variable):
    value_type = float
    entity = TaxUnit
    label = "North Carolina prior-year tax increase from restored claim of right income"
    unit = USD
    documentation = (
        "Amount by which the filers' North Carolina individual income tax "
        "(Article 4 of Chapter 105) for the earlier year or years was "
        "increased because the income they repaid this year "
        "(claim_of_right_repayment) was included in gross income for that "
        "year."
    )
    definition_period = YEAR
    reference = "https://www.ncleg.gov/EnactedLegislation/Statutes/HTML/BySection/Chapter_105/GS_105-266.2.html"
    defined_for = StateCode.NC
