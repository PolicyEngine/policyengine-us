from policyengine_us.model_api import *


class ms_taxable_income_indiv_head(Variable):
    value_type = float
    entity = Person
    label = "Mississippi taxable income for head when married couple file separately"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        is_head = person("is_tax_unit_head", period)
        agi = person("ms_agi", period)
        deductions_and_exemptions = add(
            person,
            period,
            ["ms_deductions_indiv", "ms_total_exemptions_indiv"],
        )
        # MS allowed negative taxable income
        return is_head * (agi - deductions_and_exemptions)
