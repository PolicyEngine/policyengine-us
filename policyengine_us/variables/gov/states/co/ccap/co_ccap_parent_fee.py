from policyengine_us.model_api import *


class co_ccap_parent_fee(Variable):
    value_type = float
    entity = TaxUnit 
    label = "Colorado child care assistance program eligible"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.CO    
    
    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.co.ccap
        p_fpg = parameters(period).gov.hhs.fpg
        person = tax_unit.members
        agi = tax_unit("adjusted_gross_income", period)

        size = tax_unit("tax_unit_size", period)
        hhs_fpg = p_fpg.first_person.CONTIGUOUS_US + (size-1) * p_fpg.additional_person.CONTIGUOUS_US

        
        # child_age_eligible = person("co_ccap_child_age_eligible", period)
        
        childcare_hours_per_week = tax_unit.sum(person("childcare_days_per_week", period))
        
        num_child_age_eligible = tax_unit("co_ccap_num_child_age_eligible", period)
        
        base_parent_fee = where(agi <= hhs_fpg, agi*0.01/12, (hhs_fpg*0.01 + (agi-hhs_fpg)*0.14) / 12)
        add_on_parent_fee = where(agi > hhs_fpg, (num_child_age_eligible-1)*15, 0)

        is_quality_discounted = tax_unit("co_is_quality_rating_of_child_care_facility", period)

        full_time_parent_fee = base_parent_fee + add_on_parent_fee
# ? all children care time total > 40 to be full time? Or whethere full time or not is calculated by each child.



        # full_time_discounted_parent_fee = full_time_parent_fee * 0.8 # quality rating discounted rate - parameter;

        # part_time_parent_fee = full_time_parent_fee * 0.55
        # part_time_discounted_parent_fee = part_time_parent_fee * 0.8

        is_full_time = childcare_hours_per_week >= 40 # child_care_hours - parameters

        parent_fee = where(is_full_time, full_time_parent_fee , full_time_parent_fee * 0.55) * where(is_quality_discounted, 0.8, 1)

        # what if one child qualify discounted another not