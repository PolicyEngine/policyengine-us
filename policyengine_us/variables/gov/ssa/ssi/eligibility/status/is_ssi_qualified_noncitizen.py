from policyengine_us.model_api import *


class is_ssi_qualified_noncitizen(Variable):
    value_type = bool
    entity = Person
    label = "Is an SSI qualified noncitizen"
    definition_period = YEAR

    def formula(person, period, parameters):
        qualifying_quarters_earnings = person(
            "ssi_qualifying_quarters_earnings", period
        )
        qualifying_quarters_threshold = parameters(
            period
        ).gov.ssa.ssi.income.sources.qualifying_quarters_threshold
        qualified_statuses = parameters(
            period
        ).gov.ssa.ssi.eligibility.status.qualified_noncitizen_status

        immigration_status = person("immigration_status", period)
        legal_permanent_resident = (
            immigration_status
            == immigration_status.possible_values.LEGAL_PERMANENT_RESIDENT
        )
        earnings_quarters_eligible = where(
            legal_permanent_resident,
            qualifying_quarters_earnings >= qualifying_quarters_threshold,
            True,
        )
        immigration_status_str = immigration_status.decode_to_str()

        qualifies_based_on_status = np.isin(
            immigration_status_str, qualified_statuses
        )
        return where(
            qualifies_based_on_status,
            earnings_quarters_eligible,
            False,
        )
