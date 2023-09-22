from policyengine_us.model_api import *


class wv_taxable_property_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "West Virginia taxable property value"
    defined_for = StateCode.WV
    unit = USD
    definition_period = YEAR
    reference = "https://code.wvlegislature.gov/11-21-21/"

    def formula(tax_unit, period, parameters):
        assessed_property_value = add(
            tax_unit, period, ["assessed_property_value"]
        )
        p = parameters(
            period
        ).gov.states.wv.tax.income.exemptions.homestead_exemption

        return max_(assessed_property_value - p.max_amount, 0)
