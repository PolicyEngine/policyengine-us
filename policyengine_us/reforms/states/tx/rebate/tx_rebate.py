"""Texas "Money in Your Pocket" one-time rebate reform.

Proposal: Gina Hinojosa's "Money in Your Pocket" economic agenda proposes a
one-time $1,500 rebate check to Texas families, funded by an ~$17 billion draw
on the state's Economic Stabilization Fund.
Source: https://ginafortexas.com/2026/07/recap-gina-hinojosa-launches-money-in-your-pocket-economic-agenda-across-houston-san-antonio-and-laredo/

Modeling assumptions: the proposal does not specify the eligibility unit or an
income limit. PolicyEngine models one check per household with no income limit --
the reading consistent with the campaign's stated ~$17 billion Economic
Stabilization Fund draw. The campaign's "families" are therefore operationalized
as households. The rebate is paid once (2027) and reverts to $0 from 2028.
"""

from policyengine_us.model_api import *
from policyengine_core.periods import period as period_
from policyengine_core.periods import instant
from policyengine_us.tools.parameters import add_to_list_parameter


def create_tx_rebate() -> Reform:
    class tx_rebate(Variable):
        value_type = float
        entity = Household
        label = "Texas rebate check"
        unit = USD
        definition_period = YEAR
        defined_for = StateCode.TX
        reference = "https://ginafortexas.com/2026/07/recap-gina-hinojosa-launches-money-in-your-pocket-economic-agenda-across-houston-san-antonio-and-laredo/"

        def formula(household, period, parameters):
            return parameters(period).gov.contrib.states.tx.rebate.amount

    def modify_parameters(parameters):
        state_benefits = parameters.gov.household.household_state_benefits
        current_benefits = state_benefits(instant("2027-01-01"))
        if "tx_rebate" not in current_benefits:
            new_benefits = list(current_benefits) + ["tx_rebate"]
            state_benefits.update(
                start=instant("2027-01-01"),
                stop=instant("2027-12-31"),
                value=new_benefits,
            )
        # SPM resources count the rebate as a benefit. It is zero outside
        # 2027, so the list carries it in every year.
        add_to_list_parameter(parameters.gov.household.spm_unit_benefits, ["tx_rebate"])
        return parameters

    class reform(Reform):
        def apply(self):
            self.update_variable(tx_rebate)
            self.modify_parameters(modify_parameters)

    return reform


def create_tx_rebate_reform(parameters, period, bypass: bool = False):
    if bypass:
        return create_tx_rebate()

    p = parameters.gov.contrib.states.tx.rebate

    reform_active = False
    current_period = period_(period)

    for i in range(5):
        if p(current_period).in_effect:
            reform_active = True
            break
        current_period = current_period.offset(1, "year")

    if reform_active:
        return create_tx_rebate()
    else:
        return None


tx_rebate = create_tx_rebate_reform(None, None, bypass=True)
