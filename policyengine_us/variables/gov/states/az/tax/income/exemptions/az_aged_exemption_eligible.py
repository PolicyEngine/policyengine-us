from policyengine_us.model_api import *


class az_aged_exemption_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona aged exemption dsi eligibility"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT

        dependent_head = tax_unit("dsi", period)
        head_eligible = ~dependent_head

        dependent_spouse = tax_unit("dsi_spouse", period)
        spouse_eligible = ~dependent_spouse

        return head_eligible | spouse_eligible * joint
