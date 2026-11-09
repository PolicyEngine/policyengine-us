from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.tax.income.adjusted_gross_income.claim_of_right.nj_claim_of_right_repayment_category import (
    NJClaimOfRightRepaymentCategory,
    nj_claim_of_right_category_offset,
)


class nj_claim_of_right_wage_offset(Variable):
    value_type = float
    entity = Person
    label = "New Jersey claim of right offset against wages"
    unit = USD
    documentation = (
        "The part of nj_claim_of_right_offset that reduces the person's "
        "wages (NJ-1040 line 15), which Worksheet D's earned income test "
        "reads."
    )
    definition_period = YEAR
    reference = (
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tams/tam7.pdf",
        # 2025 NJ-1040 instructions, Worksheet D line 4
        "https://www.nj.gov/treasury/taxation/pdf/current/1040i.pdf#page=23",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        return nj_claim_of_right_category_offset(
            person, period, parameters, NJClaimOfRightRepaymentCategory.WAGES
        )
