from policyengine_us.model_api import *


class refundable_ctc_barred_by_section_911_exclusion(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Refundable CTC barred by a section 911 exclusion"
    documentation = (
        "Whether section 24(d)(3) denies the refundable Child Tax Credit "
        "because the filer elects to exclude foreign earned income or housing "
        "amounts from gross income under section 911 (Form 2555). These "
        "filers also skip Schedule 8812 Credit Limit Worksheet B."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/24#d_3",
        # 2025 Instructions for Schedule 8812, Part II-A.
        "https://www.irs.gov/pub/irs-prior/i1040s8--2025.pdf#page=3",
        # 2021 Schedule 8812: Part I-B has no Form 2555 condition.
        "https://www.irs.gov/pub/irs-prior/f1040s8--2021.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.irs.credits.ctc.refundable
        elects_section_911_exclusion = (
            tax_unit("foreign_earned_income_exclusion", period) > 0
        )
        # Section 24(i)(1)(A) (2021) switched off all of subsection (d),
        # including this bar, for filers whose principal place of abode was in
        # the United States for more than half the year and for bona fide
        # residents of Puerto Rico. The model assumes every filer meets that
        # test in a fully refundable year.
        bar_in_force = (
            p.foreign_earned_income_exclusion_bar_applies and not p.fully_refundable
        )
        return elects_section_911_exclusion & bar_in_force
