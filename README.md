# prescription-vs-patient-health

The goal of this project is to:
* develop a solution to define a patient’s health status using diagnosis data
* Predict a patient’s health status using prescriptions data.

The dataset contains 85,000 patients over a period of 3 years. The tables are as follows:
* Patient Diagnosis. Each row of this dataset contains a patient’s diagnosis provided on a specific date. The diagnosis codes are presented in a standard called ICD-10.  
* Patient Prescriptions. Each row of this dataset contains a patient’s prescription filled on a specific date. The prescriptions contain drug category, drug group, and drug class.
* ICD-to-Clinical Categories Map (CCS). Each row in this file contains an ICD-10 diagnosis code and diagnosis descriptions as explained here: https://www.hcup-us.ahrq.gov/toolssoftware/ccs10/ccs10.jsp. Not all diagnosis codes have a CSS code.

# Solution Approach
1. Patient’s health status based on their diagnostic data (like “Patient 0123 has anemia and skin infection”) is obtained by using:
  * Filtering ICD-10 code starting with 'Z' (medical exam, screening etc.) from Diagnosis table
  * Left join ccs table with Diagnosis table to obtain health status vs patient_id 
  * Group health status by patient id to provide all status detail in a list (pat_health_status table)

2. Predicting Heath Status using Prescription Data alone:
  * A model is developed using one of the Association Rule algorithms called **Apriori**
  * Association rule: Popular use of this rule is in marketing i.e. "people who bought this also bought...", "people who watched this also watched" etc.
  * Current prediction: Association rule is used to estabilish a relationship between prescription and health status to predict the latter
  * Detail approach is provided below.
  
# Apriori
Apriori algorithm establishes association using three calculated variables:
* Prescription (p) **support** = (records contain p)/(number of records)
* Prescription to health-status **confidence** (p -> s) = (records contain p, s)/(records contain p)
* Prescription to health-status **lift** (p -> s) = (confidence (p -> s)/support (s))

This algorithm will also map relation where basis is health-status, those items are eventually filtered out, as we're only looking to map prescription -> health-status

# Results
Relation between patient health status and drug categories are shown below:

<img width="1147" alt="Screenshot 2022-12-17 at 10 00 15 PM" src="https://user-images.githubusercontent.com/37245809/208279218-25103e16-8836-4a41-87fd-802a52f1ec87.png">

The algorithm is used to predict health-status, for example, for 'Antivirals' prescription, possible health statuses are 'Influenza' and 'Viral infection'. This data is presented with three algorithm parameters i.e. Support, Confidence and Lift.

<img width="712" alt="Screenshot 2022-12-17 at 10 04 42 PM" src="https://user-images.githubusercontent.com/37245809/208279297-2a90ee4e-5c9d-4180-bcb9-bd6bd4562dd4.png">



