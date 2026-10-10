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
        # W. Va. Code 11-21-16 allows $2,000 per federal exemption. The IT-140
        # instructions allow none for a filer who "can be claimed as a
        # dependent on another person's return" and add: "You cannot claim
        # any dependents if you can be claimed as a dependent" (IRC 151(d)(2),
        # 152(b)(1)). 11-21-16(d) gives an individual whose federal exemption
        # is zero under 151(d)(2) a single $500 exemption; the form applies it
        # once per return: "If box e is zero, enter $500 on line 6".
        exemptions = tax_unit("exemptions_count", period)
        return where(exemptions == 0, p.base_personal, p.personal * exemptions)
