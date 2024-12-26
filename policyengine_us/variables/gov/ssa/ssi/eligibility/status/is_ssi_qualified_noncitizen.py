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
        # For legal permanent residents, check if they have enough qualifying quarters
        meets_earnings_requirement = (
            qualifying_quarters_earnings
            >= p.income.sources.qualifying_quarters_threshold
        )

        # Non-LPRs automatically meet the earnings requirement
        # LPRs must meet the earnings threshold
        earnings_requirement_satisfied = (
            ~legal_permanent_resident
        ) | meets_earnings_requirement

        # Convert immigration status to string and check if it's in the list of qualified statuses
        immigration_status_str = immigration_status.decode_to_str()
        has_qualifying_status = np.isin(
            immigration_status_str,
            p.eligibility.status.qualified_noncitizen_status,
        )
        return has_qualifying_status & earnings_requirement_satisfied
