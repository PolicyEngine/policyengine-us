from policyengine_us.model_api import *


class nm_child_income_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico child income tax credit"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503818/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcHYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        income = tax_unit("nm_agi", period)
        children = tax_unit("tax_unit_children", period)
        p = parameters(period).gov.states.nm.tax.income.credits.child_income
        amount = p.amount.calc(income) * children
        # Halve the credit if married filing separately.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        return amount / denominator
