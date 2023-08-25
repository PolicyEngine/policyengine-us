from policyengine_us.model_api import *


class nm_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child income tax credit"
    definition_period = YEAR
    unit = USD
    reference = "https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5830f-see-note-vermont-child-tax-credit/1"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # Get age status of all people in the tax unit.
        person = tax_unit.members
        age = person("age", period)
        p = parameters(period).gov.states["vt"].tax.income.credits.ctc
        eligible = age < p.ineligible_age
        count_eligible = tax_unit.sum(eligible)
        # Get maximum credit amount.
        max_credit = p.amount * count_eligible
        # Get Vermont adjusted gross income.
        vt_agi = tax_unit("vt_income_after_subtractions", period)
        # Reduce credit amount over the phaseout range.
        excess_agi = max_(vt_agi - p.reduction.start, 0)
        increments = np.ceil(excess_agi / p.reduction.amount)
        percent_reduction = p.reduction.increment * increments
        # Return reduced amount.
        return max_(max_credit - percent_reduction, 0)