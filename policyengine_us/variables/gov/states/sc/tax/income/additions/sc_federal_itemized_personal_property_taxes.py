from policyengine_us.model_api import *


class sc_federal_itemized_personal_property_taxes(Variable):
    value_type = float
    entity = TaxUnit
    label = "Personal property taxes reported on federal Schedule A for South Carolina"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.SC
    documentation = (
        "Federal Schedule A line 5c, separate from real estate taxes. "
        "When providing the filed federal deduction, include the deductible "
        "personal property tax in the federal Schedule A inputs as well."
    )
    reference = "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2025.pdf#page=4"
