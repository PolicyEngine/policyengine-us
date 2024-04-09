from policyengine_us.model_api import *


class ms_taxable_income_joint_head_or_spouse(Variable):
    value_type = float
    entity = Person
    label = "Mississippi taxable income for head or spouse when married couple file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        agi = person("ms_agi", period)

        deductions_and_exemptions = add(
            person,
            period,
            ["ms_deductions_joint", "ms_total_exemptions_joint"],
        )
        # MS allowes negative taxable income
        return is_head_or_spouse * (agi - deductions_and_exemptions)
