from policyengine_us.model_api import *


class az_senior_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona senior exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

<<<<<<< HEAD:policyengine_us/variables/gov/states/az/tax/income/exemptions/az_senior_exemption.py
        

        return stillborn * p.amount.stillborn
=======
        stillborn_children = person("is_stillbirth", period).astype(int)

        

        return stillborn_children * p.amount.other
>>>>>>> 3bc16f7ad3bdb58e5494449869d00f52d3163fd9:policyengine_us/variables/gov/states/az/tax/income/exemptions/az_other_exemption.py
