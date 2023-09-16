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

        size = tax_unit("tax_unit_size", period)
        hhs_fpg = p_fpg.first_person.CONTIGUOUS_US + (size-1) * p_fpg.additional_person.CONTIGUOUS_US


        base_parent_fee = where(agi <= hhs_fpg, agi*0.01/12, (hhs_fpg*0.01 + (agi-hhs_fpg)*0.14) / 12)
        
        disabled = person("is_disabled", period)
        dependent = person("is_tax_unit_dependent", period)
        age = person("age", period)
        child_age_eligible = where(disabled, (age < p.disabled_child_age_limit) & dependent, (age < p.age_limit) & dependent)
        num_children = tax_unit.sum(child_age_eligible) 
        
        add_on_parent_fee = where(agi > hhs_fpg, (num_children-1)*15, 0)

        quality_discounted = tax_unit("co_is_quality_rating_of_child_care_facility", period)

        full_time_parent_fee = base_parent_fee + add_on_parent_fee  
        # full_time_discounted_parent_fee = full_time_parent_fee * 0.8 # quality rating discounted rate - parameter;

        # part_time_parent_fee = full_time_parent_fee * 0.55
        # part_time_discounted_parent_fee = part_time_parent_fee * 0.8

        # childcare_hours_per_week = person("childcare_days_per_week", period)
        full_time = childcare_hours_per_week >= 40 # child_care_hours - parameters

        parent_fee = where(full_time, full_time_parent_fee , full_time_parent_fee * 0.55) * where(quality_discounted, 0.8, 1)

        # what if one child qualify discounted another not