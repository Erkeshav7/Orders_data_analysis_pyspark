from pyspark.sql import SparkSession
from pyspark.sql.functions import regexp_replace

# Create a SparkSession
spark = SparkSession.builder \
    .appName("Orders-Customers-Data-Analysis") \
    .enableHiveSupport() \
    .getOrCreate()

# 1. Read both tables from Hive and store them in different dataframes
df_orders = spark.table("tables_by_spark.orders")
df_customers = spark.table("tables_by_spark.customers")

print('Read orders and customers data successfully')

# 2. Remove double quotes from order_id and customer_id in orders dataframe
df_orders = df_orders.withColumn("order_id", regexp_replace("order_id", "\"", "")) \
                     .withColumn("customer_id", regexp_replace("customer_id", "\"", ""))

# 3. Remove double quotes from customer_id and customer_unique_id in customers dataframe
df_customers = df_customers.withColumn("customer_id", regexp_replace("customer_id", "\"", "")) \
                           .withColumn("customer_unique_id", regexp_replace("customer_unique_id", "\"", ""))

# Cache the dataframes to optimize reading operations
df_orders.cache()
df_customers.cache()

# 4. Filter records where order_status='delivered' in orders dataframe
df_orders_delivered = df_orders.filter(df_orders.order_status == 'delivered')

# 5. Perform groupby operation on customer_id column to calculate number of orders delivered to each customer
df_orders_grouped = df_orders_delivered.groupBy("customer_id").count()

# 6. Do a left join of customers dataframe with df_orders_grouped on customer_id column
df_joined = df_customers.join(df_orders_grouped, on="customer_id", how="left")

print('Join completed')

# 7. Show some records (First Action - triggers first job with multiple stages)
df_joined.show()

# Trigger an action to materialize the cached dataframes (Second Action - triggers second job)
df_orders.count()
df_customers.count()

# Stop the SparkSession
spark.stop()