from policyengine_us.model_api import *


class nm_cdcc_max_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico maximum credit for child and dependent day care amount"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.NM
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # p63

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.nm.tax.income.credits.cdcc
        person = tax_unit.members
        eligible_dependent = person("is_cdcc_eligible", period)
        # For each dependent we take the number of days in daycare
        # the daily amount can not exceed $8
        daily_expenses = min_(
            person("daily_childcare_expenses", period), p.max_daily_amount
        )
        childcare_days = person("childcare_days_per_year", period)
        total_expenses = eligible_dependent * (childcare_days * daily_expenses)
        # These costs are multiplied by 0.4 and capped at $480 per child
        reimbursed_costs = min_(
            total_expenses * p.rate, p.max_amount.one_person
        )
        # Total cap is $1,200
        total_costs = tax_unit.sum(reimbursed_costs)
        return min_(total_costs, p.max_amount)
