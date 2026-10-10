from policyengine_us.model_api import *


class va_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia EITC or low-income credit"
    documentation = "Whether the return can claim any Virginia credit for low-income taxpayers: the low-income credit or either Virginia earned income tax credit. Their own amount tests apply separately."
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=30",
    )

    def formula(tax_unit, period, parameters):
        # Va. Code 58.1-339.8(D): "no credit shall be allowed pursuant to
        # subsection B" (the low-income credit and both EITC alternatives) in
        # a year in which the filers, or a dependent on their return, claim a
        # listed subtraction, deduction or exemption.
        p = parameters(period).gov.states.va.tax.income.credits.eitc.low_income_tax
        claims_no_disqualifying_benefit = (
            add(tax_unit, period, p.ineligible_programs) == 0
        )
        # 58.1-339.8(B)(1): "the credit provided under this section shall not
        # be allowed against such tax of a dependent". Neither the Code nor the
        # instructions settle a joint return where only one spouse is claimed.
        # We read the bar as reaching a joint return, which carries both
        # spouses' tax, so either spouse being claimed bars it.
        filer_is_dependent_elsewhere = tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )
        return claims_no_disqualifying_benefit & ~filer_is_dependent_elsewhere
