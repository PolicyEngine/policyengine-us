from policyengine_us.model_api import *


class niit_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income for the net investment income tax"
    unit = USD
    documentation = (
        "Form 8960 line 13 modified adjusted gross income: adjusted gross "
        "income plus the MAGI change that comes with Schedule K-1 (Form 1041) "
        "box 14 code H amounts. A dependent's amounts stay on the dependent's "
        "own return. The foreign earned income exclusion add-back and the "
        "CFC and PFIC adjustments of Treas. Reg. 1.1411-10(e) are not modeled."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/1411#d",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=11",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=19",
        "https://www.irs.gov/pub/irs-prior/i8960--2024.pdf#page=20",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        estate_magi_adjustment = tax_unit.sum(
            not_dependent * person("estate_income_niit_magi_adjustment", period)
        )
        return tax_unit("adjusted_gross_income", period) + estate_magi_adjustment
