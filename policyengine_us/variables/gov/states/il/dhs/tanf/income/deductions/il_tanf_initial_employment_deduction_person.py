from policyengine_us.model_api import *


class il_tanf_initial_employment_deduction_person(Variable):
    value_type = float
    entity = Person
    label = "Illinois Temporary Assistance for Needy Families (TANF) initial employment deduction per person"
    unit = USD
    definition_period = MONTH
    reference = "https://www.law.cornell.edu/regulations/illinois/Ill-Admin-Code-tit-89-SS-112.141"
    defined_for = StateCode.IL

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.il.dhs.tanf.income.initial_employment_deduction

        gross_earned_income = person("il_tanf_gross_earned_income", period)
        fpg = person.spm_unit("spm_unit_fpg", period)
        payment_level = person.spm_unit(
            "il_tanf_payment_level_for_initial_eligibility", period
        )

        initial_employment_deduction = p.rate * fpg - payment_level
        is_employed = gross_earned_income > 0
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        ied_eligible_person = is_employed & is_head_or_spouse
        uncapped_ied = ied_eligible_person * initial_employment_deduction
        return min_(gross_earned_income, uncapped_ied)
