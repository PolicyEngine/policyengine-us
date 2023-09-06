from policyengine_us.model_api import *


class de_pension_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware pension exclusion"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=6",
        "https://delcode.delaware.gov/title30/c011/sc02/index.html",
    )
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.de.tax.income.subtractions.exclusions.pension

        person = tax_unit.members

        # determine age eligibility
        age = person("age", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_head", period)

        head_or_spouse = head | spouse
        age_head_or_spouse = age * head_or_spouse
        younger_eligible = age_head_or_spouse < p.min_age
        older_eligible = age_head_or_spouse >= p.min_age

        eligible_pension_income = (
            person("pension_income", period) * head_or_spouse
        )

        capped_eligible_pension_income = min_(
            p.cap.younger, eligible_pension_income
        )

        eligible_retirement_income = (
            person("de_pension_exclusion_income", period) * head_or_spouse
        )

        total_income = eligible_pension_income + eligible_retirement_income

        capped_eligible_retirement_income = min_(p.cap.older, total_income)

        if p.military_retirement_exclusion_available:
            military_retirement_pay = (
                person("military_retirement_pay", period) * head_or_spouse
            )
            capped_military_retirement_pay = min_(
                p.cap.military, military_retirement_pay
            )
            younger_amount = max_(
                capped_military_retirement_pay, capped_eligible_pension_income
            )

            exclusion_amount = select(
                [
                    younger_eligible,
                    older_eligible,
                ],
                [
                    younger_amount,
                    capped_eligible_retirement_income,
                ],
            )
            return tax_unit.sum(exclusion_amount)

        previous_exclusion_amount = select(
            [
                younger_eligible,
                older_eligible,
            ],
            [
                capped_eligible_pension_income,
                capped_eligible_retirement_income,
            ],
        )

        return tax_unit.sum(previous_exclusion_amount)
