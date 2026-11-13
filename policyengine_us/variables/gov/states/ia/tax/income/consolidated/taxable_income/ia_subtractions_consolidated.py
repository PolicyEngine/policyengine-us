from policyengine_us.model_api import *


class ia_subtractions_consolidated(Variable):
    value_type = float
    entity = TaxUnit
    label = "Iowa subtractions from taxable income for years on or after 2023"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.legis.iowa.gov/docs/code/422.7.pdf",
        "https://revenue.iowa.gov/taxes/tax-guidance/individual-income-tax/1040-expanded-instructions/ia-1040-schedule-1",
    )
    defined_for = StateCode.IA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ia.tax.income.taxable_income
        # Iowa Code 422.7(20) and (29) subtract military pay "to the extent
        # included" in federal taxable income. Dependents' income is not in
        # it; they report it on their own return, so only the head's and
        # spouse's amounts count.
        total_subtractions = tax_unit_non_dep_add(tax_unit, period, p.subtractions)
        # Prevent negative subtractions from acting as additions
        return max_(0, total_subtractions)
