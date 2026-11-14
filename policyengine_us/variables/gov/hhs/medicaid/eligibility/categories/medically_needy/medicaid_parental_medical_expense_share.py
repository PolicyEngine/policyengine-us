from policyengine_us.model_api import *
from policyengine_us.variables.household.demographic.person._parent_links import (
    is_parent_of_any,
)


class medicaid_parental_medical_expense_share(Variable):
    value_type = float
    entity = Person
    label = "Medicaid child's share of parents' medical expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-435.121#p-435.121(f)(1)(iii)",
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(d)",
        "https://www.ecfr.gov/current/title-20/section-416.1165",
        "https://dssmanuals.mo.gov/mo-healthnet-for-the-aged-blind-and-disabled/0805-000-00/0805-020-00/0805-020-15/",
    )

    def formula(person, period, parameters):
        # 42 CFR 435.121(f)(1)(iii) and 435.831(d) deduct expenses of
        # financially responsible relatives. For a child these are the
        # ineligible parents whose income SSI deems (20 CFR 416.1165), and
        # MHABD 0805.020.15 names the same parents in Missouri. Split their
        # expenses among the eligible children as the deemed income is split,
        # so that an expense is deducted once.
        tax_unit = person.tax_unit
        eligible_child = person("is_ssi_aged_blind_disabled", period) & person(
            "is_child", period
        )
        # Missouri counts the expenses of "the disabled child's natural or
        # adoptive parent/s whose income is used in determining eligibility", and
        # "This does not include a stepparent" (MHABD 0805.020.15). SSI's
        # ineligible parents include a parent's spouse (20 CFR 416.1160(d)), so
        # Missouri keeps only the child's own parents, as its parental deeming
        # does.
        missouri = person.household("state_code_str", period) == "MO"
        responsible_parent = person("is_ssi_ineligible_parent", period) & (
            ~missouri | is_parent_of_any(person, period, eligible_child)
        )
        parental_expenses = tax_unit.sum(
            person("medicaid_medically_needy_medical_expenses", period)
            * responsible_parent
        )
        eligible_children = tax_unit.sum(eligible_child)
        return where(eligible_child, parental_expenses / max_(eligible_children, 1), 0)
