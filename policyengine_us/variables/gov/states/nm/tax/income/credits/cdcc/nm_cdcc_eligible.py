from policyengine_us.model_api import *


class nm_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible household for the New Mexico dependent child day care credit"
    )
    defined_for = StateCode.NM
    unit = USD
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Filer can not be a dependent on another tax return
        dependent_on_another_return = tax_unit("dsi", period)
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        # Filer has to be be gainfully employed to receive credit
        # unless one person is disabled
        employed = tax_unit("tax_unit_earned_income", period) > 0
        disabled = person("is_disabled", period)
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        disabled_eligible = (head | spouse) & tax_unit.any(disabled)
        emloyment_eligible = employed | disabled_eligible
        # Filer can not receive tanf to be eligible
        receives_tanf = tax_unit.spm_unit("tanf", period) > 0
        # Filers have to have modified gross of income below annual earning
        # at double the federal minimum wage
        nm_modified_gross_income = tax_unit("nm_modified_gross_income", period)
        minimum_wage = parameters(period).gov.dol.minimum_wage
        income_limit = (
            minimum_wage
            * p.wage_multiplicator
            * WEEKS_IN_YEAR
            * p.full_time_hours
        )
        agi_eligible = nm_modified_gross_income <= income_limit
        return (
            emloyment_eligible
            & ~receives_tanf
            & agi_eligible
            & ~dependent_on_another_return
        )
