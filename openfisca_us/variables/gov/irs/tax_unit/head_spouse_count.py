from openfisca_us.model_api import *


class head_spouse_count(Variable):
    value_type = int
    entity = TaxUnit
    label = "Head and spouse count"
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
    filing_status = tax_unit("filing_status", period)
    head_spouse_count = where(filing_status == filing_status.possible_values.JOINT, 2, 1)
    return head_spouse_count
