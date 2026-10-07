from policyengine_us.model_api import *


class ms_self_employed_retirement_adjustment(Variable):
    value_type = float
    entity = Person
    label = "Mississippi self-employed retirement plan adjustment"
    unit = USD
    documentation = (
        "Each person's own self-employed SEP, SIMPLE and qualified plan "
        "deduction (Form 80-105 line 51). Mississippi reports each spouse's "
        "income and adjustments separately, so the tax unit's deduction is not "
        "repeated for every member. A tax-unit deduction that differs from the "
        "head's and spouse's own amounts is shared in proportion to them."
    )
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12"
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        return person_share_of_tax_unit_amount(
            person,
            period,
            "self_employed_pension_contribution_ald",
            "self_employed_pension_contribution_ald_person",
        )
