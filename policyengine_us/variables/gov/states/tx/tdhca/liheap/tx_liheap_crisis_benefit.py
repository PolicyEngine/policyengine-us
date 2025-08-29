from policyengine_us.model_api import *


class tx_liheap_crisis_benefit(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP crisis benefit"
    unit = USD
    documentation = """
    Calculates emergency LIHEAP assistance for households in energy crisis.
    
    Crisis Assistance Definition (42 U.S.C. 8624(c)):
    Emergency assistance for households facing:
    - Utility disconnection within 72 hours
    - Already disconnected utilities
    - Nearly depleted heating fuel (propane, oil)
    - Broken heating/cooling equipment
    - Other energy-related emergencies
    
    Benefit Calculation:
    Crisis Benefit = min(Actual Emergency Need, Maximum Crisis Benefit)
    Maximum Crisis Benefit: $1,400 per household per year
    
    Example 1 - Disconnection Notice:
    - Past due electric bill: $850
    - Disconnection scheduled in 48 hours
    - Crisis eligible: Yes
    - Crisis amount needed: $850
    - Crisis benefit: min($850, $1,400) = $850
    - Result: Full past due amount covered
    
    Example 2 - Large Arrearage:
    - Past due gas and electric: $2,100
    - Service already disconnected
    - Crisis eligible: Yes
    - Crisis amount needed: $2,100
    - Crisis benefit: min($2,100, $1,400) = $1,400
    - Result: Maximum assistance provided, household pays $700
    
    Example 3 - Broken AC in Summer:
    - AC repair estimate: $1,200
    - Temperature forecast: 105°F
    - Crisis eligible: Yes (health/safety threat)
    - Crisis amount needed: $1,200
    - Crisis benefit: min($1,200, $1,400) = $1,200
    - Result: Full repair cost covered
    
    Example 4 - Propane Tank Empty:
    - Propane refill cost: $450
    - Tank at 5% capacity in winter
    - Crisis eligible: Yes
    - Crisis amount needed: $450
    - Crisis benefit: min($450, $1,400) = $450
    - Result: Tank refilled completely
    
    Example 5 - No Crisis Situation:
    - Current on all utilities
    - Equipment functioning
    - Adequate fuel supply
    - Crisis eligible: No
    - Crisis benefit: $0
    - Result: May still receive regular LIHEAP benefit
    
    Crisis vs Regular Benefits:
    - Crisis: One-time emergency payment up to $1,400
    - Regular: Annual assistance based on household size
    - Can receive both in same year if eligible
    - Crisis paid directly to vendor/utility company
    
    Payment Method:
    - Paid directly to utility company or fuel vendor
    - Not paid to household
    - Resolves immediate emergency
    - May require documentation of crisis
    
    Edge Cases:
    - Multiple crises: Limited to $1,400 total per year
    - Partial payment: Household responsible for remainder
    - Equipment replacement: May require multiple funding sources
    
    Related variables:
    - tx_liheap_crisis_eligible: Determines crisis qualification
    - utility_expense: Used as proxy for crisis amount
    - tx_liheap_regular_benefit: Separate regular assistance
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8624(c) - Crisis intervention",
        "Texas Administrative Code Title 10, Chapter 5, Section 5.309",
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.tx.tdhca.liheap

        # Check crisis eligibility per 42 U.S.C. 8624(c)
        # Must have immediate energy-related emergency
        crisis_eligible = spm_unit("tx_liheap_crisis_eligible", period)

        # Get utility expenses as proxy for crisis amount needed
        # In practice, would be actual emergency amount (past due, repair cost, etc.)
        # utility_expense is a YEAR variable, so we need to access the year period
        utility_expense = spm_unit("utility_expense", period.this_year)

        # Crisis benefit is limited to actual need or maximum per State Plan Section 5.2
        # Maximum crisis assistance is $1,400 per household per year
        crisis_amount = min_(utility_expense, p.crisis_maximum_benefit)

        # Return crisis benefit only if crisis eligible
        # Non-crisis households receive $0 crisis assistance
        return where(crisis_eligible, crisis_amount, 0)
