from policyengine_us.model_api import *


class tx_liheap(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Texas LIHEAP benefit"
    unit = USD
    documentation = """
    Total Texas LIHEAP (Low Income Home Energy Assistance Program) benefit combining
    regular and crisis assistance for the year.
    
    LIHEAP Components:
    1. Regular Benefit: Annual assistance based on household size and priority status
       - Range: $1 to $12,300 per year
       - Adjusted for household size (52% to 196% of maximum)
       - 20% bonus for priority households
    
    2. Crisis Benefit: Emergency assistance for immediate energy threats
       - Maximum: $2,400 per year
       - For disconnections, broken equipment, depleted fuel
       - Paid directly to utility/vendor
    
    Total Maximum Benefit: $14,700 ($12,300 regular + $2,400 crisis)
    
    Example 1 - Regular Assistance Only:
    - Elderly couple, income $25,000/year
    - Regular benefit: $8,364 base × 1.2 priority = $10,037
    - Crisis benefit: $0 (no emergency)
    - Total LIHEAP: $10,037
    
    Example 2 - Crisis Assistance Only:
    - Family facing disconnection, income $45,000
    - Regular benefit: $0 (over income for regular)
    - Crisis benefit: $1,200 (past due amount)
    - Total LIHEAP: $1,200
    
    Example 3 - Both Regular and Crisis:
    - Single parent with toddler, income $18,000
    - Regular benefit: $6,396 × 1.2 = $7,675
    - Crisis benefit: $800 (winter disconnection notice)
    - Total LIHEAP: $8,475
    
    Example 4 - Maximum Assistance:
    - Large priority family (8 people), elderly member
    - Regular benefit: Capped at $12,300
    - Crisis benefit: $2,400 (broken heating system)
    - Total LIHEAP: $14,700 (maximum possible)
    
    Example 5 - Ineligible Household:
    - High income household ($80,000)
    - No categorical eligibility
    - Regular benefit: $0
    - Crisis benefit: $0
    - Total LIHEAP: $0
    
    Program Impact:
    - Serves approximately 150,000 Texas households annually
    - Average benefit: $400-600 for cooling, $300-400 for heating
    - Prevents an estimated 2,000+ utility disconnections yearly
    - Reduces energy burden from 15-20% to 10-12% for recipients
    
    Payment Method:
    - Benefits paid directly to utility companies or fuel vendors
    - Households don't receive cash payments
    - Credits appear on utility bills
    - Crisis payments resolve immediate emergencies
    
    Related variables:
    - tx_liheap_regular_benefit: Standard annual assistance
    - tx_liheap_crisis_benefit: Emergency assistance
    - tx_liheap_eligible: Overall program eligibility
    - tx_liheap_priority_group: Determines benefit enhancement
    """
    reference = [
        "https://www.tdhca.texas.gov/sites/default/files/2023-10/FY2024-LIHEAP-State-Plan.pdf",
        "42 U.S.C. 8621-8630 - Low-Income Home Energy Assistance Act",
        "Texas Administrative Code Title 10, Part 1, Chapter 5, Subchapter A"
    ]
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get regular benefit per State Plan Section 4
        # Annual assistance based on household size and priority status
        regular_benefit = spm_unit("tx_liheap_regular_benefit", period)
        
        # Get crisis benefit per State Plan Section 5
        # Emergency assistance for immediate energy threats
        crisis_benefit = spm_unit("tx_liheap_crisis_benefit", period)

        # Total benefit is sum of regular and crisis assistance
        # Per 42 U.S.C. 8624: States may provide both regular and crisis assistance
        # Maximum combined benefit: $12,300 + $2,400 = $14,700
        return regular_benefit + crisis_benefit
