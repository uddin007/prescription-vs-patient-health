# Databricks notebook source
# MAGIC %md
# MAGIC #### Solution Approach
# MAGIC 1. Patient’s health status based on their diagnostic data (like “Patient 0123 has anemia and skin infection”) is obtained by using:
# MAGIC   * Filtering ICD-10 code starting with 'Z' (medical exam, screening etc.) from Diagnosis table
# MAGIC   * Left join ccs table with Diagnosis table to obtain health status vs patient_id 
# MAGIC   * Group health status by patient id to provide all status detail in a list (pat_health_status table)
# MAGIC 
# MAGIC 2. Predicting Heath Status using Prescription Data alone:
# MAGIC   * A model is developed using one of the Association Rule algorithms called **Apriori**
# MAGIC   * Association rule: Popular use of this rule is in marketing i.e. "people who bought this also bought...", "people who watched this also watched" etc.
# MAGIC   * Current prediction: Association rule is used to estabilish a relationship between prescription and health status to predict the latter
# MAGIC   * Detail approach is provided below.

# COMMAND ----------

# MAGIC %md
# MAGIC ## Apriori
# MAGIC Apriori algorithm establishes association using three calculated variables:
# MAGIC * Prescription (p) **support** = (records contain p)/(number of records)
# MAGIC * Prescription to health-status **confidence** (p -> s) = (records contain p, s)/(records contain p)
# MAGIC * Prescription to health-status **lift** (p -> s) = (confidence (p -> s)/support (s))
# MAGIC 
# MAGIC This algorithm will also map relation where basis is health-status, those items are eventually filtered out, as we're only looking to map prescription -> health-status

# COMMAND ----------

# MAGIC %md
# MAGIC load the the Apriori and other python packages 

# COMMAND ----------

# MAGIC %pip install apyori

# COMMAND ----------

import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import pyspark.sql.functions as f
from pyspark.sql.functions import collect_set
from pyspark.sql.functions import udf
from apyori import apriori

# COMMAND ----------

# MAGIC %md
# MAGIC Transform and join Diagnosis with CCS

# COMMAND ----------

ccs = spark.table("ccs")
display(ccs)

# COMMAND ----------

diagnosis = spark.table("diagnosis")
diagnosis = diagnosis.filter("LEFT(ICD10,1) != 'Z'").withColumn("diag", f.regexp_replace("ICD10", "[^A-Z0-9_]", ""))
diag_ccs_join = diagnosis.join(ccs, diagnosis.diag == ccs.diag, 'left')
display(diag_ccs_join)

# COMMAND ----------

# MAGIC %md
# MAGIC Collect all health-status grouping by patient IDs

# COMMAND ----------

pat_health_status = diag_ccs_join.groupby('Patient_id').agg(collect_set(f.col('ccs_3_desc')).alias('pat_health_status'))
display(pat_health_status)

# COMMAND ----------

# MAGIC %md
# MAGIC Create list of prescription and health-status as an input to Apriori algorithm

# COMMAND ----------

prescriptions = spark.table("prescriptions")

presriptions_health_join = prescriptions.select('Patient_id', 'drug_category').join(pat_health_status, prescriptions.Patient_id == pat_health_status.Patient_id).distinct()
presriptions_health_join = presriptions_health_join.withColumn("drug_cat_list", f.array('drug_category'))  
display(presriptions_health_join)

# COMMAND ----------

spark.conf.set("spark.sql.execution.arrow.enabled", "true")
result_pdf = presriptions_health_join.select("pat_health_status", "drug_cat_list").toPandas()
result_list = result_pdf['drug_cat_list'].apply(lambda x: x.tolist()) + result_pdf['pat_health_status'].apply(lambda x: x.tolist())
result_list.tolist()[0]

# COMMAND ----------

prescription_list = result_pdf['drug_cat_list'].apply(lambda drug_cat_list: " ".join(set(drug_cat_list))).tolist()

# COMMAND ----------

# MAGIC %md
# MAGIC * Input the list of prescription and health-status to the develop the model
# MAGIC * Enter model parameters
# MAGIC * Parameter tuning needs to be done for better performance (not in scope of this study)

# COMMAND ----------

rules = apriori(transactions = result_list.tolist(), min_support = 0.003, min_confidence = 0.1, min_lift = 2, min_length = 2, max_length = 2)

# COMMAND ----------

results = list(rules)

# COMMAND ----------

# MAGIC %md
# MAGIC Create association rules dataframe for prediction 

# COMMAND ----------

def inspect(results):
    lhs         = [tuple(result[2][0][0])[0] for result in results]
    rhs         = [tuple(result[2][0][1])[0] for result in results]
    supports    = [result[1] for result in results]
    confidences = [result[2][0][2] for result in results]
    lifts       = [result[2][0][3] for result in results]
    return list(zip(lhs, rhs, supports, confidences, lifts))
resultsinDataFrame = pd.DataFrame(inspect(results), columns = ['prescription', 'health-status', 'Support', 'Confidence', 'Lift'])

boolean_series = resultsinDataFrame.prescription.isin(prescription_list)
filtered_df = resultsinDataFrame[boolean_series]

# COMMAND ----------

# MAGIC %md
# MAGIC Use the model to predict health-status, as follows:
# MAGIC * For 'Antivirals' prescription, possible health statuses are Influenza and Viral infection

# COMMAND ----------

filtered_df[filtered_df['prescription'] == 'Antivirals']
