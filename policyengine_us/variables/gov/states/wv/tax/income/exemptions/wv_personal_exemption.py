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
        # $2,000 for each exemption on the return, plus the 11-21-16(d) $500
        # for each filer who can be claimed as a dependent, on a return whose
        # dependents add no exemption. Other returns keep the ordinary count.
        exemptions = tax_unit("exemptions_count", period)
        claimable_filer_exemptions = tax_unit(
            "wv_claimable_filer_exemptions_count", period
        )
        amount = p.personal * exemptions + p.base_personal * claimable_filer_exemptions
        # IT-140 line 6 gives $500 to a return with no exemption at all, which
        # an input of zero for tax_unit_size can produce.
        no_exemption = (exemptions + claimable_filer_exemptions) == 0
        return where(no_exemption, p.base_personal, amount)
