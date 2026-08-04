from policyengine_us.model_api import *


class marketplace_effective_actuarial_value(Variable):
    value_type = float
    entity = TaxUnit
    label = "Marketplace selected plan effective actuarial value"
    unit = "/1"
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/cfr/text/45/156.140#b",
        "https://www.law.cornell.edu/cfr/text/45/156.420#a",
    )

    def formula(tax_unit, period, parameters):
        selected_plan_av = tax_unit("selected_marketplace_plan_actuarial_value", period)
        csr_av = tax_unit("marketplace_csr_actuarial_value", period)
        return max_(selected_plan_av, csr_av)
