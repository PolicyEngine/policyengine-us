from policyengine_us.model_api import *


class ms_self_employed_health_insurance_adjustment(Variable):
    value_type = float
    entity = Person
    label = "Mississippi self-employed health insurance adjustment"
    unit = USD
    documentation = (
        "Each person's own self-employed health insurance deduction (Form "
        "80-105 line 56). Mississippi reports each spouse's income and "
        "adjustments separately, so the tax unit's deduction is not repeated "
        "for every member. A tax-unit deduction that differs from the head's "
        "and spouse's own amounts is shared in proportion to them; without own amounts the head and "
        "spouse each take half."
    )
    definition_period = YEAR
    reference = "https://www.dor.ms.gov/sites/default/files/tax-forms/individual/80100251%202.pdf#page=12"
    defined_for = StateCode.MS

    def formula(person, period, parameters):
        return person_share_of_tax_unit_amount(
            person,
            period,
            "self_employed_health_insurance_ald",
            "self_employed_health_insurance_ald_person",
            split_between_spouses=True,
        )
