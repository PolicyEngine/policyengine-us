from policyengine_us.model_api import *


class vt_ctc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Vermont child tax credit"
    definition_period = YEAR
    unit = USD
    reference = "https://casetext.com/statute/vermont-statutes/title-32-taxation-and-finance/chapter-151-income-taxes/subchapter-002-taxation-of-individuals-trusts-and-estates/section-5830f-see-note-vermont-child-tax-credit/1"
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        # Get age status of all people in the tax unit.
        person = tax_unit.members
        age = person("age", period)
        p = parameters(period).gov.states.vt.tax.income.credits.ctc
        eligible = age <= p.age_limit
        count_eligible = tax_unit.sum(eligible)
        # Get maximum credit amount.
        max_credit = p.amount * count_eligible
        # Get adjusted gross income.
        agi = tax_unit("adjusted_gross_income", period)
        # Reduce credit amount over the phaseout range.
        excess_agi = max_(agi - p.reduction.start, 0)
        increments = np.ceil(excess_agi / p.reduction.increment)
        total_reduction = p.reduction.amount * increments
        # Return reduced credit amount.
        return max_(max_credit - total_reduction, 0)
