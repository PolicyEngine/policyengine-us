from policyengine_us.model_api import *


class oh_owf_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio OWF income eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5101:1-23-20"
    )

    def formula(spm_unit, period, parameters):
        # Check enrollment status
        enrolled = spm_unit("is_tanf_enrolled", period)

        # Initial eligibility test: gross income < 50% FPL (new applicants)
        initial_eligible = spm_unit("oh_owf_initial_income_eligible", period)

        # Ongoing eligibility test: countable income < payment standard
        countable_income = spm_unit("oh_owf_countable_income", period)
        payment_standard = spm_unit("oh_owf_payment_standard", period)
        ongoing_eligible = countable_income < payment_standard

        # Per ORC 5107.10(D):
        # - New applicants: must pass both initial (50% FPL) and ongoing tests
        # - Enrolled recipients: only need to pass ongoing test
        return where(
            enrolled,
            ongoing_eligible,
            initial_eligible & ongoing_eligible,
        )
