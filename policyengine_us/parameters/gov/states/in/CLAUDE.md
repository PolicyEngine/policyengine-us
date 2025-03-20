## Task Instructions: Updating Indiana State Tax Code Parameters

We have a text file named **`indiana.txt`** containing updated information about Indiana's state tax parameters. Your job is to:

1. **Identify each parameter** in our Indiana parameter YAML files that corresponds to a parameter listed in **`indiana.txt`**.
2. **Compare the 2024 values** to the existing 2023 values in our codebase.

   - If the 2024 value is **different** from the 2023 value, **append** the 2024 value as a **new entry**.
    ```yaml
    2022-01-01: 7_500
    2023-01-01: 8_100
    2024-01-01: 8_200 # <---- newly added if 2024 changed
    ```
    - If the **2023 value is the same** as the 2024 value, **do not** add a new entry; keep the 2023 date/value pair as the last entry.
3. **Add the updated reference** for 2024, **whether or not** the value changed.
    For the references, use the following format (with the correct page number from `indiana.txt`):
        - title: 2024 Indiana Income Tax Form IT-40 Instructions [PAGE NUMBER]
            href: https://www.in.gov/dor/tax-forms/individual/current/

### Page References
Page numbers appear in `indiana.txt` as `--- Page X ---`. Make sure you include the exact page where the relevant information is found.

### Change Alerts
- **Alert** if any parameter values have changed.
- After updating, **note which parameters received new 2024 values.**

### Additional Notes
- **Line length:** Keep each line ≤ 79 characters when editing the YAML files.
- **Vectorization:** Remains relevant if we add or modify formulas downstream.

### Testing
- After changes, **run `make test`** to ensure no regressions.
- Consider adding or adjusting **YAML tests** if the new parameters introduce new conditions or thresholds.