from policyengine_us.model_api import *


class nm_low_and_middle_income_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico low- and middle income exemption"
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
        eligible = agi <= p.income_threshold[filing_status]

        # Calculate the reduction based on AGI and filing status
        reduction_threshold = max_(
            agi - p.reduction.income_threshold[filing_status], 0
        )
        reduction_amount = (
            reduction_threshold * p.reduction.rate[filing_status]
        )
        reduced_exemption_amount = p.max_amount - reduction_amount

        # Multiply the exemption amount by the number of exemptions
        exemptions = tax_unit("exemptions", period)

        return eligible * (reduced_exemption_amount * exemptions)
