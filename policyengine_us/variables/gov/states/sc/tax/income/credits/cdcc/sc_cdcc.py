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
        p = parameters(period).gov.states.sc.tax.income.credits.cdcc

        # Get federal child care expenses
        federal_cdce = tax_unit("tax_unit_childcare_expenses", period)

        # # Married filing separate are ineligible.
        filing_status = tax_unit("filing_status", period)
        eligible = filing_status != filing_status.possible_values.SEPARATE

        # Number of qualifying people
        count_cdcc_eligible = min_(
            tax_unit("count_cdcc_eligible", period), p.dependent_cap
        )

        # Calculate total CDCC
        return (
            min_(federal_cdce * p.rate, p.amount * count_cdcc_eligible)
            * eligible
        )
