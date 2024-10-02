from policyengine_us.model_api import *


class id_retirement_benefits_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Idaho retirement benefits deduction"
    reference = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/"
    definition_period = YEAR
    defined_for = StateCode.ID

    def formula(person, period, parameters):
        p = parameters(
            period
        ).gov.states.id.tax.income.deductions.retirement_benefits

        age_threshold = where(
            person("is_disabled", period),
            p.age_eligibility.disabled,
            p.age_eligibility.main,
        )
        age_eligible = person("age", period) >= age_threshold

        head_or_spouse = person("is_tax_unit_head_or_spouse", period)

        return head_or_spouse & age_eligible
