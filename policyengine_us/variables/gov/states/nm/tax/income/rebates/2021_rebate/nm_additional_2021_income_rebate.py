from policyengine_us.model_api import *


class nm_additional_2021_income_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico additional 2021 income tax rebate"
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503710/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsHHgEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA",
        # PDF pages 2-3
        "https://realfile.tax.newmexico.gov/2021pit-rc-ins.pdf#page=2",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # The rebate and credit schedule bars a filer who is a dependent of
        # another taxpayer, but "If you are a dependent with a spouse who was
        # not a dependent of another taxpayer, your spouse may still qualify
        # to claim rebates or credits" (PIT-RC instructions). So only a return
        # on which every filer is a dependent elsewhere is barred.
        every_filer_dependent = tax_unit("every_filer_is_dependent_elsewhere", period)
        p = parameters(period).gov.states.nm.tax.income.rebates["2021_income"]
        filing_status = tax_unit("filing_status", period)
        return ~every_filer_dependent * p.additional.amount[filing_status]
