# Task Instructions: Updating Montana State Tax Code Parameters

## Objective
Update Montana state tax parameters based on new information from 3 text files named **`montana1.txt`** **`montana2.txt`** and **`montana3.txt`**.
They are broken up so they all fit in your context windows. You may have to search more than one for each parameter

## Step-by-Step Instructions

### Step 1: Parameter Identification
- Locate and identify each parameter in the Montana parameter YAML files that corresponds to a parameter listed in one of the files
- The parameters are located policyengine_us/parameters/gov/states/mt


### Step 2: Value Comparison and Update
- Compare the 2024 values to the existing 2023 values in the codebase.
- Follow these update rules:
  1. If the 2024 value is **different** from the 2023 value:
     - Append the 2024 value as a **new entry**
     - Example:
       ```yaml
       2022-01-01: 7_500
       2023-01-01: 8_100
       2024-01-01: 8_200  *# <--- newly added if 2024 changed*
       ```
  2. If the 2023/whatever value is the most recent entry value is the **same** as the 2024 value:
     - **Do not** add a new entry
     - Keep the 2023 date/value pair as the last entry

### Step 3: Reference Addition
- Add an updated reference for 2024, **regardless** of whether the value changed
- Use the following reference format (with the correct page number from **`montana1.txt`** **`montana2.txt`** **`montana3.txt`**.):
  ```yaml
  - title: 2024 Montana Income Tax Form Instructions
    href: https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2025/02/Form-2-Instructions-2024-2.pdf
  ```

### Step 4: Page Reference Verification
- Locate page numbers in `montana1.txt` `montana2.txt` and `montana3.txt` marked as `--- Page X ---`
- Ensure you include the exact page where the relevant information is found

### Step 5: Change Tracking
- **Alert** if any parameter values have changed
- Create a list of parameters that received new 2024 values

### Step 6: Technical Considerations
- **Line Length**: Maintain each line ≤ 79 characters when editing YAML files
- **Vectorization**: Ensure continued relevance for downstream formula modifications

### Step 7: Changelog Documentation
- Update `changelog_entry.yaml` with a summary of Montana parameter updates


## Important Notes
- Be precise and methodical in your updates
- Double-check all parameter values and references
- Maintain the integrity of the existing data structure
- Every parameter file should have an updated reference 
