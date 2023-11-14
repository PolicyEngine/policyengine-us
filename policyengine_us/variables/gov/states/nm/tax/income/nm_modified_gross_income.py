from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsfYQEoANMmylCEAIqJCuAJ7QA5BskRCYXAiUr1WnXoMgAynlIAhdQCUAogBknANQCCAOQDCTyVIwACNoUnZxcSA"  # L
    defined_for = StateCode.NM

    adds = "gov.states.nm.tax.income.modified_gross_income"
