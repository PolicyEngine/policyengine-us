from policyengine_us.model_api import *


class net_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico net income"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.PR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-a/30105/"

    def formula(tax_unit, period, parameters):
        gross_income = add(
            tax_unit,
            period,
            [
                "pr_gross_income",
            ],
        )
        exemptions = tax_unit("exemptions", period)
        deductions = tax_unit("taxable_income_deductions", period)
        income_pref_rate = tax_unit(
            "income_subject_to_preferred_rates", period
        )
        return max_(
            0, gross_income - exemptions - deductions - income_pref_rate
        )
