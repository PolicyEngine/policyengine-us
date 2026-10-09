from policyengine_us.model_api import *


class exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Number of tax exemptions"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Number of personal exemptions on the federal return: one for each "
        "filer who cannot be claimed as a dependent by another taxpayer, plus "
        "one for each dependent unless a filer can be claimed."
    )
    reference = (
        "https://www.law.cornell.edu/uscode/text/26/151#d_2",
        "https://www.law.cornell.edu/uscode/text/26/152#b_1",
        # Publication 501, Dependent Taxpayer Test.
        "https://www.irs.gov/pub/irs-prior/p501--2025.pdf#page=11",
        # 2017 Form 1040, line 6a: "If someone can claim you as a dependent,
        # do not check box 6a"; instructions, line 6b: the spouse box only
        # if the "spouse can't be claimed as a dependent".
        "https://www.irs.gov/pub/irs-prior/f1040--2017.pdf#page=1",
        "https://www.irs.gov/pub/irs-prior/i1040gi--2017.pdf#page=15",
    )

    def formula(tax_unit, period, parameters):
        # IRC 151(d)(2) zeroes the exemption of a filer whom another taxpayer
        # can claim, and IRC 152(b)(1) treats a return on which the filer (or,
        # if joint, either spouse) can be claimed as having no dependents. So
        # such a return counts only its filers who cannot be claimed.
        tax_unit_size = tax_unit("tax_unit_size", period)
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        independent_filers = tax_unit(
            "head_spouse_count_not_dependent_elsewhere", period
        )
        return where(filer_is_dependent, independent_filers, tax_unit_size)
