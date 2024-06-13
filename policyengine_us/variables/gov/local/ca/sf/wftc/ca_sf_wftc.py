from policyengine_us.model_api import *


class ca_sf_wftc(Variable):
    value_type = float
    entity = TaxUnit
    label = "San Francisco Working Families Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.local.ca.sf.wftc
        county = tax_unit.household("county_str", period)
        county_eligible = county == "SAN_FRANCISCO_COUNTY_CA"
        eitc_eligible = tax_unit("eitc_eligible", period)
        ca_eitc_eligible = tax_unit("ca_eitc_eligible", period)
        eligibility = county_eligible & (eitc_eligible | ca_eitc_eligible)
        return p.amount * eligibility
