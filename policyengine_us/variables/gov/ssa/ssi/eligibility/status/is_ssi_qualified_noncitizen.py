from policyengine_us.model_api import *


class is_ssi_qualified_noncitizen(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI qualified noncitizen"
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500502100"

    def formula(person, period, parameters):
        qualifying_quarters_earnings = person(
            "ssi_qualifying_quarters_earnings", period
        )
        p = parameters(period).gov.ssa.ssi
        immigration_status = person("immigration_status", period)
        legal_permanent_resident = (
            immigration_status
            == immigration_status.possible_values.LEGAL_PERMANENT_RESIDENT
        )
        # Need qualifying quarters if person is a legal permanent resident.
        has_qualifying_quarters = (
            qualifying_quarters_earnings
            >= p.income.sources.qualifying_quarters_threshold
        )
        earnings_quarters_eligible = where(
            legal_permanent_resident,
            has_qualifying_quarters,
            True,
        )
        immigration_status_str = immigration_status.decode_to_str()
        qualifies_based_on_status = np.isin(
            immigration_status_str,
            p.eligibility.status.qualified_noncitizen_status,
        )
        return qualifies_based_on_status & earnings_quarters_eligible
