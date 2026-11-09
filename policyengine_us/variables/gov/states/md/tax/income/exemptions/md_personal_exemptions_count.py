from policyengine_us.model_api import *


class md_personal_exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Maryland personal exemptions count"
    documentation = (
        "Number of exemptions under Md. Code, Tax-General 10-211(a) and "
        "(b)(1): one for each filer, including a filer who can be claimed as "
        "a dependent on another return, plus one for each dependent unless a "
        "filer can be claimed (outside the claimant filing exception)."
    )
    definition_period = YEAR
    defined_for = StateCode.MD
    reference = (
        "https://mgaleg.maryland.gov/mgawebsite/Laws/StatuteText?article=gtg&section=10-211&enactments=false",
        # PDF pages 1-2: 2018 ch. 575 adds subsection (a) and strikes the
        # § 151 reference from (b)(1).
        "https://mgaleg.maryland.gov/2018RS/chapters_noln/Ch_575_sb0184E.pdf#page=1",
        # PDF pages 12-13: filing status 6 and Instruction 8.
        "https://www.marylandcomptroller.gov/content/dam/mdcomp/tax/instructions/2025/resident-booklet.pdf#page=12",
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
    )

    def formula(tax_unit, period, parameters):
        # § 10-211(a)(1) allows an exemption for "the taxpayer" with no
        # dependency condition; the section imposes one only on a spouse
        # claimed on a separate return, in (a)(2)(ii). Since 2018 ch. 575,
        # (b)(1) allows $3,200 for each exemption under (a), no longer for
        # each exemption deductible under IRC § 151, so the federal denial
        # for a dependent (§ 151(d)(2)) no longer reaches Maryland. Each
        # filer keeps their own exemption, also on a separate Maryland
        # return. The 2025 booklet's filing status 6 gives a claimable filer
        # none; the model follows the statute.
        # § 10-211(a)(3) adds each dependent "as defined in § 152 of the
        # Internal Revenue Code". Under IRC 152(b)(1) a return on which the
        # filer (or, if joint, either spouse) can be claimed has none, unless
        # the would-be claimant meets the filing exception (Publication 501,
        # Dependent Taxpayer Test). On separate Maryland returns the spouses
        # split "the overall number of dependents" of the federal return.
        no_dependents = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependents = tax_unit("tax_unit_dependents", period)
        return tax_unit("tax_unit_size", period) - where(no_dependents, dependents, 0)
