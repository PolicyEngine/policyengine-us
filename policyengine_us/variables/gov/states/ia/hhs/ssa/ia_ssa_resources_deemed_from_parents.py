from policyengine_us.model_api import *
from policyengine_us.variables.gov.states._ssp_parental_resources import (
    ssp_parental_resources,
    ssp_sibling_resource_share,
)


class ia_ssa_resources_deemed_from_parents(Variable):
    value_type = float
    entity = Person
    label = "Iowa SSA resources deemed from parents"
    definition_period = MONTH
    quantity_type = STOCK
    unit = USD
    defined_for = StateCode.IA
    reference = (
        "https://hhs.iowa.gov/media/3987/download?inline=#page=46",
        "https://www.law.cornell.edu/cfr/text/20/416.1202",
        "https://www.law.cornell.edu/cfr/text/20/416.1856",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330200",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330280",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330310",
        "https://secure.ssa.gov/poms.nsf/lnx/0501330340",
    )
    # Calculated from co-resident parent links and SSI countable assets, with the
    # one/two-parent allowance and eligible-child allocation. Actual SSI receipt or
    # otherwise-eligible IHHRC determines the ordinary allocation pool. Override with
    # the agency-determined amount for a deeming exception, a step-only household, other
    # state-only sibling eligibility, or a different certified resource budget. Supply
    # each affected child's amount when its allocation pool differs. Parents receiving
    # SSI are not resource deemors; other public-assistance income exclusions do not by
    # themselves exclude resources. Parent links must identify all co-resident parents.
    # The allowance follows the number of co-resident parents, including an
    # SSI-recipient parent. The cited rules do not explicitly resolve this allowance
    # interaction for unmarried parents with mixed SSI status; use an agency-determined
    # deemed-resource input for such a budget.

    def formula(person, period, parameters):
        first, second, excess = ssp_parental_resources(
            person, period, parameters, exclude_ssi_parents=True
        )
        p = parameters(period).gov.states.ia.hhs.ssa
        federal = parameters(period).gov.ssa.ssi
        child = (
            person("is_child", period.this_year)
            & (person.marital_unit.nb_persons() == 1)
            & ~person("is_household_head", period.this_year)
        )
        category = person("ia_ssa_category", period)
        home = category == category.possible_values.IN_HOME_CARE
        immigration = person("immigration_status", period.this_year)
        immigration_eligible = (
            immigration == immigration.possible_values.CITIZEN
        ) | person("is_ssi_qualified_noncitizen", period.this_year)
        cost = max_(person("ia_ssa_ihhrc_monthly_cost", period), 0)
        income = person("ia_ssa_care_countable_income", period)
        deductions = max_(person("ia_ssa_care_additional_deductions", period), 0)
        participation = max_(income - federal.amount.individual - deductions, 0)
        participation = where(
            person("ia_ssa_ihhrc_initial_partial_month", period), 0, participation
        )
        days = clip(person("ia_ssa_care_days", period), 0, period.days)
        ihhrc = (
            home
            & person("is_ssi_aged_blind_disabled", period.this_year)
            & immigration_eligible
            & person("takes_up_ssi_if_eligible", period.this_year)
            & ~person("is_incarcerated", period)
            & (cost <= p.ihhrc_cost_limit)
            & (cost * days / period.days > participation)
        )
        candidates = child & ((person("ssi", period) > 0) | ihhrc)
        own = person("ssi_countable_resources", period.this_year)
        share = ssp_sibling_resource_share(
            person,
            first,
            second,
            excess,
            candidates,
            own,
            federal.eligibility.resources.limit.individual,
        )
        return child * share
