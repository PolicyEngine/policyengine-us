from policyengine_us.model_api import *


class vt_aabd_ep_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Vermont Essential Person assistance-group countable income"
    definition_period = MONTH
    unit = USD
    reference = "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf"
    documentation = "Whole marital-group income plus the verified net allocation for nonspouse essential persons/parents. Override for Reach Up income sources/exclusions absent from SSI inputs or an agency allocation of the shared general disregard."

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.aabd.ep
        exclusions = parameters(period).gov.ssa.ssi.income.exclusions
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        earned = max_(person("ssi_earned_income", period) - p.employment_expense, 0)
        abd_earned = person.marital_unit.sum(earned * abd)
        other_earned = person.marital_unit.sum(earned * ~abd)
        veterans = max_(person("veterans_benefits", period), 0)
        unearned = person.marital_unit.sum(
            max_(person("ssi_unearned_income", period) - veterans, 0)
        )
        general = exclusions.general
        remaining_general = max_(general - unearned, 0)
        unearned = max_(unearned - general, 0)
        # Apply any remaining group disregard to non-ABD earnings first,
        # since only the ABD members receive the half-earnings exclusion.
        remaining_general_abd = max_(remaining_general - other_earned, 0)
        other_earned = max_(other_earned - remaining_general, 0)
        abd_earned = max_(abd_earned - remaining_general_abd - exclusions.earned, 0) * (
            1 - exclusions.earned_share
        )
        needs_based = person.marital_unit.sum(
            veterans + person("ssi", period) + person("vt_aabd_federal", period)
        )
        additional = person.marital_unit.max(
            max_(person("vt_aabd_ep_additional_countable_income", period), 0)
        )
        return unearned + abd_earned + other_earned + needs_based + additional
