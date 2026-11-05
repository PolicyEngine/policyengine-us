from policyengine_us.model_api import *


class md_personal_exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maryland personal exemptions count"
    documentation = (
        "Number of exemptions under Md. Code, Tax-General 10-211(a) and "
        "(b)(1): one for each filer who cannot be claimed as a dependent on "
        "another return, plus one for each dependent unless a filer can be "
        "claimed (outside the claimant filing exception)."
    )
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
        # PDF pages 12-13: filing status 6 and Instruction 8.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        # § 10-211(a) allows an exemption for each filer and for each
        # dependent "as defined in § 152 of the Internal Revenue Code". A
        # person who can be claimed on another return is a dependent taxpayer
        # (filing status 6): "You do not get an exemption for yourself".
        # Maryland requires a married filer who can be claimed to file a
        # separate return, where each spouse claims their own exemption and
        # the spouses split "the overall number of dependents" of the federal
        # return. Under IRC 152(b)(1) that return has none when either spouse
        # can be claimed, unless the would-be claimant meets the filing
        # exception (Publication 501, Dependent Taxpayer Test).
        claimable_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        own = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        no_dependents = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependents = where(no_dependents, 0, tax_unit("tax_unit_dependents", period))
        return where(
            claimable_filer, own + dependents, tax_unit("tax_unit_size", period)
        )
