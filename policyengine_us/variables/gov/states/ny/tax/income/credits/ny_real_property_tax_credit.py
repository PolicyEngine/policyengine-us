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

        # Income measure. Through 2024 the credit is keyed to IT-214 household
        # gross income (line 16) - federal AGI plus nontaxable Social Security
        # and other household income. Part RR of Chapter 59 of the Laws of 2025
        # amended Tax Law 606(e) so that, for tax years beginning on or after
        # 2025-01-01, eligibility (and the credit amount) is based on federal
        # adjusted gross income instead.
        if rptc.uses_household_gross_income:
            income = tax_unit("ny_household_gross_income", period)
        else:
            income = tax_unit("adjusted_gross_income", period)
        # IT-214: "Your federal adjusted gross income cannot be an amount less
        # than zero. If the amount is less than zero, enter 0."
        income = max_(income, 0)
        income_threshold = income * rptc.excess_real_property_tax.calc(income)
        excess_rpt = max_(0, real_estate_tax_or_equiv - income_threshold)

        # Means-tested conditions. The renter cap (IT-214 line 21) applies to
        # the rent itself (average monthly rent $450 or less, i.e. annual rent
        # up to $5,400) — not to 25% of the rent, which is only used to size
        # the credit at line 22. The form applies the cap to adjusted rent (net
        # of heat, gas, electricity, furnishings, and board); PolicyEngine has
        # only gross rent, so the cap is applied to gross rent.
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        meets_value_conditions = (assessed_value <= rptc.max_property_value) & (
            rent <= rptc.max_rent
        )

        # IT-214 income limit ("$18,000 or less").
        meets_income_condition = income <= rptc.max_agi

        eligible = meets_value_conditions & meets_income_condition

        maximum_credit = where(
            meets_age_condition,
            rptc.maximum.elderly.calc(income),
            rptc.maximum.non_elderly.calc(income),
        )

        credit_amount = rptc.rate * excess_rpt

        return min_(eligible * credit_amount, maximum_credit)
