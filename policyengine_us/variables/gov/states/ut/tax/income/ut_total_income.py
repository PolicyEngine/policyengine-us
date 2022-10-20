from policyengine_us.model_api import *


class ut_total_income(Variable):
    """
    Utah total income is line 6 of the 2021 TC-40 Utah individual income tax
    return form. This line is the sum of Federal adjusted gross income (line 4)
    and additions to income from TC-40A Part 1 (line 5).
    """

    value_type = float
    entity = TaxUnit
    label = "UT total income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        federal_agi = tax_unit("adjusted_gross_income", period)
        ut_additions = tax_unit("ut_additions_to_income", period)

        return federal_agi + ut_additions
