from policyengine_us.model_api import *


class id_household_and_dependent_care_expense_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho household and dependent care expense deduction"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(tax_unit, period, parameters):
        relevant_expenses = tax_unit("cdcc_relevant_expenses", period)
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.dependent_care_expenses
        return min_(relevant_expenses, p.cap)
