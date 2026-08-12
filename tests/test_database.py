import pytest
from django.db import connection


@pytest.mark.django_db
def test_database_connection_executes_query():
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

    assert result == (1,)

