from policyengine_us.model_api import *


class nm_low_and_middle_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico low- and middle-income exemption"
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nm.tax.income.exemptions.low_and_middle_income
        filing_status = tax_unit("filing_status", period)
        agi = tax_unit("adjusted_gross_income", period)

        # Calculate the eligibility based on AGI and filing status
        eligible = agi <= p.income_limit[filing_status]

        # Calculate the exemption amount based on AGI and filing status
        reduction_threshold = p.reduction.income_threshold[filing_status]
        excess = max_(agi - reduction_threshold, 0)
        reduction_rate = p.reduction.rate[filing_status]
        reduction_amount = excess * reduction_rate
        exemption_amount = p.max_amount - reduction_amount

        # Multiply the exemption amount by the number of exemptions
        exemptions = tax_unit("exemptions", period)

        return eligible * (exemption_amount * exemptions)
