import pytest

import pyspark.sql.functions as F
from pyspark.sql import SparkSession


def test_df_not_empty(df):
    
    # Get row count directly from DataFrame
    row_count = df.count()
    
    # Simple validation
    assert row_count > 0
