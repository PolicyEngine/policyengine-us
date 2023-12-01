from policyengine_us.model_api import *


class nm_cdcc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = (
        "Eligible household for the New Mexico dependent child day care credit"
    )
    definition_period = YEAR
    reference = "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503752/BQCwhgziBcwMYgK4DsDWszIQewE4BUBTADwBdoAvbRABwEtsBaAfX2zgEYAWABgFYeAZgDsfAEwBKADTJspQhACKiQrgCe0AOSapEQmFwJlqjdt37DIAMp5SAIQ0AlAKIAZZwDUAggDkAws5SpGAARtCk7BISQA"
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Filer can not be a dependent on another tax return
        dependent_elsewhere = tax_unit("head_is_dependent_elsewhere", period)
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        # Filer has to be be gainfully employed to receive credit
        has_earnings = person("earned_income", period) > 0
        # If a joint return is filed, both spouses must be gainfully employed
        # unless one person is disabled
        filing_status = tax_unit("filing_status", period)
        joint = filing_status == filing_status.possible_values.JOINT
        head = person("is_tax_unit_head", period)
        spouse = person("is_tax_unit_spouse", period)
        head_has_earnings = tax_unit.any(head & has_earnings)
        spouse_has_earnings = tax_unit.any(spouse & has_earnings)
        both_have_earnings = head_has_earnings & spouse_has_earnings
        disabled = person("is_disabled", period)
        disabled_eligible = tax_unit.any((head | spouse) & disabled)
        joint_eligible = both_have_earnings | disabled_eligible
        employment_eligible = where(joint, joint_eligible, head_has_earnings)
        # Filer can not receive tanf to be eligible
        receives_tanf = tax_unit.spm_unit("tanf", period) > 0
        # Filers have to have modified gross income at or below a limit
        nm_modified_gross_income = tax_unit("nm_modified_gross_income", period)
        income_limit = (
            parameters(period).gov.dol.minimum_wage
            * p.income_limit_as_fraction_of_minimum_wage
            * WEEKS_IN_YEAR
            * p.full_time_hours
        )
        income_eligible = nm_modified_gross_income <= income_limit
        return (
            ~dependent_elsewhere
            & employment_eligible
            & ~receives_tanf
            & income_eligible
        )
