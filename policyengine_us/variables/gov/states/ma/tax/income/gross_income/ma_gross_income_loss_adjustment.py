from policyengine_us.model_api import *


class ma_gross_income_loss_adjustment(Variable):
    value_type = float
    entity = TaxUnit
    label = "MA gross income loss adjustment for Form 1 lines 6 and 7"
    unit = USD
    definition_period = YEAR
    reference = ("https://www.mass.gov/doc/2024-form-1-instructions/download",)
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        # MA Form 1 allows losses on lines 6a, 6b, and 7 to offset
        # other 5.0% income. irs_gross_income floors each source at
        # zero, so this variable captures the losses that were dropped.
        # Line 10 instruction: "Be sure to subtract any losses
        # in lines 6 or 7."
        # Line 6a: Business/profession loss (Schedule C)
        se_income = add(tax_unit, period, ["total_self_employment_income"])
        # Line 6b: Farm loss (Schedule F)
        farm = add(tax_unit, period, ["farm_income"])
        # Line 7: Rental, partnership, S-corp, farm rent losses
        rental = add(tax_unit, period, ["rental_income"])
        partnership = add(tax_unit, period, ["partnership_s_corp_income"])
        farm_rent = add(tax_unit, period, ["farm_rent_income"])
        return (
            min_(se_income, 0)
            + min_(farm, 0)
            + min_(rental, 0)
            + min_(partnership, 0)
            + min_(farm_rent, 0)
        )
