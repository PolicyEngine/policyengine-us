"""
Vermont Medicaid Spending Breakdown by Enrollment Category

This script calculates Vermont's Medicaid spending breakdown by category using
national per capita spending averages and Vermont's enrollment data.

Data Sources:
- EXHIBIT 21. Medicaid Spending by State, Eligibility Group, and Dually Eligible Status | MACPAC
  https://www.macpac.gov/publication/medicaid-spending-by-state-category-and-source-of-funds/

- Spending by enrollment category was created by multiplying total Medicaid spending
  by state by the percent of spending on aged enrollees.
"""

# Vermont's total Medicaid spending (FY 2022)
TOTAL_SPENDING_BILLIONS = 1.7221

# Vermont enrollment by category (in thousands)
VERMONT_ENROLLMENT = {
    "children": 71,
    "new_adult_group": 79,
    "other_adults": 15,
    "disabled": 20,
    "aged": 22,
}

# National per capita spending averages by category (in thousands of dollars)
# Source: MACPAC analysis of Medicaid spending patterns
NATIONAL_PER_CAPITA_THOUSANDS = {
    "children": 3.53851,
    "new_adult_group": 7.05447,
    "other_adults": 5.00694,
    "disabled": 24.73929,
    "aged": 17.69886,
}


def calculate_vermont_spending_breakdown():
    """
    Calculate Vermont's Medicaid spending by category using national per capita rates.

    Methodology:
    1. Calculate hypothetical spending using national per capita rates
    2. Determine adjustment factor to match Vermont's actual total
    3. Apply adjustment factor proportionally to each category

    Returns:
        dict: Spending by category in billions of dollars
    """
    # Step 1: Calculate hypothetical spending using national rates
    hypothetical_spending = {}
    total_hypothetical = 0

    for category, enrollment_thousands in VERMONT_ENROLLMENT.items():
        # Convert enrollment to actual numbers and calculate spending
        enrollment = enrollment_thousands * 1000
        per_capita = (
            NATIONAL_PER_CAPITA_THOUSANDS[category] * 1000
        )  # Convert to dollars

        # Calculate spending in billions
        spending_billions = (enrollment * per_capita) / 1_000_000_000
        hypothetical_spending[category] = spending_billions
        total_hypothetical += spending_billions

    # Step 2: Calculate adjustment factor
    # Vermont's actual spending differs from what national rates would predict
    adjustment_factor = TOTAL_SPENDING_BILLIONS / total_hypothetical

    # Step 3: Apply adjustment factor to get Vermont's actual spending
    vermont_spending = {}

    for category, hypothetical in hypothetical_spending.items():
        # Scale the hypothetical spending to match Vermont's actual total
        vermont_spending[category] = hypothetical * adjustment_factor

    return vermont_spending, adjustment_factor


def get_spending_breakdown_with_metadata():
    """
    Get Vermont's spending breakdown with additional metadata.

    Returns:
        dict: Complete breakdown with amounts, percentages, and methodology notes
    """
    spending_by_category, adjustment_factor = (
        calculate_vermont_spending_breakdown()
    )

    breakdown = {
        "total_billions": TOTAL_SPENDING_BILLIONS,
        "adjustment_factor": adjustment_factor,
        "methodology": (
            f"Spending breakdown reverse-engineered from national per capita averages. "
            f"Applied {adjustment_factor:.4f} adjustment factor to match actual total of ${TOTAL_SPENDING_BILLIONS}B"
        ),
        "categories": {},
    }

    for category, spending_billions in spending_by_category.items():
        breakdown["categories"][category] = {
            "spending_billions": round(spending_billions, 5),
            "spending_millions": round(spending_billions * 1000, 2),
            "percentage": round(
                (spending_billions / TOTAL_SPENDING_BILLIONS) * 100, 1
            ),
        }

    return breakdown


# Calculate Vermont's spending breakdown
if __name__ == "__main__":
    vermont_breakdown = get_spending_breakdown_with_metadata()

    # The calculated values for Vermont's Medicaid spending by category
    VERMONT_SPENDING_BY_CATEGORY = {
        "children": 0.24474,  # $244.74 million (14.2%)
        "new_adult_group": 0.54290,  # $542.90 million (31.5%)
        "other_adults": 0.07316,  # $73.16 million (4.2%)
        "disabled": 0.48199,  # $481.99 million (28.0%)
        "aged": 0.37931,  # $379.31 million (22.0%)
    }
