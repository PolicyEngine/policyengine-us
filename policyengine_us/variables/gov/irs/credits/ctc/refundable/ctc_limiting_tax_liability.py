from policyengine_us.model_api import *


class ctc_limiting_tax_liability(Variable):
    value_type = float
    entity = TaxUnit
    label = "CTC-limiting tax liability"
    unit = USD
    documentation = (
        "The tax liability that limits the non-refundable Child Tax Credit: "
        "income tax before credits (regular tax plus alternative minimum tax), "
        "less the other non-refundable credits."
    )
    definition_period = YEAR
    reference = (
        # 26 U.S.C. 26(a): credits in this subpart are limited to regular tax
        # liability (26(b)(1): the tax imposed by chapter 1) plus the tax
        # imposed by section 55(a).
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        # 2025 Schedule 8812 instructions, Credit Limit Worksheet A: line 1 is
        # the amount from Form 1040 line 18.
        "https://www.irs.gov/instructions/i1040s8",
    )

    def formula(tax_unit, period, parameters):
        # The tax on taxable income reflects every itemized deduction,
        # including state and local taxes.
        tax_liability_before_credits = tax_unit("income_tax_before_credits", period)
        non_refundable_credits = parameters(period).gov.irs.credits.non_refundable
        non_refundable_credits_ex_ctc = [
            x for x in non_refundable_credits if x != "non_refundable_ctc"
        ]
        total_credits = add(tax_unit, period, non_refundable_credits_ex_ctc)

        return max_(0, tax_liability_before_credits - total_credits)
