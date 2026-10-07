from policyengine_us.model_api import *


class ctc_tax_liability_after_preceding_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Tax liability after credits preceding the CTC"
    unit = USD
    documentation = (
        "Income tax before credits less the non-refundable credits that "
        "precede the Child Tax Credit (Schedule 8812 Credit Limit Worksheet "
        "A, line 3). Income tax before credits is the actual liability, on "
        "taxable income after every itemized deduction, state and local taxes "
        "included."
    )
    definition_period = YEAR
    reference = (
        # 26 U.S.C. 26(a): credits in this subpart are limited to regular tax
        # liability (26(b)(1): the tax imposed by chapter 1) plus the tax
        # imposed by section 55(a).
        "https://www.law.cornell.edu/uscode/text/26/26#a",
        # 2025 Instructions for Schedule 8812, Credit Limit Worksheet A: line 1
        # is the amount from Form 1040 line 18.
        "https://www.irs.gov/pub/irs-pdf/i1040s8.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        # Line 1: the tax on taxable income reflects every itemized deduction,
        # including state and local taxes. Reading it here forms no cycle:
        # the SALT deduction counts state income tax through
        # state_withheld_income_tax, withholding estimated from income, which
        # reads neither federal tax nor credits.
        tax_liability_before_credits = tax_unit("income_tax_before_credits", period)
        p = parameters(period).gov.irs.credits.ctc_tax_liability_limit
        # add() returns None for an empty list, which a reform may set.
        preceding_credits = (
            add(tax_unit, period, p.preceding_credits) if p.preceding_credits else 0
        )
        return max_(0, tax_liability_before_credits - preceding_credits)
