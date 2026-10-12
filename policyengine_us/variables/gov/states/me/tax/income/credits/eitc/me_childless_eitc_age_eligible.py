from policyengine_us.model_api import *


class me_childless_eitc_age_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "In the Maine childless EITC age expansion cohort"
    definition_period = YEAR
    reference = "https://legislature.maine.gov/statutes/36/title36sec5219-S.html"
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # 36 M.R.S. Sec. 5219-S(6) extends "eligible individual" to a filer
        # without a qualifying child who is at least 18 and has not attained 25
        # before the close of the tax year. That cohort is exactly the group
        # federal Sec. 32 excludes on the minimum-age floor; childless filers
        # aged 25 to the federal maximum are already federally eligible and do
        # not need this expansion. This variable flags the added 18-24 cohort.
        p = parameters(period).gov.states.me.tax.income.credits.eitc

        person = tax_unit.members
        no_qualifying_children = tax_unit("eitc_child_count", period) == 0

        age = person("age", period)
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        # Maine lowers the age floor to 18; the added cohort ends where federal
        # childless eligibility begins (the federal minimum childless age).
        federal_min_age = parameters(period).gov.irs.credits.eitc.eligibility.age.min
        in_expanded_age_range = (
            (age >= p.eligibility.age.min) & (age < federal_min_age) & is_head_or_spouse
        )

        return no_qualifying_children & tax_unit.any(in_expanded_age_range)
