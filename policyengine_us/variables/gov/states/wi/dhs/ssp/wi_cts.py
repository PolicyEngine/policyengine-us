from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import (
    cts_filing_unit,
    cts_financial_test,
)


class wi_cts(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin Caretaker Supplement"
    definition_period = MONTH
    unit = USD
    reference = (
        "https://docs.legis.wisconsin.gov/document/statutes/49.775",
        # PDF pages 30-34, 65
        "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=30",
    )
    defined_for = StateCode.WI

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        unit, _, _ = cts_filing_unit(person, period)
        members = person("wi_cts_sfu_member", period)
        subgroup = members & person("wi_cts_buening_member", period)
        # Buening keeps the co-parent group in the unit only when it is needy.
        needy, subgroup_known = cts_financial_test(
            person, period, parameters, unit, subgroup, 0
        )
        members = members & ~(subgroup & ~needy)
        financially_eligible, known = cts_financial_test(
            person,
            period,
            parameters,
            unit,
            members,
            person.family("wi_cts_large_group_net_income_limit", period),
        )
        # Each SSI caretaker's payment covers their own assistance group, and
        # the caretaker shares the filing unit of those children.
        children = person("wi_cts_caretaker_children", period)
        amount = (children > 0) * p.first_child + max_(
            children - 1, 0
        ) * p.additional_child
        return (
            amount
            * financially_eligible
            * known
            * subgroup_known
            * ~person.family("wi_cts_nonfinancially_ineligible", period)
        )
