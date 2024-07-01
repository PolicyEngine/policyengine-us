from policyengine_us.model_api import *


class me_property_tax_fairness_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the maine property tax fairness credit"
    definition_period = YEAR
    defined_for = StateCode.ME

    def formula(tax_unit, period, parameters):
        # Separate filers are ineligible
        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        separate = filing_status == filing_statuses.SEPARATE
        return ~separate
