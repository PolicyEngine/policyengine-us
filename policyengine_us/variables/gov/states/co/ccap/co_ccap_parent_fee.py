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
        person = tax_unit.members
        # Identify whether the filers are during the entry or re-determination process.
        is_entry = tax_unit("co_ccap_is_entry", period)
        entry_eligible = tax_unit("co_ccap_entry_eligible", period)
        is_re_determination = tax_unit("co_ccap_is_re_determination", period)
        re_determination_eligible = tax_unit(
            "co_ccap_re_determination_eligible", period
        )

        if (is_entry * entry_eligible) | (
            is_re_determination * re_determination_eligible
        ):
            # Calculate base parent fee and add on parent fee.
            agi = tax_unit("adjusted_gross_income", period)
            hhs_fpg = tax_unit("tax_unit_fpg", period)
            num_child_age_eligible = tax_unit(
                "co_ccap_num_child_age_eligible", period
            )

            # The numebrs below are weights copied from government spreadsheet (url: )
            base_parent_fee = where(
                agi <= hhs_fpg,
                agi * 0.01 / 12,
                (hhs_fpg * 0.01 + (agi - hhs_fpg) * 0.14) / 12,
            )
            add_on_parent_fee = where(
                agi > hhs_fpg, (num_child_age_eligible - 1) * 15, 0
            )

            # Sum up all the parent fee for eligible children.
            child_age_eligible = person("co_ccap_child_age_eligible", period)
            childcare_hours_per_day = person("childcare_hours_per_day", period)
            rate = p.parent_fee_rate_by_child_care_hours.calc(
                childcare_hours_per_day, right=True
            )
            non_discouted_fee = tax_unit.sum(
                child_age_eligible
                * (base_parent_fee + add_on_parent_fee)
                * rate
            )

            # Identify whether the filers are eligible for a discount.
            rating = person("co_quality_rating_of_child_care_facility", period)
            discount_eligible = (
                tax_unit.sum(p.is_quality_rating_discounted.calc(rating)) > 0
            )

            discounted_rate = p.quality_discounted_rate

            return np.round(
                where(
                    discount_eligible,
                    non_discouted_fee * discounted_rate,
                    non_discouted_fee,
                ),
                2,
            )
