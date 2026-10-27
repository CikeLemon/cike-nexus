"""工具配置回归检查，仅使用占位配置、内存数据库和离线迁移环境。"""

import importlib.util
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest import TestCase, main
from unittest.mock import MagicMock, patch

from alembic.config import Config
from alembic.migration import MigrationContext
from alembic.operations import Operations
from alembic.script import ScriptDirectory
from pydantic import ValidationError
from sqlalchemy import JSON, text
from sqlalchemy.exc import StatementError
from sqlmodel import Session, create_engine

from cike_nexus.data.entities.Tool import Tool
from cike_nexus.data.enums.ToolType import ToolType
from cike_nexus.data.PydanticJsonType import PydanticJsonType
from cike_nexus.data.value_objects.McpToolConfigValue import (
    HttpMcpToolConfigValue,
    StdioMcpToolConfigValue,
)
from cike_nexus.data.value_objects.SkillToolConfigValue import SkillToolConfigValue
from cike_nexus.data.value_objects.ToolConfigValue import (
    parse_tool_config,
    tool_config_adapter,
)


CASES = (
    (
        ToolType.StdioMCP,
        StdioMcpToolConfigValue,
        {"type": "StdioMCP", "command": "example-command", "args": [], "env": {}},
    ),
    (
        ToolType.HttpMCP,
        HttpMcpToolConfigValue,
        {"type": "HttpMCP", "url": "https://example.invalid/mcp", "headers": {}, "timeout": 30},
    ),
    (
        ToolType.SKILL,
        SkillToolConfigValue,
        {"type": "SKILL", "url": "https://example.invalid/skill"},
    ),
)
BACKEND = Path(__file__).resolve().parents[1]


def tool_data(tool_type, config, **overrides):
    return {
        "type": tool_type,
        "config": config,
        "update_at": datetime.now(timezone.utc),
        **overrides,
    }


class ToolConfigTests(TestCase):
    def test_branches_defaults_and_json(self):
        for tool_type, config_class, raw in CASES:
            with self.subTest(tool_type=tool_type):
                parsed = parse_tool_config(raw)
                self.assertIsInstance(parsed, config_class)
                self.assertIs(parsed.type, tool_type)
                self.assertIs(parse_tool_config(parsed), parsed)
                config = config_class(**{k: v for k, v in raw.items() if k != "type"})
                self.assertIs(config.type, tool_type)
                self.assertIsInstance(parse_tool_config(config), config_class)
                dumped = tool_config_adapter.dump_python(parsed, mode="json")
                self.assertEqual(dumped, raw)
                self.assertEqual(tool_config_adapter.validate_json(tool_config_adapter.dump_json(parsed)), parsed)
                self.assertIsInstance(parse_tool_config({**raw, "type": tool_type}), config_class)

    def test_reject_invalid_configs(self):
        for raw in (None, {}, [], {"type": "unknown"}, {"url": "https://example.invalid"}):
            with self.subTest(raw=raw), self.assertRaises(ValidationError):
                parse_tool_config(raw)
        for tool_type, config_class, raw in CASES:
            with self.subTest(tool_type=tool_type), self.assertRaises(ValidationError):
                config_class(**{**raw, "type": "unknown"})
            for field in config_class.model_fields:
                if field != "type":
                    with self.subTest(tool_type=tool_type, field=field), self.assertRaises(ValidationError):
                        parse_tool_config({k: v for k, v in raw.items() if k != field})

    def test_discriminator_schema(self):
        schema = tool_config_adapter.json_schema()
        self.assertEqual(schema["discriminator"]["propertyName"], "type")
        self.assertEqual(set(schema["discriminator"]["mapping"]), {t.value for t in ToolType})


