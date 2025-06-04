from policyengine_us.model_api import *
import numpy  # needed for zeros_like

class income_adjusted_part_b_premium(Variable):
    value_type = float
    entity      = Person
    label       = "Medicare Part B premium (income-adjusted)"
    unit        = USD
    definition_period = YEAR

    def formula(person, period, parameters):
        # Gate: only Medicare-eligible people pay anything
        is_eligible = person("is_medicare_eligible", period)
        if not is_eligible.any():
            return numpy.zeros_like(is_eligible, dtype=float)

        tax_unit      = person.tax_unit
        filing_status = tax_unit("filing_status",        period)
        income        = tax_unit("employment_income",    period)
        base          = person("base_part_b_premium",    period)

        # Build boolean masks for each status
        status      = filing_status.possible_values
        statuses    = [
            status.SINGLE,
            status.JOINT,
            status.HEAD_OF_HOUSEHOLD,
            status.SURVIVING_SPOUSE,      # ← spelling fixed
            status.SEPARATE,
        ]
        in_status   = [filing_status == s for s in statuses]

        # Helper: safe access to a parameter node
        p_root = parameters(period).gov.hhs.medicare.part_b.irmaa
        def safe_calc(node_name):
            try:
                return getattr(p_root, node_name).calc(income)
            except Exception:                         # node missing → zeros
                return numpy.zeros_like(income, dtype=float)

        irmaa_amount = select(
            in_status,
            [
                safe_calc("single"),
                safe_calc("joint"),
                safe_calc("head_of_household"),
                safe_calc("surviving_spouse"),
                safe_calc("separate"),
            ],
        )

        return is_eligible * (base + irmaa_amount)
