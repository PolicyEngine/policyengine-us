from policyengine_us.model_api import *


class az_families_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate"
    unit = USD
    reference = (
        "https://www.azleg.gov/legtext/56leg/1R/laws/0147.pdf#page=6",
        "https://azdor.gov/individuals/arizona-families-tax-rebate",
    )
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # The Arizona Families Tax Rebate is a one-time payment based on
        # 2021 tax returns. Eligibility requires at least $1 of AZ income
        # tax liability and having claimed dependents.
        p = parameters(period).gov.states.az.tax.income.rebate

        # Check tax liability eligibility (at least the statutory minimum).
        # SB 1734 (Laws 2023, ch. 147, sec. 3.N.4) defines tax liability as
        # tax "minus the sum of nonrefundable and refundable income tax
        # credits claimed" under title 43, chapter 10, article 5 - i.e.,
        # after all credits. The statute's definition also ADDS "any amount
        # of recaptured income tax credits" and the taxpayer's Arizona small
        # business (Form 140-SBI) income tax liability. Neither is modeled
        # here: recapture is not modeled at all, and SBI income remains in
        # regular taxable income, which approximates the combined liability.
        # The rebate itself is a session-law payment, not an article 5
        # credit, so it is excluded here. (The statute's 2020/2019 fallback
        # tests are not modelable from a single-year record; like TAXSIM,
        # the 2021 liability proxies all three years.)
        tax_after_non_refundable_credits = tax_unit(
            "az_income_tax_before_refundable_credits", period
        )
        refundable_credits = parameters(
            period
        ).gov.states.az.tax.income.credits.refundable
        other_refundable_credits = add(
            tax_unit,
            period,
            [c for c in refundable_credits if c != "az_families_tax_rebate"],
        )
        tax_liability = tax_after_non_refundable_credits - other_refundable_credits
        has_tax_liability = tax_liability >= p.min_tax_liability

        person = tax_unit.members
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)

        # Get counts by age group for max dependent limit prioritization
        # Young dependents (higher value) are prioritized over older dependents
        age_threshold = p.age_threshold
        young_dependent = dependent & (age < age_threshold)
        older_dependent = dependent & (age >= age_threshold)

        young_count = tax_unit.sum(young_dependent)
        older_count = tax_unit.sum(older_dependent)

        filing_status = tax_unit("filing_status", period)
        max_dependents = p.max_dependents[filing_status]

        # Prioritize young dependents since they have higher value
        young_counted = min_(young_count, max_dependents)
        remaining_slots = max_(max_dependents - young_counted, 0)
        older_counted = min_(older_count, remaining_slots)

        # Get amount per dependent by age using bracket calculation
        # calc(0) returns young dependent amount, calc(17) returns older amount
        young_amount = young_counted * p.amount.calc(0)
        older_amount = older_counted * p.amount.calc(age_threshold)

        rebate_amount = young_amount + older_amount

        return has_tax_liability * rebate_amount
