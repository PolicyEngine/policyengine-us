from policyengine_us.model_api import *


class s770_niit_nol_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "NOL deduction already included in supplied NII"
    documentation = "Validated section 172 deduction already subtracted from net_investment_income. The active option adds it back to broadened NII if deny_nol is true. Supply only an amount actually deducted from the NII input, not an AGI deduction or a signed business loss. Baseline source formulas contain no federal NOL deduction; default zero does not assert complete NOL coverage."
    unit = USD
    definition_period = YEAR
    reference = "https://www.congress.gov/bill/119th-congress/senate-bill/770/text"
