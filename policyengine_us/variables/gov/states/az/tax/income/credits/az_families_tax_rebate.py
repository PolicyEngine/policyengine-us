from policyengine_us.model_api import *


class az_families_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate"
    unit = USD
    documentation = "https://azdor.gov/individuals/arizona-families-tax-rebate"
    reference = "https://www.azleg.gov/legtext/56leg/1r/laws/0147.htm"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # The Arizona Families Tax Rebate is a one-time payment based on
        # 2021 tax returns. Eligibility requires at least $1 of AZ income
        # tax liability and having claimed dependents.
        p = parameters(period).gov.states.az.tax.income.rebate

        # Check tax liability eligibility (at least $1)
        tax_before_credits = tax_unit(
            "az_income_tax_before_non_refundable_credits", period
        )
        has_tax_liability = tax_before_credits >= 1

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
