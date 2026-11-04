from policyengine_us.model_api import *


class wv_personal_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia personal exemption"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = (
        "https://code.wvlegislature.gov/11-21-16/",
        # Form IT-140 exemptions box (e) and line 6 instructions
        # PDF pages 3, 26
        "https://tax.wv.gov/Documents/PIT/2025/it140.PersonalIncomeTaxFormsAndInstructions.2025.pdf#page=3",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.wv.tax.income.exemptions
        # Section 11-21-16(d) grants each claimable individual $500.
        # Limit this correction to returns without lawful dependent
        # exemptions: applying the single-exemption limit when dependents
        # add exemptions requires attribution. A child who adds no exemption
        # (IRC 152(b)(1)) leaves the per-filer amount alone.
        person = tax_unit.members
        claimable_filers = tax_unit.sum(
            person("is_tax_unit_head_or_spouse", period)
            & person("claimable_as_dependent_on_another_return", period)
        )
        own_exemptions = tax_unit("head_spouse_count_not_dependent_elsewhere", period)
        filer_allowances = (
            p.personal * own_exemptions + p.base_personal * claimable_filers
        )
        exemptions = tax_unit("exemptions_count", period)
        lawful_dependent_exemptions = exemptions - own_exemptions
        childless_claimable = (lawful_dependent_exemptions == 0) & (
            claimable_filers > 0
        )
        # Preserve the existing dependent allocation pending resolution.
        ordinary_amount = where(
            exemptions == 0, p.base_personal, p.personal * exemptions
        )
        return where(childless_claimable, filer_allowances, ordinary_amount)
