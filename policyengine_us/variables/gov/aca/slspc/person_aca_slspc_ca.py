from policyengine_us.model_api import *
from policyengine_core.parameters.operations import (
    homogenize_parameter_structures,
)


class person_aca_slspc_ca(Variable):
    value_type = float
    entity = Person
    label = "Second-lowest ACA silver-plan cost for person in California"
    unit = USD
    definition_period = YEAR
    defined_for = "is_aca_ptc_eligible_ca"

    def formula(person, period, parameters):
        # access parameter tree for CA
        ptree = person.simulation.tax_benefit_system.parameters
        if not hasattr(ptree.gov.aca, "ca_"):
            aca_params = ParameterNode(
                directory_path=REPO / "params_on_demand" / "gov" / "aca" / "ca"
            )
            aca_params = homogenize_parameter_structures(
                aca_params,
                person.simulation.tax_benefit_system.variables,
            )
            ptree.gov.aca.add_child("ca_", aca_params)
        # specify ACA geographic rating area
        aca_gra = ptree.gov.aca.ca_.gra(period)
        CA_FIPS = 6
        in_state = person.household("state_fips", period) == CA_FIPS
        cofips = person.household("county_fips", period)
        LA_COUNTY_FIPS = 37
        in_la_county = cofips == LA_COUNTY_FIPS
        zip3 = person.household("aca_zip3_ca_county_la", period)
        idx = where(in_la_county, zip3, cofips)
        gra = aca_gra[in_state * idx].astype(int)
        # specify ACA second-lowest silver-plan cost
        aca_slspc = ptree.gov.aca.ca_.slspc(period)
        age = person("aca_slspc_trimmed_age", period)
        return aca_slspc[gra][age]
