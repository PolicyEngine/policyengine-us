from policyengine_us.model_api import *


class md_tanf_gross_earned_income_deduction(Variable):
    value_type = float
    entity = SPMUnit
    label = "Maryland TANF earned income deduction"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.MD
    reference = "https://dhs.maryland.gov/documents/Manuals/Temporary-Cash-Assistance-Manual/0900-Financial-Eligibility/0904%20Deductions%20and%20Expenses%20rev%2011.22.1.doc"

    def formula(spm_unit, period, parameters):
        # Get TANF enrollment status.
        is_tanf_enrolled = spm_unit("is_tanf_enrolled", period)
        # Get earned income for the SPM unit.
        earned_income = add(spm_unit, period, ["employment_income"])
        # Determine if the SPM unit has any self-employment income.
        self_employment_income = add(
            spm_unit, period, ["self_employment_income"]
        )
        has_self_employment_income = self_employment_income > 0
        # Get the policy parameters.
        p = parameters(period).gov.states.md.tanf.income.deductions.earned
        percent = select(
            [~is_tanf_enrolled, has_self_employment_income],
            [p.new, p.self_employed],
            default=p.not_self_employed,
        )
        return earned_income * percent
