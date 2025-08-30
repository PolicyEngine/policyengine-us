from policyengine_us.model_api import *


class il_liheap_base_payment(Variable):
    value_type = float
    entity = SPMUnit
    label = "Illinois LIHEAP base payment"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.IL
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.liheap.payment.base_amount

        # Check if heat is included in rent
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        heating_expenses = add(spm_unit, period, ["heating_expense_person"])

        # For renters with heat included in rent, provide minimum cash benefit
        # For others, benefit based on actual heating expenses up to maximum
        capped_heating_expenses = min_(heating_expenses, p.max)

        return where(
            heat_in_rent,
            p.min,  # Fixed minimum for heat included in rent
            capped_heating_expenses,  # Based on actual expenses, up to maximum
        )
