from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.nj.tax.income.adjusted_gross_income.claim_of_right.nj_claim_of_right_repayment_category import (
    CATEGORY_SOURCES,
    nj_claim_of_right_category_offset,
)


class nj_claim_of_right_offset(Variable):
    value_type = float
    entity = Person
    label = "New Jersey claim of right repayment offset"
    unit = USD
    documentation = (
        "Reduction in a person's New Jersey gross income for a claim of "
        "right repayment. New Jersey applies a repayment against income of "
        "the same category in the year of repayment, and a category with a "
        "net negative amount is reported as zero. A repayment offsets the "
        "repayer's own taxable income in the category first; on a joint "
        "return any excess offsets the other spouse's. New Jersey has no "
        "counterpart to the section 1341 credit, so the federal method does "
        "not matter."
    )
    definition_period = YEAR
    reference = (
        # N.J.S.A. 54A:5-2
        "https://lis.njleg.state.nj.us/nxt/gateway.dll/statutes/1/53569/53634",
        # TAM 2011-7, Claim of Right Repayment Refunds (IRC 1341)
        "https://www.nj.gov/treasury/taxation/pdf/pubs/tams/tam7.pdf",
    )
    defined_for = StateCode.NJ

    def formula(person, period, parameters):
        offset = 0
        for category in CATEGORY_SOURCES:
            offset = offset + nj_claim_of_right_category_offset(
                person, period, parameters, category
            )
        return offset
