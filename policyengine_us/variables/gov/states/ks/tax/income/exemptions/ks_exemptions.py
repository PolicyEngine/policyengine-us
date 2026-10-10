from policyengine_us.model_api import *


class ks_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Kansas exemptions amount"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/",
        "https://ksrevisor.gov/statutes/chapters/ch79/079_032_0121b.html",
        "https://www.ksrevenue.gov/pdf/ip24.pdf#page=6",
        "https://www.ksrevenue.gov/faqs-taxii.html",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions
        veteran_exemptions_count = add(
            tax_unit,
            period,
            ["ks_disabled_veteran_exemptions_eligible_person"],
        )
        veterans_exemption_amount = veteran_exemptions_count * p.disabled_veteran.base

        if p.by_filing_status.in_effect:
            filing_status = tax_unit("filing_status", period)
            base_amount = p.by_filing_status.amount[filing_status]
            # K.S.A. 79-32,121b allows the dependent amount for each dependent
            # "for which such taxpayer is entitled to a deduction" federally;
            # under IRC 152(b)(1) a return on which the filer (or, if joint,
            # either spouse) can be claimed has none ("enter '0' in the number
            # of dependents box"). The filing-status amount stays: a claimable
            # taxpayer "will qualify for the personal exemption allowance"
            # (Kansas Department of Revenue FAQ).
            filer_is_dependent = tax_unit(
                "head_or_spouse_is_dependent_elsewhere", period
            )
            dependents = where(
                filer_is_dependent, 0, tax_unit("tax_unit_dependents", period)
            )
            dependent_amount = p.by_filing_status.dependent * dependents
            head_of_household = (
                filing_status == filing_status.possible_values.HEAD_OF_HOUSEHOLD
            )
            head_of_household_additional_amount = (
                head_of_household * p.by_filing_status.hoh_additional_amount
            )
            return (
                base_amount
                + dependent_amount
                + veterans_exemption_amount
                + head_of_household_additional_amount
            )
        exemptions_count = tax_unit("ks_count_exemptions", period)
        return exemptions_count * p.consolidated.amount + veterans_exemption_amount
