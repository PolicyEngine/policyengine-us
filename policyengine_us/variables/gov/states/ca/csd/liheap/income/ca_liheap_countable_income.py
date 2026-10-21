from policyengine_us.model_api import *


class ca_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "California LIHEAP annualized countable income"
    defined_for = StateCode.CA
    # PDF pages 7,229-240,243-247
    reference = "https://www.csd.ca.gov/Shared%20Documents/2026-Final-LIHEAP-State-Plan.pdf#page=7"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ca.csd.liheap.income
        gross = add(
            spm_unit,
            period,
            ["ca_liheap_countable_earned_income"] + p.unearned_sources,
        )
        support_paid = add(spm_unit, period, p.support_deductions)
        # The shared non-payroll aggregate includes Part B once. Payroll
        # premiums are disjoint; supplied totals must exclude vision,
        # dental, long-term care and other nonmedical charges.
        medical_premiums = add(
            spm_unit,
            period,
            [
                "medical_expense_health_insurance_premiums",
                "pre_tax_health_insurance_premiums",
            ],
        )
        return max_(gross - support_paid - medical_premiums, 0)
