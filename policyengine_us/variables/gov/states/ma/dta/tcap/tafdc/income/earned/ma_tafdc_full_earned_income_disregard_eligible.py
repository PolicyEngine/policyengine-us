from policyengine_us.model_api import *


class ma_tafdc_full_earned_income_disregard_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Is eligible for the full earned income disregard under the Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC)"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/regulations/massachusetts/106-CMR-704-281"  # (A)
    defined_for = StateCode.MA

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.ma.dta.tcap.tafdc.earned_income_disregard.full_disregard
        gross_income = person.spm_unit(
            "ma_tafdc_applicable_income_for_financial_eligibility", period
        )

        fpg = person.spm_unit("spm_unit_fpg", period)
        income_limit = fpg * p.fpg_limit
        return gross_income < income_limit
