from policyengine_us.model_api import *


class oh_owf_initial_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio OWF initial income eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-administrative-code/rule-5101:1-23-20",
        "https://dam.assets.ohio.gov/image/upload/jfs.ohio.gov/OWF/tanf/2024%20TANF%20State%20Plan%20Combined.pdf#page=4",
    )

    def formula(spm_unit, period, parameters):
        # Get gross income (before any disregards) using federal TANF variables
        gross_income = add(
            spm_unit,
            period,
            ["tanf_gross_earned_income", "tanf_gross_unearned_income"],
        )

        # Get initial eligibility income limit (50% of FPL effective July 1)
        fpg = spm_unit("oh_owf_fpg", period)
        p = parameters(period).gov.states.oh.odjfs.owf.initial_eligibility
        income_limit = fpg * p.income_limit_rate

        # Initial eligibility test: gross income must be below limit
        # Per ORC 5107.10(D)(1) and ODJFS Payment Standards Table
        return gross_income < income_limit
