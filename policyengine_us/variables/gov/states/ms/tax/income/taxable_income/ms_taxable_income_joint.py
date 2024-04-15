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
        # MS allowes negative taxable income when married couple file jointly
        ms_unadjusted_taxable_income_joint = person(
            "ms_unadjusted_taxable_income_joint", period
        )
        any_spouse_negative_income = person.tax_unit.any(
            ms_unadjusted_taxable_income_joint < 0
        )

        # 1. both head and spouse have positive taxable income (includes 0)

        # 2. at least one head or spouse has negative taxable income
        # assign total net_income to tax unit head
        is_head = person("is_tax_unit_head", period)
        total_taxable_income_attributed_to_head = sum(
            ms_unadjusted_taxable_income_joint
        )

        income_combined = [
            is_head[i] * total_taxable_income_attributed_to_head
            for i in range(len(is_head))
        ]

        return where(
            any_spouse_negative_income,
            income_combined,
            ms_unadjusted_taxable_income_joint,
        )
