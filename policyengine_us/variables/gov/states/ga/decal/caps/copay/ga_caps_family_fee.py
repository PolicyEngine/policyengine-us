from policyengine_us.model_api import *


class ga_caps_family_fee(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Georgia CAPS family fee (co-payment)"
    definition_period = MONTH
    defined_for = StateCode.GA
    reference = (
        "https://caps.decal.ga.gov/assets/downloads/CAPS/AppendixD-Family%20Fee%20Assessment%20Chart.pdf",
        "https://caps.decal.ga.gov/assets/downloads/CAPS/0-CAPS_Policy-Manual.pdf#page=55",
        "https://www.decal.ga.gov/documents/attachments/CCDFStatePlan25-27.pdf#page=49",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ga.decal.caps.family_fee
        # Minor parent fee waiver: parents age <= 17 have no fee.
        person = spm_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period.this_year)
        age = person("age", period.this_year)
        has_minor_parent = spm_unit.any(is_head_or_spouse & (age <= p.minor_parent_age))
        # DFCS custody fee waiver: any child in DFCS custody waives the fee.
        has_dfcs_custody_child = add(spm_unit, period, ["is_in_foster_care"]) > 0
        fee_waived = has_minor_parent | has_dfcs_custody_child
        # Compute fee from FPL-ratio scale bracket.
        countable_income = spm_unit("ga_caps_countable_income", period)
        fpg = spm_unit("spm_unit_fpg", period)
        mask = fpg > 0
        fpl_ratio = np.divide(
            countable_income,
            fpg,
            out=np.zeros_like(countable_income),
            where=mask,
        )
        fee_rate = p.rate.calc(fpl_ratio)
        # Weekly fee = floor(annual income * rate / 52), then convert to monthly.
        annual_income = countable_income * MONTHS_IN_YEAR
        weekly_fee = np.floor(annual_income * fee_rate / WEEKS_IN_YEAR)
        monthly_fee = weekly_fee * (WEEKS_IN_YEAR / MONTHS_IN_YEAR)
        return where(fee_waived, 0, monthly_fee)
