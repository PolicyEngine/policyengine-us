from policyengine_us.model_api import *


class is_eligible_md_poverty_line_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-709/"

    def formula(tax_unit, period, parameters):
        # (3)    “Eligible low income taxpayer” means an individual, or an
        # individual and the individual’s spouse if they file a joint income
        # tax return:
        # (i)    whose federal adjusted gross income as modified under
        # §§ 10–204 through 10–206 of this title does not exceed the
        # applicable poverty income level;
        AGI_COMPONENTS = [
            "adjusted_gross_income",
            "md_total_additions",
        ]
        agi_plus_md_additions = add(tax_unit, period, AGI_COMPONENTS)
        fpg = tax_unit("tax_unit_fpg", period)
        agi_below_fpg = agi_plus_md_additions <= fpg
        # (ii)    whose earned income as defined under § 32(c)(2) of the
        # Internal Revenue Code does not exceed the applicable poverty
        # income level;
        earnings = tax_unit("tax_unit_earned_income", period)
        earnings_below_fpg = earnings <= fpg
        # (iii)    who is not claimed as an exemption on another individual’s
        #  tax return under § 10–211 of this title;
        # SKIP - assumed throughout openfisca-us.
        # (iv)    for whom the credit allowed under § 10–704(a)(1) of this
        # subtitle is less than the State income tax.
        # This appears to refer to the MD total EITC per
        # https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-704/
        # However, the tax form indicates it's only the non-refundable portion,
        # because it gets pooled with other non-refundable credits.
        md_eitc = tax_unit(
            "md_non_single_childless_non_refundable_eitc", period
        )
        md_income_tax_before_credits = tax_unit(
            "md_income_tax_before_credits", period
        )
        eitc_less_than_income_tax = md_eitc < md_income_tax_before_credits
        in_md = tax_unit.household("state_code_str", period) == "MD"
        return (
            agi_below_fpg
            & earnings_below_fpg
            & eitc_less_than_income_tax
            & in_md
        )
