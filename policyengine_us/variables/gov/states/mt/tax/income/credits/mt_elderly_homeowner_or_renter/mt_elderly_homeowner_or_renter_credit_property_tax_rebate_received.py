from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received(Variable):
    value_type = float
    entity = Person
    label = "Montana property tax rebate received, in elderly homeowner/renter credit gross household income"
    documentation = (
        "Montana property tax rebate cash actually received by this person "
        "during the year. Defaults to zero: prior-year property taxes or a "
        "calculated entitlement do not establish eligibility, a claim, or receipt."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # SB542 eligibility and claim requirements, PDF pages 2-3.
        "https://archive.legmt.gov/content/Sessions/69th/Contractor_index/CH0767.pdf#page=2",
        "https://archive.legmt.gov/bills/2021/HB0199/HB0191_X.pdf#page=2",
        # 2024 Schedule 2EC, line 8: "the 2023 Montana property tax rebate"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
        # 2025 Schedule 2EC, line 8: "the 2024 Montana property tax rebate"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=45",
    )

    # Actual receipt input: SB542 sections 1(3) and 3(5) require qualifying
    # ownership/occupancy, paid taxes, and a claim. The model's separate
    # mt_property_tax_rebate amount calculation omits those requirements.
