from policyengine_us.model_api import *


class ms_taxable_income_joint(Variable):
    value_type = float
    entity = Person
    label = "Mississippi taxable income when married couple file jointly"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=13",
        "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80105228.pdf",  # Line 38 - 49,
    )
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        # assign total net_income to tax unit head
        is_head = person("is_tax_unit_head", period)
        agi = person("ms_agi", period)
        head_agi = is_head * person.tax_unit.sum(agi)
        deductions_and_exemptions = add(
            person.tax_unit,
            period,
            ["ms_deductions_joint", "ms_total_exemptions_joint"],
        )
        return max_(head_agi - deductions_and_exemptions, 0)
