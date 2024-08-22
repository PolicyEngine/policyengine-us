from policyengine_us.model_api import *


class id_pbf(Variable):
    value_type = float
    entity = TaxUnit
    label = "Idaho permanent building tax"
    definition_period = YEAR
    reference = "https://tax.idaho.gov/wp-content/uploads/forms/EIN00046/EIN00046_11-15-2021.pdf#page=10"
    defined_for = "id_pbf_liable"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.id.tax.income.other_taxes.pbf
        return p.amount
