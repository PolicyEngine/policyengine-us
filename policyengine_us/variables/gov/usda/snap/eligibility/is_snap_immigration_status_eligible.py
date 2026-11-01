from policyengine_us.model_api import *


class is_snap_immigration_status_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Person is eligible for SNAP due to immigration status"
    definition_period = MONTH
    reference = (
        "https://www.law.cornell.edu/uscode/text/7/2015#f",
        "https://www.law.cornell.edu/uscode/text/8/1612",
        "https://www.law.cornell.edu/cfr/text/7/273.4#a_6",
        "https://www.fns.usda.gov/snap/obbb-alien-eligibility",
    )

    def formula(person, period, parameters):
        immigration_status = person("immigration_status", period.this_year)
        immigration_status_str = immigration_status.decode_to_str()

        p = parameters(period).gov.usda.snap.eligibility
        federal_eligible = np.isin(
            immigration_status_str,
            p.eligible_immigration_statuses,
        )
        ca_eligible = person("ca_snap_immigration_status_eligible", period)
        # 8 USC 1612(a) and 7 CFR 273.4(a)(6) apply on top of the 7 USC
        # 2015(f) status list, including in California during its delayed
        # implementation of P.L. 119-21 sec. 10108 (CDSS ACL 25-92).
        waiting_period = person("meets_snap_qualified_alien_waiting_period", period)
        return (federal_eligible | ca_eligible) & waiting_period
