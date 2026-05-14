from policyengine_us.model_api import *


class additional_senior_deduction_magi(Variable):
    value_type = float
    entity = TaxUnit
    label = "Modified adjusted gross income for the senior deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.congress.gov/119/bills/hr1/BILLS-119hr1enr.pdf#page=88",
        "https://www.irs.gov/pub/irs-pdf/f1040s1a.pdf#page=1",
    )

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        excluded_income = add(
            tax_unit,
            period,
            [
                "foreign_earned_income_exclusion",
                "specified_possession_income",
                "puerto_rico_income",
            ],
        )
        return agi + excluded_income
