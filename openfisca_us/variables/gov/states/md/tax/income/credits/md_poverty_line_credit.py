from openfisca_us.model_api import *


class md_poverty_line_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://casetext.com/statute/code-of-maryland/article-tax-general/title-10-income-tax/subtitle-7-income-tax-credits/section-10-704-effective-until-6302023-for-earned-income"

    def formula(tax_unit, period, parameters):
        # Get the federal poverty line for the tax_unit
        # Find the number of persons in your family/household from the chart that is the same as the number of persons entered on your federal tax return. Enter the income level that corresponds to the number of person
        fpg = tax_unit("tax_unit_fpg", period)
        # Get the tax unit's earned income
        earned_income = tax_unit("tax)unit_earned_income", period)
        # Get total of md_agi and md_total_additions

        agi_plus_md_additions = add(
            tax_unit("md_agi", period), tax_unit("md_total_additions", period)
        )
        countable_income = max_(agi_plus_md_additions, earned_income)
        # Enter the amount from line 1 or 2, whichever is larger.
        is_eligible = countable_income < fpg

        eligible_income = countable_income * is_eligible

        # 5. Multiply line 2 by 5% (.05). This is your State Poverty Level
        # Credit. Enter that amount here and on line 23 of Form 502.
        # (Part-year residents or members of the military,
        # see Instruction 26(o))
        rate = parameters(
            period
        ).gov.states.md.tax.income.credits.md_poverty_line_credit_rate
        credit = eligible_income * rate
        md_eitc = tax_unit("md_eitc", period)
        # Return the minimum of the two
        return min_(credit, md_eitc)
