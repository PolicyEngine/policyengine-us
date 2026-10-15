from policyengine_us.model_api import *


class medicaid_ltss_impairment_related_work_expenses(Variable):
    value_type = float
    entity = Person
    label = "Medicaid LTSS monthly impairment-related work expenses"
    unit = USD
    definition_period = MONTH
    documentation = (
        "Derives the monthly expense amount from actual money payments, "
        "reimbursements and business-cost facts. Recurring payments are "
        "deducted in their payment month. A one-time item or service "
        "payment is deducted then, or in twelve equal monthly amounts "
        "beginning then if the person elects allocation. Its payment "
        "month is the monthly input period, allowing separate purchases "
        "in different months to overlap without losing their history. "
        "Reimbursed, available-for-reimbursement and already-deducted "
        "business costs are removed before allocation. Ordinary timing "
        "requires working and receiving earned income in the payment "
        "month. Pre-work, deferred first-paycheck, after-work and special "
        "downpayment timing need additional facts and elections and are "
        "outside this calculation. The reported items or services must "
        "be needed and used for work because of the impairment and meet "
        "reasonable-charge verification; callers report actual payments, "
        "not a qualified or allocated policy amount. Claimant disability, "
        "blindness and age conditions, and the income-budget cap and "
        "exclusion order, are applied separately by derived outputs."
    )
    reference = (
        "https://regulations.delaware.gov/api/AdminCode/title16/20000/13aee487-1cd1-4726-addf-63603af28a78#page=6",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0976.htm",
        "https://www.ssa.gov/OP_Home/cfr20/416/416-1112.htm",
    )

    def formula_2026_01_01(person, period, parameters):
        working = person("medicaid_ltss_irwe_working_when_paid", period)
        monthly = max_(
            max_(person("medicaid_ltss_irwe_monthly_payments", period), 0)
            - max_(person("medicaid_ltss_irwe_monthly_reimbursements", period), 0)
            - max_(person("medicaid_ltss_irwe_monthly_business_expenses", period), 0),
            0,
        )
        expenses = person.empty_array()
        if (working & (monthly > 0)).any():
            received_earnings = person("medicaid_ltss_gross_earned_income", period) > 0
            expenses = where(working & received_earnings, monthly, 0)
        # 416.976(e)(2): the allocation begins in the payment month.
        allocation_parameter = parameters.gov.hhs.medicaid.eligibility.long_term_care.financial.federal.irwe.allocation_months
        # A shorter new allocation rule must not truncate older purchases.
        # Future policy values do not extend the current lookback.
        allocation_months = max(
            int(value.value)
            for value in allocation_parameter.values_list
            if value.instant_str <= str(period.start) and value.value is not None
        )
        for months_ago in range(allocation_months):
            paid_month = period.offset(-months_ago)
            # Keep each purchase on the allocation rule in its payment month.
            paid_allocation_months = int(allocation_parameter(paid_month.start))
            allocated = person("medicaid_ltss_irwe_allocate_over_12_months", paid_month)
            paid_while_working = person(
                "medicaid_ltss_irwe_working_when_paid", paid_month
            )
            net_payment = max_(
                max_(person("medicaid_ltss_irwe_nonrecurring_payment", paid_month), 0)
                - max_(
                    person("medicaid_ltss_irwe_nonrecurring_reimbursement", paid_month),
                    0,
                )
                - max_(
                    person(
                        "medicaid_ltss_irwe_nonrecurring_business_expenses", paid_month
                    ),
                    0,
                ),
                0,
            )
            allocated_month = allocated & (months_ago < paid_allocation_months)
            applies = paid_while_working & (allocated_month | (months_ago == 0))
            # No earnings history is needed for months with no usable payment.
            if not (applies & (net_payment > 0)).any():
                continue
            paid_with_earnings = (
                person("medicaid_ltss_gross_earned_income", paid_month) > 0
            )
            deduction = where(
                allocated_month,
                net_payment / paid_allocation_months,
                net_payment if months_ago == 0 else 0,
            )
            expenses += where(paid_while_working & paid_with_earnings, deduction, 0)
        return expenses
