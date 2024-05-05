from policyengine_us.model_api import *


class ms_taxable_income_indiv(Variable):
    value_type = float
    entity = Person
    label = "Mississippi taxable income when married couple file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        pre_deductions_agi = person(
            "ms_pre_deductions_taxable_income_indiv", period
        )
        deductions = person("ms_deductions_indiv", period)
        return max_(pre_deductions_agi - deductions, 0)
