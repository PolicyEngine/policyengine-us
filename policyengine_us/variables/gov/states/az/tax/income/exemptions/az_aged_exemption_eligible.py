from policyengine_us.model_api import *


class az_aged_exemption_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for the Arizona aged exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE

        dependent_head = tax_unit("head_is_dependent_elsewhere", period)
        head_eligible = ~dependent_head * separate

        dependent_spouse = tax_unit("spouse_is_dependent_elsewhere", period)
        spouse_eligible = ~dependent_spouse

        return head_eligible | spouse_eligible
