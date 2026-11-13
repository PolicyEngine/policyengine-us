from policyengine_us.model_api import *


class market_income(Variable):
    value_type = float
    entity = Person
    label = "Market income"
    unit = USD
    documentation = (
        "Income from all non-government sources. SPM resources add it, so it "
        "counts every cash source of federal gross income that "
        "spm_unit_benefits does not, with its losses where it has them."
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        COMPONENTS = [
            "employment_income",
            "self_employment_income",
            "sstb_self_employment_income",
            # Schedule E partnership and S corporation income.
            "partnership_s_corp_income",
            "pension_income",
            "dividend_income",
            "interest_income",
            "gi_cash_assistance",
            "capital_gains",
            # Capital gain distributions reported without Schedule D.
            "non_sch_d_capital_gains",
            # Form 4797 other gains and losses.
            "other_net_gain_person",
            "rental_income",
            # Farm rental income (Form 4835).
            "farm_rent_income",
            "estate_income",
            "illicit_income",
            "farm_operations_income",
            "miscellaneous_income",
            "alimony_income",
            "strike_benefits",
            "retirement_distributions",
            "military_retirement_income",
            # Disability benefits from an employer plan, taxable or not.
            "disability_benefits",
            "ak_permanent_fund_dividend",
        ]
        return add(person, period, COMPONENTS)
