from policyengine_us.model_api import *


class id_retirement_benefits_deduction_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Idaho retirement benefits deduction"
    documentation = "https://legislature.idaho.gov/statutesrules/idstat/title63/t63ch30/sect63-3022a/"
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
        meets_age_requirement = person("age", period) >= age_threshold

        # age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_or_spouse = head | spouse

        return head_or_spouse * meets_age_requirement
