from policyengine_us.model_api import *
from policyengine_us.tools.period_branch import has_input
from policyengine_us.tools.state_itemization import (
    SALT_ELECTION_STATES,
    SALT_ELECTION_WHEN_STATE_ITEMIZED,
    joint_federal_itemizes,
    joint_itemization_is_enabled,
    joint_uses_alternative,
)
from policyengine_us.variables.gov.states.tax.income.state_deduction_method import (
    StateDeductionMethod,
)


class state_and_local_sales_tax_elected(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Elect state and local general sales taxes on federal Schedule A"
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/26/164#b_5"

    def formula(tax_unit, period, parameters):
        # A filer who supplies only a combined total can also supply the election.
        if has_input(
            tax_unit.simulation, "state_and_local_sales_or_income_tax", period
        ):
            return False
        income_tax = add(
            tax_unit, period, ["state_withheld_income_tax", "local_income_tax"]
        )
        sales_tax = add(tax_unit, period, ["state_sales_tax", "local_sales_tax"])
        default = sales_tax > income_tax
        if joint_itemization_is_enabled(period, parameters):
            state = tax_unit.household("state_code_str", period)
            compares_sales = np.isin(state, SALT_ELECTION_STATES)
            if compares_sales.any():
                choices = tax_unit("tax_unit_joint_itemization", period)
                optional_itemizers = np.isin(state, SALT_ELECTION_WHEN_STATE_ITEMIZED)
                uses_standard = (
                    choices % len(StateDeductionMethod)
                    == StateDeductionMethod.STANDARD.index
                )
                return where(
                    compares_sales
                    & joint_federal_itemizes(choices)
                    & ~(optional_itemizers & uses_standard),
                    joint_uses_alternative(choices),
                    default,
                )
        return default
