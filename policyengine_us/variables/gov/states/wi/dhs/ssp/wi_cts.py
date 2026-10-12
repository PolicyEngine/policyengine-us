from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.wi.dhs.ssp._wi_cts import cts_income_limits


class wi_cts(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin Caretaker Supplement"
    definition_period = MONTH
    unit = USD
    reference = "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf"
    defined_for = StateCode.WI

    def formula(person, period, parameters):
        p = parameters(period).gov.states.wi.dhs.ssp.cts
        members = person("wi_cts_sfu_member", period)
        subgroup = members & person("wi_cts_buening_member", period)
        gross = person("wi_cts_gross_income", period)
        net = person("wi_cts_net_income", period)
        deductions = max_(person("wi_cts_dependent_care_deduction", period), 0) + max_(
            person("child_support_expense", period), 0
        )
        assets = max_(person("wi_cts_countable_resources", period), 0)
        sub_gross, sub_net, sub_known = cts_income_limits(
            person, period, parameters, subgroup, buening=True
        )
        needy = (
            (person.family.sum(subgroup * gross) <= sub_gross)
            & (max_(person.family.sum(subgroup * (net - deductions)), 0) <= sub_net)
            & (person.family.sum(subgroup * assets) <= p.resource_limit)
        )
        members = members & ~(subgroup & ~needy)
        gross_limit, net_limit, known = cts_income_limits(
            person, period, parameters, members
        )
        financially_eligible = (
            (person.family.sum(members * gross) <= gross_limit)
            & (max_(person.family.sum(members * (net - deductions)), 0) <= net_limit)
            & (person.family.sum(members * assets) <= p.resource_limit)
        )
        children = person.family.sum(members & person("wi_cts_child_eligible", period))
        amount = (children > 0) * p.first_child + max_(
            children - 1, 0
        ) * p.additional_child
        return (
            amount
            * financially_eligible
            * known
            * sub_known
            * ~person.family("wi_cts_nonfinancially_ineligible", period)
            * person("wi_cts_payee", period)
        )
