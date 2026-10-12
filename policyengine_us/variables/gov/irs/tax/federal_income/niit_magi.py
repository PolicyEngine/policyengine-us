from policyengine_us.model_api import *


class niit_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income for the net investment income tax"
    unit = USD
    documentation = (
        "Form 8960 line 13 modified adjusted gross income: adjusted gross "
        "income plus the MAGI change that comes with Schedule K-1 (Form 1041) "
        "box 14 code H amounts, plus the foreign earned income excluded under "
        "26 U.S.C. 911(a)(1) net of the deductions disallowed for it (26 U.S.C. "
        "1411(d); see niit_magi_section_911_addition). A dependent's amounts "
        "stay on the dependent's own return. The CFC and PFIC adjustments of "
        "Treas. Reg. 1.1411-10(e) are not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#d",
        "https://www.law.cornell.edu/cfr/text/26/1.1411-2",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=11",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=19",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=20",
        "https://www.irs.gov/pub/irs-prior/i8960--2025.pdf#page=23",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        estate_magi_adjustment = tax_unit.sum(
            not_dependent * person("estate_income_niit_magi_adjustment", period)
        )
        # Section 1411(d) adds "the excess (if any)" of the section
        # 911(a)(1) exclusion over the amounts section 911(d)(6) disallows
        # for it, so the addition is never negative.
        section_911_addition = max_(
            0, tax_unit("niit_magi_section_911_addition", period)
        )
        return (
            tax_unit("adjusted_gross_income", period)
            + estate_magi_adjustment
            + section_911_addition
        )
