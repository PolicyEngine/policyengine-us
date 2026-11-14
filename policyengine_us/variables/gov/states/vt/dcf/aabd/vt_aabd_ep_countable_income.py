from policyengine_us.model_api import *
from policyengine_us.variables.gov.ssa.ssi.eligibility.resources.deemed._ssi_spouses import (
    _ssi_couple_total,
    _ssi_spouse_index,
)


class vt_aabd_ep_countable_income(Variable):
    value_type = float
    entity = Person
    label = "Vermont Essential Person assistance-group countable income"
    definition_period = MONTH
    unit = USD
    reference = (
        # PDF pages 42, 48-51
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2700-AABD.pdf#page=42",
        "https://outside.vermont.gov/dept/DCF/Shared%20Documents/ESD/Rules/2200-Reach-Up.pdf#page=70",
    )
    documentation = """
    Income of the marital unit's household members under rule 2786, with
    earnings counted before payroll deductions (Reach Up rule 2251(a)), plus
    vt_aabd_ep_additional_countable_income.
    NOTE: Reach Up income sources or exclusions without an SSI input are not
    modeled.
    """

    def formula(person, period, parameters):
        p = parameters(period).gov.states.vt.dcf.aabd.ep
        ssi_income = parameters(period).gov.ssa.ssi.income
        exclusions = ssi_income.exclusions
        abd = person("is_ssi_aged_blind_disabled", period.this_year)
        arrangement = person("vt_aabd_living_arrangement", period)
        la = arrangement.possible_values
        # Rule 2782: the group includes only members living in the same
        # household, so a spouse in a facility is left out.
        in_household = (arrangement == la.INDEPENDENT) | (
            arrangement == la.HOUSEHOLD_OF_ANOTHER
        )
        # Rule 2786 applies the Reach Up income rules, and Reach Up rule
        # 2251(a) counts earnings "prior to any voluntary or involuntary
        # deductions including ... insurance".
        # NOTE: SSI excludes salary-reduction health premiums from wages (POMS
        # SI 00820.102 C.2), so this sums SSI's earned sources rather than
        # reading ssi_earned_income; the ssi term below keeps SSA's treatment.
        gross_earned = add(person, period, ssi_income.sources.earned)
        earned = in_household * max_(gross_earned - p.employment_expense, 0)
        abd_earned = _ssi_couple_total(person, period.this_year, earned * abd)
        other_earned = _ssi_couple_total(person, period.this_year, earned * ~abd)
        # NOTE: Rule 2786 withholds the $20 exclusion from VA pension only; with
        # no pension-specific input, all veterans benefits are treated as pension.
        veterans = max_(person("veterans_benefits", period), 0)
        unearned = _ssi_couple_total(
            person,
            period.this_year,
            in_household * max_(person("ssi_unearned_income", period) - veterans, 0),
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
        needs_based = _ssi_couple_total(
            person,
            period.this_year,
            in_household
            * (veterans + person("ssi", period) + person("vt_aabd_federal", period)),
        )
        additional_income = max_(
            person("vt_aabd_ep_additional_countable_income", period), 0
        )
        spouse_index = _ssi_spouse_index(person, period.this_year)
        additional = max_(
            additional_income,
            where(spouse_index >= 0, additional_income[np.maximum(spouse_index, 0)], 0),
        )
        return unearned + abd_earned + other_earned + needs_based + additional
