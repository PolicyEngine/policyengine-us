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
        # The law 7-2-18.34(J)(2) defines qualifying children as those from IRC 152(c).
        # IRC 152(c) refers to the EITC qualifying children.
        # https://www.law.cornell.edu/uscode/text/26/152#c
        children = tax_unit("eitc_child_count", period)
        # New Mexico reduces the number of claimable dependents by one.
        eligible_children = max_(children - 1, 0)
        amount_per_child = p.amount[filing_status]
        return amount_per_child * eligible_children
