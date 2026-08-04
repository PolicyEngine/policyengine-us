from policyengine_us.model_api import *


class ca_sf_caap_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for San Francisco County CAAP due to immigration status"
    definition_period = MONTH
    defined_for = "in_san_francisco"

    def formula(person, period, parameters):
        p = parameters(period).gov.local.ca.sf.caap
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()
        # SF's PRUCOL / humanitarian lawful-residence categories have no exact
        # ImmigrationStatus enum member; we approximate them with the
        # humanitarian set in the whitelist (SEC. 20.7-6). The manual lists
        # several additional humanitarian categories as eligible that have no
        # ImmigrationStatus enum member, so we don't treat them as eligible at
        # the moment:
        #   - COFA permanent residents (citizens of the Federated States of
        #     Micronesia, the Marshall Islands, and Palau).
        #   - VAWA self-petitioners.
        #   - U-visa holders (victims of crime).
        #   - T-visa holders (victims of trafficking).
        #   - Special Immigrant Visa (SIV) holders.
        return np.isin(immigration_status_str, p.qualified_immigration_status)
