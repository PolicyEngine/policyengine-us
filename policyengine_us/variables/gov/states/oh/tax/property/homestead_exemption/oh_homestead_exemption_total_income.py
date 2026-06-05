from policyengine_us.model_api import *


class oh_homestead_exemption_total_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "Ohio homestead exemption total income"
    unit = USD
    documentation = "Modified adjusted gross income of the owner and spouse for the year preceding the homestead exemption application year."
    definition_period = YEAR
    reference = "https://codes.ohio.gov/ohio-revised-code/section-323.151"

    def formula(tax_unit, period, parameters):
        return tax_unit("oh_modified_agi", period.last_year)
