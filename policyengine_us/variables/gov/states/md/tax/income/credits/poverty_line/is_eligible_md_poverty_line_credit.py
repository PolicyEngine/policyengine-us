from policyengine_us.model_api import *


class is_eligible_md_poverty_line_credit(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for MD Poverty Line Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-709&enactments=false",
        "https://www.law.cornell.edu/uscode/text/26/32#c_2",
        "https://www.law.cornell.edu/cfr/text/26/1.32-2",
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-107&enactments=false",
        # PDF pages 12, 23: filing status 6 and the poverty level credit.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
    )
    defined_for = StateCode.MD

    def formula(tax_unit, period, parameters):
        # (3)    "Eligible low income taxpayer" means an individual, or an
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
        # (2) keys the applicable poverty income level to the exemptions the
        # individual "is allowed and claims under § 10-211(b)(1)".
        fpg = tax_unit("md_poverty_line_credit_income_level", period)
        agi_below_fpg = agi_plus_md_additions <= fpg
        # (ii)    whose earned income as defined under § 32(c)(2) of the
        # Internal Revenue Code does not exceed the applicable poverty
        # income level;
        # eitc_earned_income is PolicyEngine's § 32(c)(2) measure, the one the
        # federal EITC uses: wages plus net earnings from self-employment
        # (including farm and partnership earnings) after the § 164(f)
        # deduction, netted across the filers and floored at zero.
        earnings = tax_unit("eitc_earned_income", period)
        earnings_below_fpg = earnings <= fpg
        # (iii)    who is not claimed as an exemption on another individual’s
        #  tax return under § 10–211 of this title;
        # This takes an actual claim under § 10-211 on another Maryland
        # return; being claimable is not enough. The instructions' filing
        # status 6 chart also bars a claimable but unclaimed filer; the
        # statute governs. Any filer's claim bars the return, since the
        # eligible taxpayer is "an individual, or an individual and the
        # individual's spouse if they file a joint income tax return".
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        md_claimed = person("md_claimed_as_exemption_on_another_return", period)
        claimed_elsewhere = tax_unit.any(filer & md_claimed)
        # (iv)    for whom the credit allowed under § 10–704(a)(1) of this
        # subtitle is less than the State income tax.
        # This appears to refer to the MD total EITC per
        # https://law.justia.com/codes/maryland/2021/tax-general/title-10/subtitle-7/section-10-704/
        # However, the tax form indicates it's only the non-refundable portion,
        # because it gets pooled with other non-refundable credits.
        md_eitc = tax_unit("md_married_or_has_child_non_refundable_eitc", period)
        md_income_tax_before_credits = tax_unit("md_income_tax_before_credits", period)
        eitc_less_than_income_tax = md_eitc < md_income_tax_before_credits
        return (
            agi_below_fpg
            & earnings_below_fpg
            & ~claimed_elsewhere
            & eitc_less_than_income_tax
        )
