from policyengine_us.model_api import *


class vt_elderly_or_disabled_credit_exclusion_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for Vermont elderly or disabled credit"
    definition_period = YEAR
    defined_for = StateCode.VT

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.vt.tax.income.agi.exclusions.elderly_or_disabled.eligibility

        # filing status
        filing_status = tax_unit("filing_status", period)

        person = tax_unit.members
        qualifies_for_elderly_or_disabled_credit = person(
            "qualifies_for_elderly_or_disabled_credit", period
        )
        num_qualifying_individuals = tax_unit.sum(
            qualifies_for_elderly_or_disabled_credit
        )

        # agi eligibility
        agi_limit = select(
            [
                filing_status
                == filing_status.possible_values.JOINT
                & num_qualifying_individuals
                == 1,
                filing_status
                == filing_status.possible_values.JOINT
                & num_qualifying_individuals
                == 2,
                filing_status == filing_status.possible_values.SEPARATE,
                filing_status == filing_status.possible_values.SINGLE,
                True,
            ],
            [
                p.agi_limit.joint_one_qualified,
                p.agi_limit.joint_two_qualified,
                p.agi_limit.separate,
                p.agi_limit.single,
                0,
            ],
        )
        agi_eligible = tax_unit("vt_agi", period) < agi_limit

        # the total of your nontaxable social security and other nontaxable pension(s), annuities, or disability income eligibility
        # 1. nontaxable social security
        total_social_security = tax_unit("tax_unit_social_security", period)
        taxable_social_security = tax_unit(
            "tax_unit_taxable_social_security", period
        )
        non_taxable_social_security = (
            total_social_security - taxable_social_security
        )
        # 2. nontaxable pension(s) and annuities
        total_pensions_and_annuities = add(
            tax_unit, period, ["pension_income"]
        )
        taxable_pensions_and_annuities = add(
            tax_unit, period, ["taxable_pension_income"]
        )
        non_taxable_pensions_and_annuities = (
            total_pensions_and_annuities - taxable_pensions_and_annuities
        )
        # 3. disability income
        disability_income = add(
            tax_unit, period, ["total_disability_payments"]
        )

        total_income = (
            non_taxable_social_security
            + non_taxable_pensions_and_annuities
            + disability_income
        )

        income_limit = select(
            [
                filing_status
                == filing_status.possible_values.JOINT
                & num_qualifying_individuals
                == 1,
                filing_status
                == filing_status.possible_values.JOINT
                & num_qualifying_individuals
                == 2,
                filing_status == filing_status.possible_values.SEPARATE,
                filing_status == filing_status.possible_values.SINGLE,
                True,
            ],
            [
                p.income_limit.joint_one_qualified,
                p.income_limit.joint_two_qualified,
                p.income_limit.separate,
                p.income_limit.single,
                0,
            ],
        )
        nontaxable_income_eligible = total_income < income_limit

        return (
            (num_qualifying_individuals > 0)
            & agi_eligible
            & nontaxable_income_eligible
        )
