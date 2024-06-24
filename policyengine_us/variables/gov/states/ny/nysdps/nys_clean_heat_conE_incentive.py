from policyengine_us.model_api import *


class nys_clean_heat_conE_incentive(Variable):
    value_type = float # only if it's residential
    entity = TaxUnit
    label = "New York State Clean Heat incentive (con Edison)"
    documentation = "The incentive for purchasing and installing a heat pump"
    "The tax credit for a qualified purchase or lease of geothermal energy system equipment, with a 5-year carryover."
    
    unit = USD
    definition_period = YEAR
    reference = "https://cleanheat.ny.gov/assets/pdf/CECONY%20Clean%20Heat%20Program%20Manual%206%203%2024.pdf"
    defined_for = StateCode.NY

    def formula(tax_unit, parameters, period):
        p = parameters(period).gov.states.ny.nysdps.nys_clean_heat

        var0 = tax_unit("nys_clean_heat_conE_family_type", period)

        if var0.status == 'Residential':
            var1 = tax_unit("nys_clean_heat_conE_heat_pump", period)
            var2 = tax_unit("nys_clean_heat_conE_family_dac", period)
            
            if var1.status == 'ASHP':
                var3 = tax_unit("nys_clean_heat_conE_home", period)
                var4 = tax_unit("nys_clean_heat_conE_heat_pump_type", period)
                uncapped_incentive = \
                    p.conE_incentive[var0.status[var1.status[var2.status[var3[var4.status]]]]]
            else:
                uncapped_incentive = p.conE_incentive[var0.status[var1.status[var2.status]]]

            # calc cap
            cost = tax_unit("nys_clean_heat_conE_project_cost", period)
            rate = p.conE_rate[var2]
            cap = cost * rate

            incentive = min(uncapped_incentive, cap)


        else:
            pass # for Multifamily

        return incentive