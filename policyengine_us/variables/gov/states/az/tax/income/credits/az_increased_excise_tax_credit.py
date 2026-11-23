from policyengine_us.model_api import *


class az_increased_excise_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Increased Excise Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_increased_excise_tax_credit_eligible"
    reference = (
        "https://www.azleg.gov/viewdocument/?docName=https://www.azleg.gov/ars/43/01072-01.htm",
        "https://www.azleg.gov/ars/43/01072-02.htm",
        "https://www.azleg.gov/ars/43/01001.htm",
        "https://www.azleg.gov/ars/42/02201.htm",
        # Form 140 line 56 instructions and worksheet.
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=25",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.increased_excise
        # Arizona counts personal and dependent exemptions under 43-1072.01(C);
        # under 43-1072.02(C), taxpayers, nonfiling spouses and dependents count.
        # Each joint filer remains a taxpayer (43-1001; 42-2201(A)(1)).
        # A claimed joint filer fails 43-1072.02(A) and cannot count as a
        # nonfiling spouse. The other filer still counts once.
        # ADOR tells joint filers to enter two without a claimed-spouse adjustment.
        # Follow the individual statutory exclusion rather than the form.
        # IRC 152(b)(1) bars dependents when either filer can be claimed,
        # unless the claimant's refund-only filing exception applies.
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        claimed_filers = tax_unit.sum(filer & claimed)
        unclaimed_filers = tax_unit.sum(filer & ~claimed)
        no_dependents = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        persons = where(
            no_dependents,
            unclaimed_filers,
            tax_unit("tax_unit_size", period) - claimed_filers,
        )
        uncapped_credit = persons * p.amount
        return min_(uncapped_credit, p.max_amount)
