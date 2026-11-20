from policyengine_us.model_api import *


class ny_real_property_tax_credit_potential(Variable):
    value_type = float
    entity = TaxUnit
    label = "New York real property tax credit if the tax unit were the household's claimant"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (e)
        # 2024 IT-214-I: "If at least one member of your household is age 65
        # or older, the credit can be as much as $375."
        "https://www.tax.ny.gov/pdf/2024/inc/it214i_2024.pdf#page=1",
        # 2024 IT-214-I line 19: "the total rent that you and all members of
        # your household paid".
        "https://www.tax.ny.gov/pdf/2024/inc/it214i_2024.pdf#page=2",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        rptc = parameters(period).gov.states.ny.tax.income.credits.real_property_tax
        person = tax_unit.members
        aged = person("age", period) >= rptc.elderly_age
        rent = person("rent", period)

        # NOTE: Part RR of Chapter 59 of the Laws of 2025 moved the credit from
        # the household to the qualified taxpayer for tax years from 2025, all
        # on the same date: the income measure (606(e)(1)(C), (7)(A)), the
        # rent (606(e)(1)(F)), the age test (606(e)(3), (6)) and the number of
        # credits (606(e)(6)). The household gross income switch therefore
        # marks the household rules for all four.
        if rptc.uses_household_gross_income:
            # Through 2024 the income measure is IT-214 household gross income
            # (line 16), already the total for everyone in the household.
            income = tax_unit("ny_household_gross_income", period)
            # 606(e)(1)(F)(i): the real property tax equivalent is 25% of
            # the adjusted rent "actually paid ... by a household"; IT-214
            # line 19 counts the rent "you and all members of your household
            # paid".
            rent_paid = tax_unit.max(person.household.sum(rent))
            # 606(e)(6)(A): where two or more members of a household can
            # qualify "and one of them is sixty-five years of age or more",
            # the credit is the one for those aged 65 or older. 606(e)(1)(A)(i)
            # defines a qualified taxpayer by residence, occupancy and filing
            # a return, which the model does not track, and the 2024 IT-214-I
            # gives the elderly limit when "at least one member of your
            # household is age 65 or older". So any household member's age
            # counts, including a tax unit dependent's.
            meets_age_condition = tax_unit.any(person.household.any(aged))
        else:
            # From 2025 (Part RR of Chapter 59 of the Laws of 2025) the
            # credit is keyed to federal AGI, and eligibility and the amount
            # turn on the taxpayer's own return.
            income = tax_unit("ny_recomputed_federal_agi", period)
            # 606(e)(1)(F)(ii): rent "actually paid ... by a qualified
            # taxpayer".
            rent_paid = tax_unit.sum(rent)
            # 606(e)(3)(B)(i): the elderly amounts need a qualified taxpayer,
            # spouse or claimed dependent aged 65 or older. A return on which
            # a filer can be claimed as a dependent (outside the claimant
            # filing exception) has no dependents (IRC 152(b)(1)), so a
            # dependent's age does not count there.
            filer = person("is_tax_unit_head_or_spouse", period)
            no_dependents = person.tax_unit(
                "head_or_spouse_is_dependent_elsewhere_without_filing_exception",
                period,
            )
            meets_age_condition = tax_unit.any(aged & (filer | ~no_dependents))

        # Qualifying real property taxes stay with the tax unit in every year:
        # 606(e)(1)(E) lets a qualified taxpayer include them "only to the
        # extent that such taxpayer or the spouse of such taxpayer ... owns or
        # has owned the residence and paid such taxes".
        real_estate_tax = add(tax_unit, period, ["real_estate_taxes"])
        equivalent_rent = rent_paid * rptc.rent_tax_equivalent
        real_estate_tax_or_equiv = real_estate_tax + equivalent_rent

        # IT-214: "Your federal adjusted gross income cannot be an amount less
        # than zero. If the amount is less than zero, enter 0."
        income = max_(income, 0)
        # IT-214-I "How to fill in Form IT-214": "enter whole dollar amounts
        # only ... drop amounts below 50 cents and increase amounts from 50 to
        # 99 cents to the next dollar" - i.e. round half up (np.round would
        # round half to even).
        income = np.floor(income + 0.5)
        # IT-214's rate and amount tables use closed integer bands ($0-3,000,
        # then 3,001-5,000, ...), so a value exactly at a band top stays in
        # that band: calc(..., right=True) over band-top thresholds, with a
        # -.inf first threshold so an income of exactly $0 lands inside the
        # first band rather than below the scale.
        income_threshold = income * rptc.excess_real_property_tax.calc(
            income, right=True
        )
        excess_rpt = max_(0, real_estate_tax_or_equiv - income_threshold)

        # Means-tested conditions. The renter cap (IT-214 line 21) applies to
        # the rent itself (average monthly rent $450 or less, i.e. annual rent
        # up to $5,400) — not to 25% of the rent, which is only used to size
        # the credit at line 22. The form applies the cap to adjusted rent (net
        # of heat, gas, electricity, furnishings, and board); PolicyEngine has
        # only gross rent, so the cap is applied to gross rent. 606(e)(7)(D)
        # tests "the adjusted rent for the residence", so through 2024 it is
        # the household's rent.
        assessed_value = add(tax_unit, period, ["assessed_property_value"])
        meets_value_conditions = (assessed_value <= rptc.max_property_value) & (
            rent_paid <= rptc.max_rent
        )

        # IT-214 income limit ("$18,000 or less").
        meets_income_condition = income <= rptc.max_agi

        # Tax Law 606(e)(7)(E) excludes an individual whom another taxpayer can
        # claim as a dependent ("You could not be claimed as a dependent",
        # IT-214), while 606(e)(6)(C) covers "a qualified taxpayer and their
        # spouse", so one qualified spouse keeps the credit.
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        eligible = (
            meets_value_conditions & meets_income_condition & (independent_filers > 0)
        )

        # From 2025 (Part RR of Chapter 59 of the Laws of 2025) the credit is a
        # flat amount looked up by federal AGI bracket, allowed only when the
        # property-tax measure exceeds the FAGI-based threshold (IT-214 line 19
        # gate). Through 2024 the credit is 50% of excess, capped by the maximum
        # chart.
        if rptc.uses_flat_amount_table:
            flat_amount = where(
                meets_age_condition,
                rptc.amount.elderly.calc(income, right=True),
                rptc.amount.non_elderly.calc(income, right=True),
            )
            gate = excess_rpt > 0
            return where(eligible & gate, flat_amount, 0)

        maximum_credit = where(
            meets_age_condition,
            rptc.maximum.elderly.calc(income, right=True),
            rptc.maximum.non_elderly.calc(income, right=True),
        )

        credit_amount = rptc.rate * excess_rpt

        return min_(eligible * credit_amount, maximum_credit)
