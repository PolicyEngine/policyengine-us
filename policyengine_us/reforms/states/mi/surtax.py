from policyengine_us.model_api import *
from policyengine_core.periods import period as period_

def create_mi_surtax() -> Reform:
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

    class mi_income_tax(Variable):
        value_type = float
        entity = TaxUnit
        label = "Michigan income tax"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.MI

        adds = ["mi_income_tax_before_refundable_credits", "mi_surtax"]
        subtracts = ["mi_refundable_credits"]

    class reform(Reform):  
        def apply(self):  
            self.update_variable(mi_income_tax)  
            self.update_variable(mi_surtax)  

    return reform

def create_mi_surtax_reform(  
    parameters, period, bypass: bool = False  
):  
    if bypass:  
        return create_mi_surtax()  

    p = parameters.gov.contrib.states.mi.surtax  

    reform_active = False  
    current_period = period_(period)  

    for i in range(5):  
        if p(current_period).in_effect:  
            reform_active = True  
            break  
        current_period = current_period.offset(1, "year")  

    if reform_active:  
        return create_mi_surtax()  
    else:  
        return None  
