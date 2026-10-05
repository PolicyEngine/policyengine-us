from policyengine_us.model_api import *


class educator_expense_ald(Variable):
    value_type = float
    entity = TaxUnit
    label = "Educator expense deduction"
    unit = USD
    documentation = (
        "Above-the-line deduction for the head's and spouse's educator "
        "expenses (Schedule 1, line 11). Each eligible educator deducts up to "
        "the cap; on a joint return neither spouse can use the other's unused "
        "amount. A tax unit dependent deducts their own expenses on their own "
        "return."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/62#a_2_D",
        "https://www.law.cornell.edu/uscode/text/26/62#d",
        # Form 1040 instructions (2025), Schedule 1, line 11.
        "https://www.irs.gov/pub/irs-prior/i1040gi--2025.pdf#page=93",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        deduction = person("educator_expense_ald_person", period)
        return tax_unit.sum(head_or_spouse * deduction)
