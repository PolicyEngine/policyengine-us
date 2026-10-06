from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_property_tax_rebate_received(Variable):
    value_type = float
    entity = Person
    label = "Montana property tax rebate received, in elderly homeowner/renter credit gross household income"
    documentation = (
        "The Montana property tax rebate for the prior property tax year, "
        "claimed from August 15 to October 1 of this year, allocated to the "
        "tax unit head."
    )
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # 2024 Schedule 2EC, line 8: "the 2023 Montana property tax rebate"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2024_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
        # 2025 Schedule 2EC, line 8: "the 2024 Montana property tax rebate"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=45",
    )

    def formula(person, period, parameters):
        # The rebate for tax year 2023 property taxes was claimed from
        # August 15 to October 1, 2024, so it counts on the 2024 schedule. It
        # is the rebate computed on last year's property taxes, which is 0
        # when the inputs cover only this year.
        head = person("is_tax_unit_head", period)
        return head * person.tax_unit("mt_property_tax_rebate", period.last_year)
