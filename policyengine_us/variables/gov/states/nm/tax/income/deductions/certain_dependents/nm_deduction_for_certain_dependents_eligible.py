from policyengine_us.model_api import *


class nm_deduction_for_certain_dependents_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligibility for New Mexico deduction for certain dependents"
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503892/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgAcATgBMASgA0ybKUIQAiokK4AntADkW6REJhcCFWs069BoyADKeUgCFNAJQCiAGRcA1AIIA5AMIu0qRgAEbQpOySkkA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        dependent_on_another_return = tax_unit("dsi", period)
        # The deduction does not apply if an exemption under IRS 151 is claimed
        # IRC 151 refers to the personal exemption.
        federal_exemption_amount = tax_unit("c04600", period)
        return ~dependent_on_another_return & (federal_exemption_amount == 0)
