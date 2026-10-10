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
        person = tax_unit.members
        # R.I. Gen. Laws 44-33-3: the claimant is a homeowner or renter aged
        # 65 or older or disabled, and "does not include any person claimed as
        # a dependent by any taxpayer". Members of a household choose who
        # claims, so either spouse may be the claimant, but the age or
        # disability and the dependency test belong to the same person.
        filer = person("is_tax_unit_head_or_spouse", period)
        age_eligible = person("age", period) >= p.age_threshold
        disabled = person("is_disabled", period)
        claimed = person("claimed_as_dependent_on_another_return", period)
        eligible_claimant = filer & (age_eligible | disabled) & ~claimed
        household_income = tax_unit("ri_property_tax_household_income", period)
        income_threshold = p.rate.one_person.thresholds[-1]
        # The tax form RI-1040H specifies the income of a household as a eligibility requirement
        household_income_eligible = household_income <= income_threshold
        return tax_unit.any(eligible_claimant) & household_income_eligible
