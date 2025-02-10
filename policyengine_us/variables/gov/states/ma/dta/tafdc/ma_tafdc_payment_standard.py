from policyengine_us.model_api import *


class ma_tafdc_payment_standard(Variable):
    value_type = float
    unit = USD
    entity = TaxUnit
    label = "Massachusetts Temporary Assistance for Families with Dependent Children (TAFDC) payment standard"
    definition_period = MONTH
    reference = "https://www.masslegalservices.org/content/75-how-much-will-you-get-each-month"
    defined_for = StateCode.MA

    def formula(tax_unit, period, parameters):
        in_public_housing = tax_unit.household("is_in_public_housing", period)
        p = parameters(period).gov.states.ma.dta.tafdc.eligibility.income_limit
        teen_parent_present = tax_unit.any(
            tax_unit.members("is_teen_parent", period)
        )
        capped_unit_size = min_(
            tax_unit("tax_unit_size", period), p.max_unit_size
        )
        # Calculate the base income limit for non-teen parents
        ps_non_teen_parent = where(
            in_public_housing,
            p.base.public_housing.calc(capped_unit_size),
            p.base.private_housing.calc(capped_unit_size),
        )
        additional_person_ps = p.additional_person * (
            capped_unit_size - p.max_unit_size
        )
        total_base_ps = ps_non_teen_parent + additional_person_ps
        # Calculate the base income limit for teen parents
        ps_teen_parent = where(
            in_public_housing,
            p.teen_parent.public_housing.calc(capped_unit_size),
            p.teen_parent.private_housing.calc(capped_unit_size)
            + additional_person_limit,
        )
        additional_person_teen_ps = p.teen_parent.additional_person * (
            capped_unit_size - p.max_unit_size
        )
        total_teen_parent_ps = ps_teen_parent + additional_person_teen_ps
        # Select the appropriate income limit based on whether there is a teen parent
        return where(teen_parent_present, total_teen_parent_ps, total_base_ps)
