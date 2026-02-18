from policyengine_us.model_api import *


class az_families_tax_rebate_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Families Tax Rebate subtraction"
    unit = USD
    documentation = "https://azdor.gov/individuals/arizona-families-tax-rebate"
    reference = "A.R.S. 43-1022 - Subtractions from Arizona Gross Income"
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        # The Arizona Families Tax Rebate is subtracted from Arizona gross
        # income because while it is taxable federally, Arizona does not
        # tax it at the state level
        p = parameters(period).gov.states.az.tax.income.rebate

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

        return young_amount + older_amount
