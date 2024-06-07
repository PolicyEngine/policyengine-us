from policyengine_us.model_api import *


class ny_ctc_claimed_additional_credits(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claimed additional credits applicable for the NY CTC Worksheet B"
    definition_period = YEAR
    documentation = ("Filers in New York are requirede to file the Worksheet B for Form IT-213, Line 6 if they claimed any of the following federal tax credits: adoption credit, mortgage interest credit, carryforward of District of Columbia firsttime homebuyer credit, or residential energy efficient property credit; or excluded income from Puerto Rico; or filed federal Form 2555 or Form 4563.")
    reference = "https://www.tax.ny.gov/pdf/2021/inc/it213i_2021.pdf#page=3"
    defined_for = StateCode.NY


    def formula(tax_unit, period, parameters):
        # We currently do not include the adoption credit, mortgage interest credit, 
        # carryforward of District of Columbia first time homebuyer credit
        applicable_credits = tax_unit("residential_clean_energy_credit", period)
        return applicable_credits > 0 
