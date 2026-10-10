from policyengine_us.model_api import *


class al_estate_and_trust_income(Variable):
    value_type = float
    entity = Person
    label = "Alabama estate and trust income"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://alison.legislature.state.al.us/code-of-alabama?section=40-18-25",
        "https://admincode.legislature.state.al.us/administrative-code/810-3-25",
        # PDF pages 15, 24
        "https://www.revenue.alabama.gov/wp-content/uploads/2026/01/25f40bk.pdf#page=15",
    )
    defined_for = StateCode.AL

    def formula(person, period, parameters):
        # A beneficiary reports their share of estate or trust income on
        # Form 40, Part I, line 5 (Schedule E, Part II). Code of Ala.
        # § 40-18-25(b)(4) switches off IRC § 642(h), so the excess deductions
        # and loss carryovers an estate or trust passes to beneficiaries on
        # termination do not reach them, and Ala. Admin. Code r.
        # 810-3-25-.05(8)(b) bars passing an irrevocable trust's loss on.
        # Only income flows through.
        return max_(0, person("estate_income", period))
