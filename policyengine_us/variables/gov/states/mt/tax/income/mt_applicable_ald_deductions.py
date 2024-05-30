from policyengine_us.model_api import *


class mt_applicable_ald_deductions(Variable):
    value_type = float
    entity = Person
    label = "Montana applicable above-the-line deductions "
    unit = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        ald_deductions = person.tax_unit("above_the_line_deductions", period)
        return ald_deductions / person.tax_unit("head_spouse_count", period)
