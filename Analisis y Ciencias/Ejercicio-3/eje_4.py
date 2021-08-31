#$SPARK_HOME/bin/spark-submit --conf spark.executor.cores=2 --conf spark.executor.memory=2G --master spark://spark-master:7077 /home/st03/py/eje_1.py


from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql import Row, Window
from pyspark.sql.types import IntegerType
import hashlib

#   Init spark session
spark = SparkSession.builder \
    .master("local") \
    .config("spark.sql.autoBroadcastJoinThreshold", -1) \
    .config("spark.executor.memory", "3g") \
    .appName("Exercise4_st03") \
    .getOrCreate()

#   Load source data
products_table = spark.read.parquet("./products_parquet")
sales_table = spark.read.parquet("./sales_parquet")
sellers_table = spark.read.parquet("./sellers_parquet")

#   Define the UDF function
def algo(order_id, bill_text):
    #   If number is even
    ret = bill_text.encode("utf-8")
    if int(order_id) % 2 == 0:
        #   Count number of 'A'
        cnt_A = bill_text.count("A")
        for _c in range(0, cnt_A):
            ret = hashlib.md5(ret).hexdigest().encode("utf-8")
        ret = ret.decode('utf-8')
    else:
        ret = hashlib.sha256(ret).hexdigest()
    return ret

#   Register the UDF function.
algo_udf = spark.udf.register("algo", algo)

#   Use the `algo_udf` to apply the aglorithm and then check if there is any duplicate hash in the table
sales_table.withColumn("hashed_bill", algo_udf(col("order_id"), col("bill_raw_text")))\
    .groupby(col("hashed_bill")).agg(count("*").alias("cnt")).where(col("cnt") > 1).show()
