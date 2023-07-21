from policyengine_us.model_api import *


class de_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6"
        "https://delcode.delaware.gov/title30/c011/sc02/index.html"
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.pension_exclusion
        person = tax_unit.members
        # determine age eligibility
        age_head = tax_unit("age_head", period)
        under_60_head_eligible = (age_head < p.min_age).astype(int)
        above_60_head_eligible = (age_head >= p.min_age).astype(int)

        # determine military eligiblity
        military_disabled_head = tax_unit("military_disabled_head", period)
        military_eligible = (
            military_disabled_head & under_60_head_eligible
        ).astype(int)

        # determine pension exclusion value based on military status
        exclusion_value = where(
            military_eligible,
            p.max_pension_amount_cap,
            p.min_pension_amount_cap,
        )

        # determine pension exclusion amount
        pension_income = person("market_income", period)

        # determine eligible retirement income for head above 60
        elig_retirement_income = person(
            "eligible_retirement_income_for_elderly", period
        )
        total_income_above_60 = pension_income + elig_retirement_income

        # determine exclusion eligibility
        is_eligible_for_under_60_military = (
            under_60_head_eligible & military_disabled_head
        ).astype(int)
        is_eligible_for_under_60_non_military = (
            under_60_head_eligible & ~military_disabled_head
        ).astype(int)

        # apply the exclusion value or the pension income, whichever is lower, for eligible individuals
        pension_exclusion_under_60_military = where(
            is_eligible_for_under_60_military,
            min_(exclusion_value, pension_income),
            0,
        )
        pension_exclusion_under_60_non_military = where(
            is_eligible_for_under_60_non_military,
            min_(exclusion_value, pension_income),
            0,
        )
        pension_exclusion_above_60 = where(
            above_60_head_eligible,
            min_(p.max_pension_amount_cap, total_income_above_60),
            0,
        )

        return (
            pension_exclusion_under_60_military
            + pension_exclusion_under_60_non_military
            + pension_exclusion_above_60
        )
