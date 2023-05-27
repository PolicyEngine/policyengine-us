from policyengine_us.model_api import *


class nh_education_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Hampshire Education Tax Credits"
    documentation = "New Hampshire Education Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = "https://www.gencourt.state.nh.us/rsa/html/NHTOC/NHTOC-V-77-G.htm"
    defined_for = StateCode.NH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.nh.tax.income.credits.education_tax_credit

        # Get Rate for donation
        donation = tax_unit("donation", period)
        rate = p.rate.calc(donation)

        # Exclude married filing separately filers.
        filing_status = tax_unit("filing_status", period)
        filing_eligible = (
            filing_status != filing_status.possible_values.SEPARATE
        )

        # Calculate total child tax credit
        return count_eligible * p.rate * filing_eligible
