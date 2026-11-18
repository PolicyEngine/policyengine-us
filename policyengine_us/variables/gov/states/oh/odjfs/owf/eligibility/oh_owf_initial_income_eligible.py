from policyengine_us.model_api import *


class oh_owf_initial_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio OWF initial income eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10/9-29-2013",
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10/9-29-2017",
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10/9-30-2021",
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
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

        # ORC 5107.10(D)(1)(a)-(b) permits initial gross income at the limit.
        # The separate countable-income/payment-standard test remains strict.
        return gross_income <= income_limit
