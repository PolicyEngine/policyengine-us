from policyengine_us.model_api import *


class az_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Property Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = [
        "https://www.azleg.gov/ars/43/01072.htm",  # ARS 43-1072(B)
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=5",
    ]
    defined_for = "az_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.property_tax
        income = tax_unit("az_property_tax_credit_income", period)

        # ARS 43-1072(A)(3): a claimant who "lived with a spouse or one or
        # more persons" uses the Table 2 (B)(2) schedule, while a claimant who
        # "did not live with a spouse or any other persons" uses the Table 1
        # (B)(1) schedule. Any co-resident (spouse, adult child, sibling,
        # roommate) triggers Table 2. Use the broadest available signal:
        # explicit cohabitating-spouses input, a married couple filing jointly,
        # or a household with more than one person.
        household_size = tax_unit.household("household_size", period)
        lives_with_others = (
            tax_unit("cohabitating_spouses", period)
            | tax_unit("tax_unit_married", period)
            | (household_size > 1)
        )

        # Household income (Form 140PTC line J) can be negative, for example
        # after a line D capital loss. The 2023-2025 instructions (page 5, line
        # J note) then consider household income to be zero for the Schedule 1
        # and 2 lookup. The 2021 and 2022 instructions have no such note; the
        # schedules start at 0, so the same floor is applied in every year. A
        # single-amount scale returns 0 below its first threshold, so a
        # negative income must be floored here rather than passed to calc.
        schedule_income = max_(income, 0)
        cap = where(
            lives_with_others,
            p.amount.cohabitating.calc(schedule_income),
            p.amount.living_alone.calc(schedule_income),
        )

        # ARS 43-1072(B): the credit is the lesser of the table amount and
        # property taxes paid. For renters, taxes paid is rent multiplied by
        # the landlord's property tax factor from Form 201 (Form 140PTC line
        # 13); the rent_property_tax_rate parameter approximates this
        # landlord-specific factor.
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        rent = add(tax_unit, period, ["rent"])
        property_taxes_paid = real_estate_taxes + p.rent_property_tax_rate * rent

        return min_(cap, property_taxes_paid)
