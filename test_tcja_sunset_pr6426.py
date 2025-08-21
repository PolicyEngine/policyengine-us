#!/usr/bin/env python3
"""
Test to verify that PR #6426 incorrectly extends TCJA sunset date.

This test demonstrates that the PR changes the stop date from 2026-01-01
(correct TCJA sunset) to 2035-01-01 (incorrect extension).

The TCJA expires on December 31, 2025, so parameters should revert to
pre-TCJA values starting January 1, 2026, NOT 2035.
"""

from policyengine_core.periods import instant


def test_pr_6426_incorrect_tcja_extension():
    """
    This test demonstrates the issue with PR #6426.
    
    The PR changes the stop date from instant("2026-01-01") to 
    instant("2035-01-01"), which incorrectly extends TCJA provisions
    by 9 years beyond their legal expiration.
    """
    
    # The correct TCJA sunset date per the law
    CORRECT_TCJA_SUNSET = instant("2026-01-01")
    
    # What PR #6426 incorrectly changes it to
    PR_6426_INCORRECT_DATE = instant("2035-01-01")
    
    # Check the file that was modified
    import os
    file_path = "policyengine_us/variables/gov/states/ny/tax/income/credits/ctc/ny_ctc_pre_2024_eligible.py"
    
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            content = f.read()
            
        # Check if the incorrect date is in the file
        if 'instant("2035-01-01")' in content:
            print("❌ FAIL: PR #6426 incorrectly extends TCJA sunset to 2035")
            print(f"   Found: stop=instant('2035-01-01')")
            print(f"   Expected: stop=instant('2026-01-01')")
            print("")
            print("   Legal requirement: TCJA expires December 31, 2025")
            print("   The original code was correct.")
            return False
            
        elif 'instant("2026-01-01")' in content:
            print("✅ PASS: File correctly uses 2026-01-01 for TCJA sunset")
            print("   This matches the legal requirement.")
            return True
            
        else:
            print("⚠️  Could not find either date in the file")
            return None
    else:
        print(f"⚠️  File not found: {file_path}")
        return None


if __name__ == "__main__":
    print("Testing PR #6426 - TCJA Sunset Date\n")
    print("="*50)
    
    result = test_pr_6426_incorrect_tcja_extension()
    
    print("="*50)
    if result is False:
        print("\n🚨 PR #6426 should be rejected or fixed.")
        print("The change extends TCJA 9 years beyond its legal expiration.")
        exit(1)  # Exit with error code
    elif result is True:
        print("\n✅ The code correctly implements TCJA sunset.")
        exit(0)
    else:
        print("\n⚠️  Test inconclusive.")
        exit(2)