from policyengine_us.model_api import *


class id_iccp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Income eligible for the Idaho Child Care Program"
    defined_for = StateCode.ID
    reference = (
        "https://adminrules.idaho.gov/rules/current/16/160612.pdf#page=7",
        "https://healthandwelfare.idaho.gov/services-programs/children-families/apply-child-care",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.id.dhw.iccp.income
        countable_income = spm_unit("id_iccp_countable_income", period)
        enrolled = spm_unit("id_iccp_enrolled", period)
        # The department's table rounds each limit up to a whole dollar. Round
        # to cents first so floating-point noise can't push a whole-dollar limit
        # up by one.
        initial_limit = np.ceil(
            np.round(
                spm_unit("id_iccp_fpg", period) * p.fpl_rate.initial_eligibility, 2
            )
        )
        continuing_limit = spm_unit("hhs_smi", period) * p.smi_rate.continuing
        return countable_income <= where(enrolled, continuing_limit, initial_limit)
