from policyengine_us.model_api import *


class nc_scca_market_rate(Variable):
    value_type = int
    entity = Person
    label = "North Carolina Subsidized Child Care Assistance (SCCA) program market rate"
    reference = (
        "https://ncchildcare.ncdhhs.gov/Portals/0/documents/pdf/M/Market_Rates_Centers_Eff_10-1.pdf?ver=9w52alSPhmrmo0N9gGVMEw%3d%3d"
        "https://docs.google.com/spreadsheets/d/1y7p8qkiOrMAM42rtSwT_ZXeA5tzew4edNkrTXACxf4M/edit?gid=1339413807#gid=1339413807"
    )
    definition_period = MONTH
    defined_for = StateCode.NC

    def formula(person, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.scca
        county = person.household("county_str", period)
        age_group = person("nc_scca_age_group", period)
        return p.childcare_market_rates[county][age_group]
