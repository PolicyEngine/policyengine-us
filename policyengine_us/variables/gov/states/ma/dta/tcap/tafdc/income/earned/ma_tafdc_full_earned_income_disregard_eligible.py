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
        gross_income = person.spm_unit.sum(
            person("ma_tcap_gross_earned_income", period) # <-- maybe change this variable
        ) 
        fpg = person.spm_unit("spm_unit_fpg", period)
        return gross_income < fpg * p.fpg_limit
