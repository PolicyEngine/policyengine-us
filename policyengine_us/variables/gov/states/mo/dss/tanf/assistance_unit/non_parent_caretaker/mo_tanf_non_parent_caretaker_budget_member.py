from policyengine_us.model_api import *


class mo_tanf_non_parent_caretaker_budget_member(Variable):
    value_type = bool
    entity = Person
    label = "Member of the Missouri TANF non-parent caretaker neediness budget"
    definition_period = MONTH
    reference = (
        "https://dssmanuals.mo.gov/temporary-assistance-case-management/0210-005-35/",
    )
    defined_for = StateCode.MO

    def formula(person, period, parameters):
        # DSS Manual 0210.005.35: "consider the needs and income of the
        # NPCR, his/her spouse, and any of his/her or their children under
        # age 18 who are household members. Exclude eligible children in
        # the Temporary Assistance assistance group." The model places
        # every dependent child in the caretaker's tax unit in the
        # assistance group, and a caretaker with a child of their own there
        # is a parent, so the budget holds the NPCR and their spouse.
        npcr = person("mo_tanf_non_parent_caretaker", period)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        is_dependent = person("is_tax_unit_dependent", period.this_year)
        spouse = head_or_spouse & ~is_dependent & ~npcr & person.tax_unit.any(npcr)
        return npcr | spouse
