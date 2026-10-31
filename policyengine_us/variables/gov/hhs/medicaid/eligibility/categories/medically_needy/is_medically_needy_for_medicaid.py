from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


class is_medically_needy_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Medically needy"
    documentation = (
        "First-pass Medicaid medically needy/spenddown eligibility. This "
        "models aged, blind, and disabled people in states with a medically "
        "needy pathway for their category; applies state income and asset "
        "limits; and subtracts modeled medical expenses from countable income. "
        "It does not model non-ABD medically needy groups, state budget-period "
        "timing, anticipated-expense rules, or state-specific spenddown "
        "administration beyond the annual expense proxy."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/42/part-435/subpart-D",
        "https://www.ecfr.gov/current/title-42/section-435.602#p-435.602(a)(2)(i)",
        "https://www.ecfr.gov/current/title-42/section-435.831#p-435.831(d)",
        "https://www.ecfr.gov/current/title-42/section-435.845#p-435.845(a)",
        "https://www.ecfr.gov/current/title-20/section-416.1202#p-416.1202(b)",
    )

    def formula(person, period, parameters):
        in_category = person("is_in_medicaid_medically_needy_category", period)
        is_aged_blind_or_disabled = person("is_ssi_aged_blind_disabled", period)
        personal_income = person("ssi_countable_income", period)
        medical_expenses = person("medicaid_medically_needy_medical_expenses", period)
        # A child's resources include the excess of ineligible parents'
        # resources (20 CFR 416.1202(b)), as ssi_countable_income already
        # includes their deemed income. SSI's allocation gates apply: a child
        # whose own resources exceed the SSI individual limit, or who fails
        # SSI's immigration test, is deemed nothing.
        personal_assets = person("ssi_countable_resources", period) + person(
            "ssi_resources_deemed_from_ineligible_parent", period.first_month
        )
        # SSI financial responsibility rules (42 CFR 435.602): the unit is
        # the individual or the married couple, plus parents for a child,
        # not the tax filing unit.
        # 42 CFR 435.831(d) deducts expenses of financially responsible
        # relatives. For a child these are the ineligible parents whose
        # income SSI deems (20 CFR 416.1165); split their expenses among the
        # eligible children as the deemed income is split, so that an
        # expense is deducted once.
        tax_unit = person.tax_unit
        eligible_child = is_aged_blind_or_disabled & person("is_child", period)
        parental_expenses = tax_unit.sum(
            medical_expenses * person("is_ssi_ineligible_parent", period)
        )
        eligible_children = tax_unit.sum(eligible_child)
        parental_expense_share = where(
            eligible_child, parental_expenses / max_(eligible_children, 1), 0
        )
        income = _ssi_couple_total(
            person,
            period,
            personal_income - medical_expenses - parental_expense_share,
        )
        assets = _ssi_couple_total(person, period, personal_assets)
        ma = parameters(period).gov.hhs.medicaid
        mn = ma.eligibility.categories.medically_needy
        is_joint = _ssi_spouse_index(person, period) >= 0
        state = person.household("state_code_str", period)
        income_limit = MONTHS_IN_YEAR * where(
            is_joint,
            mn.limit.income.couple[state],
            mn.limit.income.individual[state],
        )
        asset_limit = where(
            is_joint,
            mn.limit.assets.couple[state],
            mn.limit.assets.individual[state],
        )
        under_limits = (income <= income_limit) & (assets <= asset_limit)
        other_categories = [
            category
            for category in ma.eligibility.categories.covered
            if category != "is_medically_needy_for_medicaid"
        ]
        not_in_other_pathway = add(person, period, other_categories) == 0
        return (
            is_aged_blind_or_disabled
            & in_category
            & not_in_other_pathway
            & under_limits
        )
