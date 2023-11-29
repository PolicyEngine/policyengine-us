from policyengine_us.model_api import *


class ky_tuition_tax_credit_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Kentucky tuition tax credit"  # Form 8863-K
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.KY

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("ky_filing_status", period)
        # Married filing separate filers are ineligible.
        return filing_status != filing_status.possible_values.SEPARATE
