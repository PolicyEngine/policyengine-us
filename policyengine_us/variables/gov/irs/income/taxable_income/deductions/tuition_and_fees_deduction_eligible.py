from policyengine_us.model_api import *


class tuition_and_fees_deduction_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Tuition and fees deduction eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.irs.gov/pub/irs-pdf/f8917.pdf#page=2",
        # Law was repealed in 2021
        "https://irc.bloombergtax.com/public/uscode/doc/irc/section_222",
    )

    def formula(tax_unit, period, parameters):
        # Married filing separately are not eligible for this deduction.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Can't claim this deduction if the household has taken the
        # American Oppportunity or Lifetime Learning Credit.
        aoc_llc = add(
            tax_unit,
            period,
            [
                "american_opportunity_credit",
                "lifetime_learning_credit_potential",
            ],
        )
        # IRC 222(c)(3): no deduction to an individual for whom a section 151
        # deduction "may be allowed to another taxpayer". Without this, a
        # filer barred from the education credits for that reason would
        # become eligible here.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return ~separate & (aoc_llc == 0) & ~dependent_filer
