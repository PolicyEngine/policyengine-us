from policyengine_us.model_api import *


class monthly_selected_marketplace_plan_premium_proxy(Variable):
    value_type = float
    entity = TaxUnit
    label = "Monthly selected Marketplace plan premium proxy"
    unit = USD
    definition_period = MONTH
    documentation = (
        "The selected plan premium for one month, using that month's bronze "
        "or silver price. Plan selection, take-up and enrollment remain annual "
        "inputs. The annual selected_marketplace_plan_premium_proxy sums these "
        "amounts and continues to accept supplied annual premiums."
    )

    def formula(tax_unit, period, parameters):
        year = period.this_year
        takes_up_aca_if_eligible = tax_unit("takes_up_aca_if_eligible", year)
        person = tax_unit.members
        pays_marketplace_premium = tax_unit.any(person("pays_aca_premium", year))
        category = tax_unit("selected_marketplace_plan_category", year)
        silver_premium = tax_unit("slcsp", period) * tax_unit(
            "selected_marketplace_plan_benchmark_ratio", year
        )
        selected_plan_premium = where(
            category == category.possible_values.BRONZE,
            tax_unit("lcbp", period),
            silver_premium,
        )
        return where(
            takes_up_aca_if_eligible & pays_marketplace_premium,
            selected_plan_premium,
            0,
        )
