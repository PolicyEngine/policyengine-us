from policyengine_us.model_api import *


class ny_real_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "NY real property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.nysenate.gov/legislation/laws/TAX/606"  # (e)
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        rptc = parameters(period).gov.states.ny.tax.income.credits.real_property_tax

        # Age-based eligibility.
        person = tax_unit.members
        age = person("age", period)
        is_dependent = person("is_tax_unit_dependent", period)
        aged = age >= rptc.elderly_age
        meets_age_condition = tax_unit.any(~is_dependent & aged)

        # Real-estate-based phase-in.
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        equivalent_rent = rent * rptc.rent_tax_equivalent
        real_estate_tax_or_equiv = real_estate_tax + equivalent_rent

        # The credit is keyed to IT-214 household gross income (line 16),
        # not federal AGI: it adds back nontaxable Social Security and other
        # income the household received.
        household_gross_income = tax_unit("ny_household_gross_income", period)
        income_threshold = household_gross_income * rptc.excess_real_property_tax.calc(
            household_gross_income
        )
        excess_rpt = max_(0, real_estate_tax_or_equiv - income_threshold)

        # Means-tested conditions. The renter cap (IT-214 line 21) applies to
        # the rent itself (average monthly rent $450 or less, i.e. annual rent
        # up to $5,400) — not to 25% of the rent, which is only used to size
        # the credit at line 22.
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        meets_value_conditions = (assessed_value <= rptc.max_property_value) & (
            rent <= rptc.max_rent
        )

        meets_income_condition = household_gross_income < rptc.max_agi

        eligible = meets_value_conditions & meets_income_condition

        maximum_credit = where(
            meets_age_condition,
            rptc.maximum.elderly.calc(household_gross_income),
            rptc.maximum.non_elderly.calc(household_gross_income),
        )

        credit_amount = rptc.rate * excess_rpt

        return min_(eligible * credit_amount, maximum_credit)
