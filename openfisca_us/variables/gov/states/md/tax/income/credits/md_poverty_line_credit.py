from openfisca_us.model_api import *


class md_poverty_line_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"

    def formula(tax_unit, period, parameters):
        # Get the federal poverty line for the tax_unit
        # Find the number of persons in your family/household from the chart that is the same as the number of persons entered on your federal tax return. Enter the income level that corresponds to the number of person
        fpg = tax_unit("tax_unit_fpg", period)
        # Get the tax unit's earned income
        earned_income = tax_unit("tax_unit_earned_income", period)
        # Get total of md_agi and md_total_additions
        # From the law:
        # (2)    “Applicable poverty income level” means the amount specified in the poverty income standard that corresponds to the number of exemptions which the individual is allowed and claims under § 10–211(b)(1) of this title.

        # (3)    “Eligible low income taxpayer” means an individual, or an individual and the individual’s spouse if they file a joint income tax return:
        #     (i)    whose federal adjusted gross income as modified under §§ 10–204 through 10–206 of this title does not exceed the applicable poverty income level;
        agi_plus_md_additions = add(
            tax_unit,
            period,
            [
                "adjusted_gross_income",
                "md_total_additions",
            ],
        )
        # Enter the amount from line 1 or 2, whichever is larger.
        eligible = max_(agi_plus_md_additions, earned_income) <= fpg

        # 5. Multiply line 2 by 5% (.05). This is your State Poverty Level
        # Credit. Enter that amount here and on line 23 of Form 502.
        # (Part-year residents or members of the military,
        # see Instruction 26(o))
        rate = parameters(
            period
        ).gov.states.md.tax.income.credits.poverty_line_credit
        uncapped_plc = earned_income * rate
        md_state_non_refundable_eitc = tax_unit(
            "md_state_non_refundable_eitc", period
        )
        income_tax_before_credits = tax_unit(
            "md_income_tax_before_credits", period
        )

        plc = min_(
            income_tax_before_credits - md_state_non_refundable_eitc,
            uncapped_plc,
        )

        return plc * eligible
