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
        # Form 140 line 56 instructions and worksheet.
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140i.pdf#page=25",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.increased_excise
        # The increased excise tax credit is allowed for each person that a
        # personal or dependent exemption can be claimed for
        # (A.R.S. 43-1072.01(C)); from 2021, 43-1072.02(C) allows $25 for each
        # person "who is either the taxpayer, the taxpayer's spouse who does
        # not file a return or a dependent". Both sections allow it only "for
        # a taxpayer who is not claimed as a dependent by any other
        # taxpayer", and the Form 140 instructions let a joint filer claim the
        # credit but not for a spouse who is barred, so a filer whom another
        # taxpayer claims is not counted. The worksheet counts dependents
        # "provided that person(s) qualifies as a dependent for federal
        # purposes": none on a return on which the filer (or, if joint,
        # either spouse) can be claimed (IRC 152(b)(1)), unless the would-be
        # claimant files only for a refund (Publication 501).
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
