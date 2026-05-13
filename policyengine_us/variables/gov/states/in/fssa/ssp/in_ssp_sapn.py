from policyengine_us.model_api import *


class in_ssp_sapn(Variable):
    value_type = float
    entity = Person
    label = "Indiana Supplemental Assistance for Personal Needs"
    unit = USD
    definition_period = MONTH
    defined_for = "in_ssp_sapn_eligible"
    reference = (
        "https://www.in.gov/fssa/ompp/files/Medicaid_PM_5000.pdf",
        "https://secure.ssa.gov/poms.nsf/lnx/0501401001CHI",
    )

    def formula(person, period, parameters):
        # Medicaid PM 5000 § 5005.05.00: SAPN = PNA minus budgeted
        # income (IC 12-15-32-6.5, 405 IAC 7-1-1(c)).
        # Uses actual SSI payment + SSI countable income as proxy for
        # Medicaid post-eligibility budgeted income.
        p = parameters(period).gov.states["in"].fssa.ssp
        joint_claim = person("ssi_claim_is_joint", period.this_year)
        eligible = person("in_ssp_sapn_eligible", period)
        both_eligible = person.marital_unit.sum(eligible) == 2
        is_couple = joint_claim & both_eligible
        ssi_monthly = person("ssi", period)
        countable_income = person("ssi_countable_income", period)
        max_individual = p.sapn.amount.individual
        max_couple = p.sapn.amount.couple
        pna = p.personal_needs_allowance

        individual_amount = max_(
            min_(pna - ssi_monthly - countable_income, max_individual),
            0,
        )
        couple_budgeted = person.marital_unit.sum(ssi_monthly + countable_income)
        couple_amount = max_(
            min_(2 * pna - couple_budgeted, max_couple),
            0,
        )
        return where(is_couple, couple_amount / 2, individual_amount)
