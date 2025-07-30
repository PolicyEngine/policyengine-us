from policyengine_us.model_api import *


class mi_surtax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Michigan surtax"
    defined_for = StateCode.MI
    unit = USD
    definition_period = YEAR

    def formula(tax_unit, period, parameters):
        # Check if surtax is in effect
        in_effect = parameters(
            period
        ).gov.contrib.states.mi.surtax.rate.in_effect
        if not in_effect:
            return 0

        taxable_income = tax_unit("mi_taxable_income", period)
        filing_status = tax_unit("filing_status", period)

        # Get surtax parameters based on filing status
        if filing_status == FilingStatus.JOINT:
            surtax_params = parameters(
                period
            ).gov.contrib.states.mi.surtax.joint
        else:
            surtax_params = parameters(
                period
            ).gov.contrib.states.mi.surtax.single

        # Calculate surtax using marginal rate structure
        surtax = 0
        for bracket in surtax_params.brackets:
            threshold = bracket.threshold
            rate = bracket.rate

            if taxable_income > threshold:
                surtax += (taxable_income - threshold) * rate
                break

        return surtax
