from policyengine_us.model_api import *


class ks_count_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "number of KS exemptions"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ksrevenue.gov/pdf/ip21.pdf"
        "https://www.ksrevenue.gov/pdf/ip22.pdf"
    )
    defined_for = StateCode.KS

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        statuses = filing_status.possible_values
        joint = filing_status == statuses.JOINT
        hoh = filing_status == statuses.HEAD_OF_HOUSEHOLD
        adults = where(joint | hoh, 2, 1)
        dependents = tax_unit("tax_unit_dependents", period)
        return adults + dependents
