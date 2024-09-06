from policyengine_us.model_api import *


class sc_taxable_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "South Carolina taxable income"
    defined_for = StateCode.SC
    unit = USD
    definition_period = YEAR
    reference = (
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2022.pdf#page=33"
    )

    def formula(tax_unit, period, parameters):
        taxable_income = tax_unit("taxable_income", period)
        additions = tax_unit("sc_additions", period)
        subtractions = tax_unit("sc_subtractions", period)
        return max_(0, taxable_income + additions - subtractions)
