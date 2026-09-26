from policyengine_us.model_api import *


class estate_tax_credit(Variable):
    value_type = float
    entity = Person
    label = "Estate tax credit"
    documentation = (
        "Applicable credit amount (unified credit) against the estate tax: "
        "the tentative tax under the section 2001(c) rate schedule on the "
        "applicable exclusion amount, which is the basic exclusion amount "
        "plus any deceased spousal unused exclusion amount."
    )
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/2010#c",
        "https://www.law.cornell.edu/uscode/text/26/2001#c",
        "https://www.irs.gov/pub/irs-prior/i706--2024.pdf#page=9",
    )
    defined_for = "is_deceased"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs
        # 26 U.S.C. 2010(c)(2): the applicable exclusion amount is the basic
        # exclusion amount plus any deceased spousal unused exclusion amount.
        applicable_exclusion_amount = p.credits.estate.base + person(
            "deceased_spousal_unused_exclusion_amount", period
        )
        # 26 U.S.C. 2010(c)(1): the applicable credit amount is the tentative
        # tax that the section 2001(c) rate schedule would impose on the
        # applicable exclusion amount.
        return p.tax.estate.rate.calc(applicable_exclusion_amount)
