from policyengine_us.model_api import *


class mt_applicable_ald_deductions(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable above-the-line deductions "
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        ald_deductions = person.tax_unit("above_the_line_deductions", period)
        spouse = person("is_tax_unit_spouse", period)
        spouse_present = person.tax_unit.any(spouse)
        total_deduction = where(
            spouse_present, ald_deductions / 2, ald_deductions
        )
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return head_or_spouse * total_deduction