class ToolEntityTests(TestCase):
    def test_constructor_and_model_validate(self):
        for tool_type, config_class, raw in CASES:
            for factory in (Tool, Tool.model_validate):
                with self.subTest(tool_type=tool_type, factory=factory.__name__):
                    data = tool_data(tool_type.value, raw)
                    entity = factory(**data) if factory is Tool else factory(data)
                    self.assertIs(entity.type, tool_type)
                    self.assertIsInstance(entity.config, config_class)
                    self.assertEqual(entity.model_dump(mode="json")["config"], raw)
            self.assertIsInstance(Tool(**tool_data(tool_type, config_class(**raw))).config, config_class)

    def test_required_and_matching_type(self):
        raw = CASES[2][2]
        valid = tool_data("SKILL", raw)
        invalid = (
            {},
            {k: v for k, v in valid.items() if k != "type"},
            {k: v for k, v in valid.items() if k != "config"},
            {**valid, "type": None},
            {**valid, "type": ""},
            {**valid, "config": None},
            {**valid, "type": "HttpMCP"},
        )
        for data in invalid:
            for factory in (Tool, Tool.model_validate):
                with self.subTest(data=data, factory=factory.__name__), self.assertRaises(ValueError):
                    factory(**data) if factory is Tool else factory(data)

    def test_metadata_contract(self):
        table = Tool.__table__
        self.assertEqual(table.name, "tool")
        self.assertIsInstance(table.c.config.type, PydanticJsonType)
        self.assertIsInstance(table.c.config.type.impl, JSON)
        self.assertFalse(table.c.config.nullable)
        self.assertFalse(table.c.type.nullable)
        self.assertEqual(table.c.type.type.enums, ["StdioMCP", "HttpMCP", "SKILL"])
        self.assertEqual(table.c.name.type.length, 256)
        self.assertEqual(table.c.description.type.length, 512)
        self.assertTrue(Tool.model_fields["type"].is_required())
        self.assertTrue(Tool.model_fields["config"].is_required())
        self.assertEqual(
            {index.name for index in table.indexes},
            {f"ix_tool_{name}" for name in (
                "create_at", "created_by", "is_deleted", "updated_by",
                "name", "description", "type", "disabled",
            )},
        )

    def test_database_round_trip(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            Tool.__table__.create(engine)
            with Session(engine) as session:
                for index, (tool_type, _, raw) in enumerate(CASES, start=1):
                    entity = Tool(**tool_data(tool_type.value, raw, id=index))
                    # 模拟未经过构造器的配置字典赋值，确认落库边界也会解析。
                    entity.config = dict(raw)
                    session.add(entity)
                session.commit()
            with Session(engine) as session:
                for index, (tool_type, config_class, raw) in enumerate(CASES, start=1):
                    entity = session.get(Tool, index)
                    self.assertIs(entity.type, tool_type)
                    self.assertIsInstance(entity.config, config_class)
                    self.assertEqual(tool_config_adapter.dump_python(entity.config, mode="json"), raw)
            with engine.connect() as connection:
                self.assertEqual(connection.execute(text("SELECT type FROM tool ORDER BY id")).scalars().all(),
                                 [t.value for t in ToolType])
        finally:
            engine.dispose()

    def test_invalid_config_rejected_on_write(self):
        engine = create_engine("sqlite:///:memory:")
        try:
            Tool.__table__.create(engine)
            with Session(engine) as session:
                entity = Tool(**tool_data("SKILL", CASES[2][2], id=1))
                entity.config = {"type": "HttpMCP"}
                session.add(entity)
                with self.assertRaises(StatementError):
                    session.commit()
                session.rollback()
                self.assertIsNone(session.get(Tool, 1))
        finally:
            engine.dispose()


class ToolMigrationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        path = BACKEND / "alembic" / "versions" / "fa0e32874b19_tool_config_not_null.py"
        spec = importlib.util.spec_from_file_location("tool_config_migration", path)
        cls.migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.migration)

    def test_revision_chain(self):
        config = Config()
        config.set_main_option("script_location", str(BACKEND / "alembic"))
        scripts = ScriptDirectory.from_config(config)
        self.assertEqual(scripts.get_heads(), [self.migration.revision])
        self.assertEqual(self.migration.down_revision, "c6510b57d8b4")

    def test_offline_mysql_upgrade_and_downgrade(self):
        for method, expected in ((self.migration.upgrade, "NOT NULL"), (self.migration.downgrade, "NULL")):
            with self.subTest(method=method.__name__):
                output = StringIO()
                migration_context = MigrationContext.configure(
                    dialect_name="mysql", opts={"as_sql": True, "output_buffer": output},
                )
                with Operations.context(migration_context), patch.object(
                    self.migration.context, "is_offline_mode", return_value=True,
                ):
                    method()
                self.assertEqual(output.getvalue().strip(), f"ALTER TABLE tool MODIFY config JSON {expected};")

    def test_online_empty_config_blocks_alter(self):
        bind = MagicMock()
        bind.execute.return_value.first.return_value = (1,)
        with patch.object(self.migration.context, "is_offline_mode", return_value=False), patch.object(
            self.migration.op, "get_bind", return_value=bind,
        ), patch.object(self.migration.op, "alter_column") as alter:
            with self.assertRaisesRegex(RuntimeError, "空的工具配置"):
                self.migration.upgrade()
            alter.assert_not_called()
        query = str(bind.execute.call_args.args[0])
        self.assertIn("config IS NULL", query)
        self.assertIn("JSON_TYPE(config) = 'NULL'", query)

    def test_online_valid_data_allows_alter(self):
        bind = MagicMock()
        bind.execute.return_value.first.return_value = None
        with patch.object(self.migration.context, "is_offline_mode", return_value=False), patch.object(
            self.migration.op, "get_bind", return_value=bind,
        ), patch.object(self.migration.op, "alter_column") as alter:
            self.migration.upgrade()
            self.assertEqual(alter.call_args.args, ("tool", "config"))
            self.assertFalse(alter.call_args.kwargs["nullable"])


if __name__ == "__main__":
    main()
