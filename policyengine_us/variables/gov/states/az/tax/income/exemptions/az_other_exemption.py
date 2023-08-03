from policyengine_us.model_api import *


class az_other_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona other exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

        stillbirth = person("is_stillbirth", period).astype(int)

        

        return (stillbirth + spouse_eligible) * p.amount.other
