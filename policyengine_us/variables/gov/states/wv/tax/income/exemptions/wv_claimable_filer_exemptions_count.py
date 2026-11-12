from policyengine_us.model_api import *


class wv_claimable_filer_exemptions_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "West Virginia exemptions for filers who can be claimed as dependents"
    documentation = (
        "Number of $500 West Virginia exemptions under W. Va. Code "
        "11-21-16(d): one for each head or spouse who can be claimed as a "
        "dependent on another return, on a return whose dependents add no "
        "exemption."
    )
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-16/",  # (d)
        "https://code.wvlegislature.gov/11-21-22A/",  # (b)
    )
    defined_for = StateCode.WV

    def formula(tax_unit, period, parameters):
        # 11-21-16(d): "a resident individual whose exemption amount for
        # federal tax purposes is zero by virtue of section 151(d)(2)", one
        # who can be claimed as a dependent, "shall be allowed a single West
        # Virginia exemption in the amount of $500". Each such filer gets one.
        person = tax_unit.members
        claimable_filers = tax_unit.sum(
            person("is_tax_unit_head_or_spouse", period)
            & person("claimable_as_dependent_on_another_return", period)
        )
        # Limit this to returns whose dependents add no exemption: a child who
        # adds none (IRC 152(b)(1)) leaves the per-filer exemption alone. When
        # dependents add exemptions, applying the single-exemption limit needs
        # an attribution rule, so those returns keep the ordinary count.
        own_exemptions = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        exemptions = tax_unit("exemptions_count", period)
        no_dependent_exemptions = exemptions == own_exemptions
        return where(no_dependent_exemptions, claimable_filers, 0)
