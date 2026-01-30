"""
Tests for SQL Runner safety layer.
Chat2App Module - MDP Platform V3.1
"""
import pytest
from app.engine.sql_runner import validate_sql, SQLValidationError


class TestSQLValidation:
    """Test cases for SQL validation logic."""

    def test_valid_select_query(self):
        """应该接受有效的 SELECT 查询"""
        sql = "SELECT * FROM objects WHERE object_type = 'Target'"
        assert validate_sql(sql) is True

    def test_valid_select_with_join(self):
        """应该接受带 JOIN 的 SELECT 查询"""
        sql = """
        SELECT o.id, o.display_name, p.property_value
        FROM objects o
        JOIN object_properties p ON o.id = p.object_id
        WHERE o.object_type = 'Target'
        """
        assert validate_sql(sql) is True

    def test_valid_select_with_limit(self):
        """应该接受带 LIMIT 的 SELECT 查询"""
        sql = "SELECT id, display_name FROM objects LIMIT 50"
        assert validate_sql(sql) is True

    def test_reject_empty_sql(self):
        """应该拒绝空 SQL"""
        with pytest.raises(SQLValidationError, match="cannot be empty"):
            validate_sql("")

    def test_reject_whitespace_only_sql(self):
        """应该拒绝仅空白的 SQL"""
        with pytest.raises(SQLValidationError, match="cannot be empty"):
            validate_sql("   \n\t  ")

    def test_reject_insert_statement(self):
        """应该拒绝 INSERT 语句"""
        sql = "INSERT INTO objects (id, name) VALUES ('id1', 'name1')"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)

    def test_reject_update_statement(self):
        """应该拒绝 UPDATE 语句"""
        sql = "UPDATE objects SET name = 'hacked' WHERE 1=1"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)

    def test_reject_delete_statement(self):
        """应该拒绝 DELETE 语句"""
        sql = "DELETE FROM objects WHERE id = '123'"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)

    def test_reject_drop_table(self):
        """应该拒绝 DROP TABLE"""
        sql = "DROP TABLE objects"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)

    def test_reject_truncate_table(self):
        """应该拒绝 TRUNCATE TABLE"""
        sql = "TRUNCATE TABLE objects"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)

    def test_reject_sql_injection_comment(self):
        """应该拒绝 SQL 注入（注释）"""
        sql = "SELECT * FROM objects -- WHERE 1=1"
        with pytest.raises(SQLValidationError, match="Forbidden"):
            validate_sql(sql)

    def test_reject_block_comment(self):
        """应该拒绝块注释"""
        sql = "SELECT * FROM objects /* comment */ WHERE id = '1'"
        with pytest.raises(SQLValidationError, match="Forbidden"):
            validate_sql(sql)

    def test_reject_multiple_statements(self):
        """应该拒绝多语句查询"""
        sql = "SELECT * FROM objects; DROP TABLE objects;"
        with pytest.raises(SQLValidationError, match="Forbidden"):
            validate_sql(sql)

    def test_reject_sleep_injection(self):
        """应该拒绝 SLEEP 注入"""
        sql = "SELECT * FROM objects WHERE SLEEP(10)"
        with pytest.raises(SQLValidationError, match="Forbidden"):
            validate_sql(sql)

    def test_reject_benchmark_injection(self):
        """应该拒绝 BENCHMARK 注入"""
        sql = "SELECT BENCHMARK(1000000, SHA1('test'))"
        with pytest.raises(SQLValidationError, match="Forbidden"):
            validate_sql(sql)

    def test_case_insensitive_detection(self):
        """应该检测大小写混合的危险关键字"""
        sql = "DeLeTe FROM objects WHERE id = '1'"
        with pytest.raises(SQLValidationError, match="Only SELECT"):
            validate_sql(sql)
