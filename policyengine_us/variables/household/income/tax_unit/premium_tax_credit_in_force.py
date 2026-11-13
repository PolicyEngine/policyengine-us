from policyengine_us.model_api import *


class premium_tax_credit_in_force(Variable):
    value_type = float
    entity = TaxUnit
    label = "premium tax credit counted in household net income"
    documentation = (
        "The premium tax credit, a refundable federal income tax credit "
        "(26 U.S.C. 36B), as household net income counts it: the credit the "
        "tax unit uses, which 36B(b)(2) limits to the premiums of the plan "
        "it enrolls in and which is zero for a tax unit that doesn't enroll. "
        "Like the other federal refundable credits, it is zero in a year the "
        "federal income tax is abolished."
    )
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/36B#b_2"
    defined_for = "federal_income_tax_in_force"
    adds = ["used_aca_ptc"]
