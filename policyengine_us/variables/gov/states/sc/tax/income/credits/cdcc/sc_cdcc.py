from policyengine_us.model_api import *


class sc_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina CDCC"
    documentation = "South Carolina Child and Dependent Care Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=22"
    )
    defined_for = StateCode.SC

    def formula(tax_unit, period, parameters):
        # Get South Carolina CDCC rate
        p = parameters(period).gov.states.sc.tax.income.credits.cdcc.rate

        # Get federal child care expenses
        federal_cdce = tax_unit("childcare_expenses", period)

        # # Married filing separate are ineligible.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE

        # Calculate total SC CDCC
        return federal_cdce * p * eligible
