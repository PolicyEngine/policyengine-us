from policyengine_us.model_api import *


class nm_hundred_year_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico hundred year exemption"
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503677/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgBsAdlEBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        p = parameters(period).gov.states.nm.tax.income.exemptions.hundred_year
        head_eligible = age_head >= p.age_eligibility
        spouse_eligible = age_spouse >= p.age_eligibility
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        # Halve the exemption if only one of head and spouse is eligible of a joint filer.
        denominator = where(joint, 2, 1)
        numerator = head_eligible.astype(int) + spouse_eligible.astype(int)
        # Exempt AGI apportioned among eligible spouses.
        # That is, assume all income is community property.
        return tax_unit("nm_agi", period) * numerator / denominator
