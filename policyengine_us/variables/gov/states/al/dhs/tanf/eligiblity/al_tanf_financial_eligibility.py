from policyengine_us.model_api import *


class al_tanf_financial_eligibility(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Alabama family assistance (TANF) based on financial requirements"
    defined_for = StateCode.AL
    definition_period = YEAR
    reference = "https://dhr.alabama.gov/wp-content/uploads/2023/10/DHR-FAD-595-Oct.23.pdf"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.al.dhs.tanf
        income = add(spm_unit, period, ["al_tanf_applicable_income"])
        # A certain percentage of incocome is disregarded based on the care
        # and childcare expenses
        care_and_child_care_expenses = add(
            spm_unit, period, ["childcare_expenses", "care_expenses"]
        )
        total_disregard = (
            care_and_child_care_expenses * p.expense_disregard_rate
        )
        reduced_income = max_(income - total_disregard, 0)
        # The payment standard is dependent on the number of people in the household
        unit_size = spm_unit("spm_unit_size", period)
        capped_unit_size = min_(unit_size, p.max_unit_size)
        payment_standard = (
            p.payment_standard[capped_unit_size] * MONTHS_IN_YEAR
        )
        return reduced_income < payment_standard
