# 后端开发指南

本文件适用于 `backend/cike_nexus/`。同时遵循 [根目录 AGENTS.md](../../AGENTS.md)；详细开发说明见 [README.md](README.md)。以下相对路径以本目录为基准。

## 环境与常用命令

- Python 要求为 `>=3.14`，以 `pyproject.toml` 和 `.python-version` 为准；依赖通过 uv 和 `uv.lock` 管理。
- 下列命令的工作目录均为 `backend/cike_nexus/`。不直接修改虚拟环境或锁文件来绕过依赖声明。

| 命令 | 用途与边界 |
| --- | --- |
| `uv sync` | 同步项目依赖 |
| `uv run fastapi dev main.py` | 启动本地开发服务；需要可用的环境配置 |
| `uv run fastapi run main.py` | 启动服务的生产运行模式；不等于获得部署授权 |
| `uv run alembic revision --autogenerate -m "描述"` | 连接目标数据库比较结构并生成迁移；先确认目标环境 |
| `uv run alembic upgrade head` | 执行迁移、修改数据库；须确认授权和目标环境 |

命令清单不是自动执行清单。纯调查、文档改动不要求启动服务或连接数据库。当前没有配置 pytest、后端 lint 或静态类型检查命令，不编造它们；任务需要建立这些能力时再同步依赖与指南。

## 代码导航与分层职责

请求流转为 `Router → Service → Session/Entity`，对外数据通过 DTO 表达。

| 位置 | 职责 |
| --- | --- |
| [main.py](main.py) | 创建 FastAPI 应用、注册路由前缀和标签 |
| `src/cike_nexus/routers/` | 方法、路径、参数绑定和响应契约，转发给 Service |
| `src/cike_nexus/applications/<module>/` | 业务规则、查询、校验和写入 |
| `src/cike_nexus/dtos/<module>/` | 入参与出参模型，不直接把数据库实体当公共契约 |
| `src/cike_nexus/data/entities/` | SQLModel 表实体 |
| [FullAuditedEntity.py](src/cike_nexus/data/abstracts/FullAuditedEntity.py) | 审计实体与软删除基类 |
| [FullAuditedDto.py](src/cike_nexus/dtos/FullAuditedDto.py) | 审计 DTO 定义及 ID 序列化意图；已知限制见下文 |
| [DbContext.py](src/cike_nexus/data/DbContext.py) | engine 与 `get_session` 会话依赖 |
| `src/cike_nexus/data/value_objects/`、`src/cike_nexus/data/enums/` | 值对象与枚举；先核实当前存在的定义 |
| `src/cike_nexus/utilities/` | 通用工具，例如密码哈希 |

- Router 不承载业务规则或提交事务。通过 `Annotated[XxxService, Depends(XxxService)]` 注入服务。
- Service 的会话依赖来自 `DbContext.get_session`；参数类型应是 `Session`，不能把模块对象当作类型或依赖类。
- import 后确认拿到的是类还是模块，尤其是从包直接导入 Service 的情况；不要复制已有错误注解。
- 新增模块按 `dtos/<module>/`、`applications/<module>/`、`routers/<Module>Router.py` 对齐，并在 `main.py` 注册实际路由。
- 类文件采用与类名一致的 `PascalCase`，方法和字段沿用 Python 的 `snake_case`。为字段和业务约束写清楚含义，不为明显代码重复解释。

## 领域规则与既有决策

- 涉及领域命名先读 [CONTEXT.md](CONTEXT.md)。业务实现按对应规格核实，不从表名猜业务语义。
- 部门任务阅读 [部门 CRUD 规格](docs/specs/department-crud.md) 和 [ADR-0001](docs/adr/0001-parent-id-zero-as-no-parent-sentinel.md)。规格中的实施步骤、历史环境状态和验证结论不代表当前实现状态。
- 部门的已确认语义：`parent_id = 0` 表示无上级，不是真实的部门记录；`0` 不是合法部门 ID；部门树可以有多个顶级部门，不能取第一个节点当唯一根。
- 同级重名、移动防环、删除前置条件、排序和错误映射等完整规则查规格，不在这里维护第二份规则全集。
- 不为改变上述哨兵语义而修改 MySQL SQL mode，或擅自改成真实根记录／`NULL`。

## 实体、DTO 与数据约定

