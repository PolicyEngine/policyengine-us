from policyengine_us.model_api import *


class nm_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico child income tax credit"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503818/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcHYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        agi = tax_unit("adjusted_gross_income", period)
        # The law 7-2-18.34(J)(2) defines qualifying children as those from IRC 152(c).
        # IRC 152(c) refers to the EITC qualifying children.
        # https://www.law.cornell.edu/uscode/text/26/152#c
        children = tax_unit("eitc_child_count", period)
        p = parameters(period).gov.states.nm.tax.income.credits.ctc
        amount_per_child = p.amount.calc(agi)
        amount = amount_per_child * children
        # Halve the credit if married filing separately.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        denominator = where(separate, 2, 1)
        return amount / denominator
