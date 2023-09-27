from policyengine_us.model_api import *


class nm_deduction_for_certain_dependents(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico deduction for certain dependents"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503892/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcATgBMASgA0ybKUIQAiokK4AntADkW6REJhcCFWs069BoyADKeUgCFNAJQCiAGRcA1AIIA5AMIu0qRgAEbQpOySkkA"
    defined_for = "nm_deduction_for_certain_dependents_eligible"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(
            period
        ).gov.states.nm.tax.income.deductions.certain_dependents
        # The law 7-2-39(D) defines dependents as those from IRC 152.
        # IRC 152 refers to all dependents.
        # https://www.law.cornell.edu/uscode/text/26/152
        dependents = tax_unit("tax_unit_dependents", period)
        # New Mexico reduces the number of claimable dependents by one.
        countable_dependents = max_(dependents - 1, 0)
        amount_per_dependent = p.amount[filing_status]
        return amount_per_dependent * countable_dependents
