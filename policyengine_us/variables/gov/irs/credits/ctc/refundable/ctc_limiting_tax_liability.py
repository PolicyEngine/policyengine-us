from policyengine_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = (
        "The tax liability that limits the non-refundable CTC: income tax "
        "before credits, less non-refundable credits other than the CTC."
    )
    definition_period = YEAR
    reference = [
        # Regular tax liability limits the aggregate of nonrefundable credits.
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        "https://www.law.cornell.edu/uscode/text/26/26#b_1",
        # The refundable portion is measured against the same limitation.
        "https://www.law.cornell.edu/uscode/text/26/24#d_1",
        # Schedule 8812 Credit Limit Worksheet A.
        "https://www.irs.gov/instructions/i1040s8",
    ]

    def formula(tax_unit, period, parameters):
        # Actual liability, including any SALT deduction. This used to be
        # evaluated on a "no_salt" branch to avoid a circular dependency, but
        # the SALT deduction's income tax component now comes from
        # state_withheld_income_tax (an AGI-based estimate) and
        # local_income_tax, neither of which depends on the federal CTC. The
        # branch also inherited whatever the parent simulation had already
        # cached, so its value depended on which variables were requested
        # first.
        tax_liability_before_credits = tax_unit("income_tax_before_credits", period)
        non_refundable_credits = parameters(period).gov.irs.credits.non_refundable
        non_refundable_credits_ex_ctc = [
            x for x in non_refundable_credits if x != "non_refundable_ctc"
        ]
        total_credits = add(tax_unit, period, non_refundable_credits_ex_ctc)

        return max_(0, tax_liability_before_credits - total_credits)
