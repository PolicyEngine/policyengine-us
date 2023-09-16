from policyengine_us.model_api import *


class co_ccap_entry_eligible(Variable):
    value_type = str
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.cccap
        p_fpg = parameters(period).gov.hhs.fpg
        p_smi = parameters(period).gov.hhs.smi
        person = tax_unit.members
        agi = tax_unit("adjusted_gross_income", period)
        
        # Calculate monthly fpg limit
        county = tax_unit.household("county_str", period)
        hhs_fpg_rate = p.entry_threshold[county]
        size = tax_unit("tax_unit_size", period)
        hhs_fpg = p_fpg.first_person.CONTIGUOUS_US + (size-1) * p_fpg.additional_person.CONTIGUOUS_US
        monthly_hhs_fpg =  np.round(hhs_fpg * hhs_fpg_rate / 12, 2)
        
        # Calculate monthly smi limit
        # hhs_smi_rate = p.initial_income_eligibility
        # four_person_smi = p_smi.amount.CO
        # adjustment_mapping = p_smi.household_size_adjustment
        # first_person_rate = adjustment_mapping.first_person
        # second_to_sixth_additional_rate = (
        #     adjustment_mapping.second_to_sixth_person
        # )
        # seven_or_more_additional_rate = adjustment_mapping.additional_person
        # size_adjustment = (
        #     first_person_rate
        #     + second_to_sixth_additional_rate * (min_(size, 6) - 1)
        #     + seven_or_more_additional_rate * max_(size - 6, 0)
        # )
        # hhs_smi = four_person_smi * size_adjustment
        spm_unit = tax_unit.spm_unit
        hhs_smi = spm_unit("hhs_smi", period)
        monthly_hhs_smi = np.round(hhs_smi * hhs_smi_rate / 12, 2)

        income_eligible = (agi < monthly_hhs_fpg) & (agi < monthly_hhs_smi)

        # Identify child(ren) eligibility.
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child_age_eligible = where(disabled, (age < p.disabled_child_age_limit) & dependent, (age < p.age_limit) & dependent)
        
        return tax_unit.sum(income_eligible & child_age_eligible)