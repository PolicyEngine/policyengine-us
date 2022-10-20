from policyengine_us.model_api import *


class ut_taxable_income(Variable):
    """
    This variable computes Utah taxable income (line 9 of the Utah 2021 TC-40
    form) as Total income (line 6) minus Salt Refund (line 7) minus
    subtractions from income (line 8).
    """

    value_type = float
    entity = TaxUnit
    label = "UT taxable income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.UT

    def formula(tax_unit, period, parameters):
        salt_refund = tax_unit("salt_refund_last_year", period)
        ut_subtractions = tax_unit("ut_subtractions_from_income", period)
        ut_total_income = tax_unit("ut_total_income", period)

        return ut_total_income - salt_refund - ut_subtractions
