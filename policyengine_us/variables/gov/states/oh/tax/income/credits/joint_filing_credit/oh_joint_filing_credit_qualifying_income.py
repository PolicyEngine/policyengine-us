from policyengine_us.model_api import *


class oh_joint_filing_credit_qualifying_income(Variable):
    value_type = float
    entity = Person
    label = "Ohio qualifying income for the joint filing credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.055",
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20",
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        agi = person("oh_agi_person", period)
        # Interest, dividends, capital gains and rents are excluded only to
        # the extent included in Ohio AGI (R.C. 5747.05(E)(1)). A qualifying
        # capital gain deducted under R.C. 5747.01(A)(34) is already out of
        # Ohio AGI, so it is not excluded again.
        # Capped at the capital gains reported, so a directly set multi-entity
        # deduction cannot cancel the other exclusions.
        deducted_gain = min_(
            person("oh_qualifying_capital_gain_deduction", period),
            max_(person("capital_gains", period), 0),
        )
        excluded = person("oh_joint_filing_credit_agi_subtractions", period)
        # Prevent negative subtractions from acting as additions
        subtractions = max_(0, excluded - deducted_gain)
        return agi - subtractions
