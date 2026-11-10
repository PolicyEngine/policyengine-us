from policyengine_us.model_api import *


class ks_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "number of KS exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        # K.S.A. 79-32,121(a): $2,250 "for each exemption for which such
        # individual is entitled to a deduction" federally.
        "https://kslegislature.gov/li_2024s/b2023_24/statute/079_000_0000_chapter/079_032_0000_article/079_032_0121_section/079_032_0121_k/",
        "https://www.kslegislature.gov/li_2022/b2021_22/measures/documents/hb2239_enrolled.pdf#page=38",
        # IRC 151(d)(2): no personal exemption for an individual whom another
        # taxpayer is allowed to claim.
        "https://www.law.cornell.edu/uscode/text/26/151#d_2",
        "https://www.ksrevenue.gov/pdf/ip21.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip22.pdf#page=6",
        "https://www.ksrevenue.gov/pdf/ip23.pdf#page=6",
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        # K.S.A. 79-32,121(a) counts the exemptions to which the filer is
        # entitled federally. IRC 151(d)(2) denies a filer's own exemption
        # when another taxpayer is allowed to claim them, whether or not they
        # do, and applies to each spouse separately. The K-40 instructions
        # instead zero the whole return when a filer is claimed; the statute
        # governs. A head of household counts only the head: the extra
        # allowance in 79-32,121 is limited to tax year 1998.
        filers = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        # Dependents are those "you claim as a dependent" federally; under IRC
        # 152(b)(1) a return on which the filer (or, if joint, either spouse)
        # can be claimed has none, unless the would-be claimant meets the
        # filing exception (Publication 501, Dependent Taxpayer Test).
        no_dependents = tax_unit(
            "head_or_spouse_is_dependent_elsewhere_without_filing_exception", period
        )
        dependents = where(no_dependents, 0, tax_unit("tax_unit_dependents", period))
        return filers + dependents
