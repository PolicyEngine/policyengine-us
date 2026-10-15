from policyengine_us.model_api import *


class va_low_income_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Virginia Low Income Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.VA
    reference = (
        "https://law.lis.virginia.gov/vacode/title58.1/chapter3/section58.1-339.8/",
        "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2025-760-instructions.pdf#page=30",
    )

    def formula(tax_unit, period, parameters):
        # Criteria 1: Not qualified to claim EITC if anyone in the tax unit claimed any of the following:
        p = parameters(period).gov.states.va.tax.income.credits.eitc.low_income_tax
        program_eligible = add(tax_unit, period, p.ineligible_programs) == 0

        # Criteria 2: Not qualified if a filer is claimed as a dependent on
        # another taxpayer's return. Neither Va. Code 58.1-339.8 nor the
        # instructions settle a joint return where only one spouse is
        # claimed. We read the statute's bar on the credit "against such tax
        # of a dependent" as reaching a joint return, which carries both
        # spouses' tax, so either spouse being claimed bars it.
        filer_is_dependent_elsewhere = tax_unit(
            "head_or_spouse_is_dependent_elsewhere", period
        )

        return program_eligible & ~filer_is_dependent_elsewhere
