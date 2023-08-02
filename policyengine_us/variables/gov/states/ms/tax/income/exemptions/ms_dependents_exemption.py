from policyengine_us.model_api import *


class ms_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Mississippi qualified and other dependent children exemption"
    reference = "https://www.dor.ms.gov/sites/default/files/Forms/Individual/80100221.pdf#page=5"
    definition_period = YEAR
    defined_for = StateCode.MS

    def formula(tax_unit, period, parameters):
        # Then get the MS Exemptions part of the parameter tree.
        p = parameters(period).gov.states.ms.tax.income.exemptions.dependents

        # Total the number of dependents.
        dependents = tax_unit("tax_unit_dependents", period)

        # Get their dependent exemption amount based on their filing status.
        return dependents * p.amount
