from policyengine_us.model_api import *


class is_eligible_md_poverty_line_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # (3)    “Eligible low income taxpayer” means an individual, or an
        # individual and the individual’s spouse if they file a joint income
        # tax return:
        # (i) whose federal adjusted gross income as modified under
        # §§ 10–204 through 10–206 of this title does not exceed the
        # applicable poverty income level;
        AGI_COMPONENTS = [
            "adjusted_gross_income",
            "md_total_additions",
        ]
        agi_plus_md_additions = add(tax_unit, period, AGI_COMPONENTS)
        fpg = tax_unit("tax_unit_fpg", period)
        agi_below_fpg = agi_plus_md_additions <= fpg
        # (ii) whose earned income as defined under § 32(c)(2) of the
        # Internal Revenue Code does not exceed the applicable poverty
        # income level;
        earnings = tax_unit("tax_unit_earned_income", period)
        earnings_below_fpg = earnings <= fpg
        # (iii) who is not claimed as an exemption on another individual’s
        #  tax return under § 10–211 of this title;
        # SKIP - assumed throughout PolicyEngine-us.
        # (iv) for whom the credit allowed under § 10–704(a)(1) is less than the State income tax.
        # § 10–704(a)(1) is the MD total nonrefundable EITC
        # This appears to refer to MD nonrefundable EITC < state income tax
        md_non_refundable_eitc = tax_unit(
            "md_non_refundable_eitc", period
        )
        md_income_tax_before_credits = tax_unit(
            "md_income_tax_before_credits", period
        )
        eitc_less_than_income_tax = md_non_refundable_eitc < md_income_tax_before_credits
        return agi_below_fpg & earnings_below_fpg & eitc_less_than_income_tax
