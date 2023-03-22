from policyengine_us.model_api import *


class nj_dependents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Jersey qualified and other dependent children exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NJ

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        # filing_status = tax_unit("filing_status", period)
        # joint = filing_status == filing_status.possible_values.JOINT

        # Then get the NJ Exemptions part of the parameter tree.
        p = parameters(period).gov.states.nj.tax.income.exemptions.dependents

        # Total the number of dependents.
        dependents = tax_unit("tax_unit_dependents", period)

        # Get their dependent exemption amount based on their filing status.
        return dependents * p.amount
