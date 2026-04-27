from policyengine_us.model_api import *


class wa_pte_combined_disposable_income(Variable):
    value_type = float
    entity = TaxUnit
    unit = USD
    definition_period = YEAR
    label = (
        "Washington Senior/Disabled Property Tax Exemption combined disposable income"
    )
    defined_for = StateCode.WA
    reference = (
        "https://app.leg.wa.gov/RCW/default.aspx?cite=84.36.383",
        "https://app.leg.wa.gov/WAC/default.aspx?cite=458-16A-120",
        "https://dor.wa.gov/sites/default/files/2022-02/PTExemption_Senior.pdf#page=2",
    )

    adds = "gov.states.wa.dor.property_tax_exemption.senior_disabled.income.sources"
    subtracts = "gov.states.wa.dor.property_tax_exemption.senior_disabled.income.deductions.sources"
