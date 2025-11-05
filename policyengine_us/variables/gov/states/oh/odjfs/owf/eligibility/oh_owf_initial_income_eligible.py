from policyengine_us.model_api import *


class oh_owf_initial_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Ohio OWF initial income eligibility"
    definition_period = MONTH
    defined_for = StateCode.OH
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5107.10",
        "http://codes.ohio.gov/oac/5101:1-23-20",
    )

    def formula(spm_unit, period, parameters):
        person = spm_unit.members

        # Get gross income (before any disregards) using federal TANF variables
        gross_earned = spm_unit.sum(person("tanf_gross_earned_income", period))
        gross_unearned = spm_unit.sum(
            person("tanf_gross_unearned_income", period)
        )
        gross_income = gross_earned + gross_unearned

        # Get initial eligibility income limit (50% of current year FPL)
        fpg = spm_unit("tanf_fpg", period)
        p = parameters(period).gov.states.oh.odjfs.owf.initial_eligibility
        income_limit = fpg * p.income_limit_percent

        # Initial eligibility test: gross income must be below limit
        # Per ORC 5107.10(D)(1) and ODJFS Payment Standards Table
        return gross_income < income_limit
