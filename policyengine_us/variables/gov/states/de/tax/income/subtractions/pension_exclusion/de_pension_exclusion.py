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
        age = person("age", period)
        under_60_head_eligible = age < p.min_age
        above_60_head_eligible = age >= p.min_age

        # determine military eligiblity
        military_retirement_pay = person(
            "military_retirement_pay", period
        ).astype(bool)

        military_eligible = where(
            p.military_retirement_exclusion_available,
            military_retirement_pay > 0,
            military_retirement_pay < 0,
        )

        # determine pension exclusion value based on military status
        exclusion_value = where(
            military_eligible,
            p.cap.military,
            p.cap.younger,
        )

        # determine pension exclusion amount
        pension_income = person("pension_income", period)

        # determine eligible retirement income for head above 60
        elig_retirement_income = person(
            "de_eligible_retirement_income_for_elderly", period
        )
        total_income_above_60 = pension_income + elig_retirement_income

        # determine exclusion eligibility
        is_eligible_for_under_60_military = (
            under_60_head_eligible & military_eligible
        ).astype(int)
        is_eligible_for_under_60_non_military = (
            under_60_head_eligible & ~military_eligible
        ).astype(int)

        # apply the exclusion value or the pension income, whichever is lower, for eligible individuals
        min_amount_under_60_military = min_(exclusion_value, pension_income)
        pension_exclusion_under_60_military = where(
            is_eligible_for_under_60_military,
            min_amount_under_60_military,
            0,
        )

        min_amount_under_60_non_military = min_(
            exclusion_value, pension_income
        )
        pension_exclusion_under_60_non_military = where(
            is_eligible_for_under_60_non_military,
            min_amount_under_60_non_military,
            0,
        )

        min_amount_above_60 = min_(p.cap.older, total_income_above_60)
        pension_exclusion_above_60 = where(
            above_60_head_eligible,
            min_amount_above_60,
            0,
        )

        # Summing the individual exclusions for each case
        total_exclusion_under_60_military = tax_unit.sum(
            pension_exclusion_under_60_military
        )
        total_exclusion_under_60_non_military = tax_unit.sum(
            pension_exclusion_under_60_non_military
        )
        total_exclusion_above_60 = tax_unit.sum(pension_exclusion_above_60)

        return (
            total_exclusion_under_60_military
            + total_exclusion_under_60_non_military
            + total_exclusion_above_60
        )
