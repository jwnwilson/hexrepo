import pytest
from pyspark.sql import SparkSession, Row


# ---------------------------------------------------------------------------
# Session-scoped SparkSession — created once for the entire test run.
# Use this for the vast majority of tests: it's fast because Spark only
# starts up once, and PySpark sessions are designed to be reused.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def spark() -> SparkSession:
    """
    A single SparkSession shared across the whole test suite.
    Connects to the local cluster defined in docker-compose when
    SPARK_MASTER is set, otherwise falls back to local[*] mode so
    tests can also run without Docker (e.g. in CI).
    """
    import os

    master = os.getenv("SPARK_MASTER", "local[*]")

    session = (
        SparkSession.builder
        .master(master)
        .appName("pytest-session")
        # Keep shuffle partitions small for unit tests — default 200 is
        # overkill and slows down small DataFrames considerably.
        .config("spark.sql.shuffle.partitions", "4")
        .config("spark.default.parallelism", "4")
        # Silence noisy executor logs in test output.
        .config("spark.ui.showConsoleProgress", "false")
        .getOrCreate()
    )

    session.sparkContext.setLogLevel("WARN")

    yield session

    session.stop()


# ---------------------------------------------------------------------------
# Convenience fixture: a fresh SparkContext reference (derived from the
# session above — no extra overhead).
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def sc(spark: SparkSession):
    return spark.sparkContext


# ---------------------------------------------------------------------------
# Function-scoped fixture — use sparingly, only when a test genuinely
# needs a clean session (e.g. testing custom SparkSession configuration).
# Creates + tears down a full Spark context per test, so it's slow.
# ---------------------------------------------------------------------------

@pytest.fixture(scope="function")
def isolated_spark() -> SparkSession:
    """
    A short-lived SparkSession for tests that need custom config or that
    must not share state with other tests.  Use the session-scoped `spark`
    fixture by default and reserve this for the rare cases that need it.
    """
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("pytest-isolated")
        .config("spark.sql.shuffle.partitions", "2")
        .config("spark.ui.showConsoleProgress", "false")
        # Required when running alongside the session-scoped fixture in the
        # same process — lets a new session coexist.
        .config("spark.driver.allowMultipleContexts", "true")
        .getOrCreate()
    )

    session.sparkContext.setLogLevel("ERROR")

    yield session

    session.stop()


# ---------------------------------------------------------------------------
# Helper fixture: resets any temp views registered during a test so they
# don't leak into subsequent tests sharing the same session.
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def clean_temp_views(spark: SparkSession):
    yield
    for view in spark.catalog.listTables():
        if view.isTemporary:
            spark.catalog.dropTempView(view.name)



@pytest.fixture()
def df(spark):
    rows = [
        Row(order_id=1, customer="alice", amount=99.99),
        Row(order_id=2, customer="bob",   amount=49.50),
    ]
    return spark.createDataFrame(rows)


@pytest.fixture()
def table_name():
    return "test_table"

