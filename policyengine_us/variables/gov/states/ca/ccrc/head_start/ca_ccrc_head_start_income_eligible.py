from policyengine_us.model_api import *


class ca_ccrc_head_start_income_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "California Child Care Resource Center Head Start income eligible"
    definition_period = YEAR
    reference = (
        "https://www.ccrcca.org/headstart/programs/eligibility-requirements/"
    )
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.ccrc.head_start.eligibility
        fpg = tax_unit("tax_unit_fpg", period)
        income_limit = fpg * p.fpg_fraction
        # CCRC website doesn't specify which income source to use
        ca_agi = tax_unit("ca_agi", period)
        return ca_agi <= income_limit
