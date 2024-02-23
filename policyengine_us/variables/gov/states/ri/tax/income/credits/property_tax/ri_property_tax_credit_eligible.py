from policyengine_us.model_api import *


class ri_property_tax_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Rhode Island property tax credit eligibility status"
    definition_period = YEAR
    reference = (
        "http://webserver.rilin.state.ri.us/Statutes/TITLE44/44-33/44-33-3.htm",  # (1) & (2) determines age and disability eligibility
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-01/2021-ri-1040h_w.pdf#page=1",
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.credits.property_tax
        # minimum age eligibility
        greater_head_or_spouse_age = tax_unit(
            "greater_age_head_spouse", period
        )
        age_eligible = greater_head_or_spouse_age >= p.age_threshold
        # disability eligibility
        head_is_disabled = tax_unit("head_is_disabled", period)
        spouse_is_disabled = tax_unit("spouse_is_disabled", period)
        head_or_spouse_disabled = head_is_disabled | spouse_is_disabled
        household_income = tax_unit("ri_property_tax_household_income", period)
        income_threshold = p.rate.one_person.thresholds[-1]
        # The tax form RI-1040H specifies the income of a household as a eligibility requirement
        household_income_eligible = household_income <= income_threshold
        return (
            age_eligible | head_or_spouse_disabled
        ) & household_income_eligible