- 新增实体前核实已有审计基类，按是否需要软删除选择继承；不要重复定义审计字段或假定基类已正确自动填充它们。
- 适用软删除的业务置 `is_deleted=True`，默认业务查询过滤已删除数据。是否允许读取已删除详情、恢复或级联操作由该功能的明确契约决定；规格内部冲突先说明。
- 实体字段用 `Field(description=...)` 标注中文含义；字符串长度按需求显式限制，大整数主键和关联 ID 使用 `sa_type=BigInteger`。
- DTO 应使用有效的 Pydantic 模型表达验证与序列化；审计 DTO 当前存在缺陷，复用前核实，不把普通类的字段注解当作生效的模型验证。
- 已约定字符串的 ID 必须在真实 JSON 响应中验证，不只检查 Python 注解或装饰器。不要未经任务授权调整用户接口的既有返回类型。
- 时间默认值应在每条记录创建时求值，而非模块导入时固定一次；创建与更新的自动赋值机制必须实际核实。
- 跨实体查询和关联优先沿用项目的显式关联表与 Service 查询方式，不默认引入新的 ORM 关系或 Repository 层。
- JSON 配置落库前核实对应值对象、枚举分派、验证和序列化方式；读取时保持类型语义，不将任意 dict 当作已验证配置。

## 会话、事务与错误处理

- `DbContext.get_session` 管理会话的创建和关闭，当前不提供自动提交的工作单元。
- 现有用户新增在 Service 内显式执行 `add`、`commit`、`refresh`。新写操作应明确事务边界，避免一个业务操作被拆成多个部分成功的提交。
- 事务异常不得继续当作成功返回；如果需要继续使用同一会话，应先正确回滚。不要为局部需求引入另一套会话管理。
- 业务校验失败通过 `HTTPException` 表达，状态码和提示按功能契约选择，不把所有错误统一包装为 `200`。
- 密码处理复用 [PasswordHasher.py](src/cike_nexus/utilities/PasswordHasher.py)。公共 DTO 不输出明文密码、摘要或内部凭据，错误和日志也不得泄露这些内容。

## Alembic 迁移与配置

- [alembic/env.py](alembic/env.py) 使用 `SQLModel.metadata`。实体必须在比较结构前实际导入，文件存在或包级 `import *` 不保证表已进入 metadata。
- 修改实体时核对真实导入链、迁移历史和目标数据库。不机械规定新增实体一定修改哪个 import 文件；以 metadata 是否完整为准。
- 生成迁移优先使用项目的 autogenerate 流程，并审查每个操作。实体缺失或未导入可能让现存表被判为待删除，不能直接执行这类产物。
- 不为完成局部功能恢复用户主动删除的实体、接受意外删表／删列，或夹带无关建表；遇到结构差异先明确来源和任务范围。
- 已在共享环境执行的历史迁移不直接重写，后续结构变更通过新迁移表达。检查升级顺序以及降级的数据影响，不未经授权执行降级。
- 应用 engine 从 `SQL_CONNECTION_STRING` 环境变量读取连接配置；Alembic 从 `alembic.ini` 的 `sqlalchemy.url` 读取。两者不是自动同步的，切换数据库时分别核对且不要输出实际凭据。
- 百分号转义按使用位置区分：URL 编码与 Alembic／ConfigParser 的转义不是同一件事，不将 `.env` 中的 `%` 一律改成 `%%`。

## 验证与已知限制

- 接口／DTO 改动验证真实 HTTP 状态码和 JSON；业务改动验证正常路径、校验拒绝及状态变化。接口测试应使用隔离数据库，不默认连接业务库。
- 模型／迁移改动检查 metadata 完整性、生成差异、迁移顺序及存量数据影响；只读源码不能证明迁移可执行。
- 有测试基础设施后优先运行与改动相关的检查。新增基础设施先适配项目依赖和数据库约束，不直接照搬规格里尚未实施的测试方案。
- 以下为需要复核的现存缺口，不是可复制的规范：`AuditedDto` 未继承 `BaseModel`；审计时间默认值与更新赋值未完整落实；用户查询仍是占位；用户 Service 的会话注解和路由依赖导入需要核实。
- 当前实体文件、迁移历史与文档可能处于不同步状态。每次迁移相关任务重新核对工作区，不从历史规格推断所有表已登记或结构已对齐。
- 若缺少数据库配置、访问权限或依赖，报告实际检查结果及未验证范围。不得把编译、源码阅读或孤立函数检查描述成接口运行通过。
