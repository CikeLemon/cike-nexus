# 前端开发指南

本文件适用于 `frontend/cike-nexus-web/`。同时遵循 [根目录 AGENTS.md](../../AGENTS.md)。以下相对路径以本目录为基准；前端目前处于基础组件与脚手架阶段，不假定已有业务页面或后端接入。

## 环境与开发命令

- 使用 pnpm 和 `pnpm-lock.yaml` 管理依赖，不另外生成 npm／yarn 锁文件。
- 技术基础为 Vue 3、TypeScript、Vite、Tailwind v4、Reka UI、`class-variance-authority` 和 `@lucide/vue`；版本以 [package.json](package.json) 和锁文件为准。
- 所有命令的工作目录为 `frontend/cike-nexus-web/`。

| 命令 | 用途 |
| --- | --- |
| `pnpm install` | 安装或同步前端依赖 |
| `pnpm dev` | 启动本地 Vite 开发服务器 |
| `pnpm build` | 执行 `vue-tsc -b && vite build`，检查类型并构建 |
| `pnpm preview` | 本地预览已构建产物，不是部署命令 |

当前没有配置 `test` 或 `lint` scripts，也没有已建立的自动化测试／lint 流程。不要写或调用不存在的 `pnpm test`、`pnpm lint`；任务需要建立这些能力时再更新配置与指南。

## 代码导航与基础约定

| 位置 | 职责 |
| --- | --- |
| [src/main.ts](src/main.ts) | 创建 Vue 应用并导入全局样式 |
| [src/App.vue](src/App.vue) | 根组件入口 |
| `src/components/` | Vue 组件 |
| `src/components/ui/` | 可复用基础组件，目前有 Button |
| [src/lib/utils.ts](src/lib/utils.ts) | 共享工具入口，目前导出 `cn` |
| [src/style.css](src/style.css) | Tailwind 接入、主题变量与全局样式 |
| [vite.config.ts](vite.config.ts) | Vue／Tailwind 插件及运行时路径别名 |
| [tsconfig.app.json](tsconfig.app.json) | 应用 TypeScript 配置及路径映射 |

- Vue 组件沿用 SFC 和 `<script setup lang="ts">`；保持组件文件 `PascalCase` 命名。
- `@` 指向 `src`。调整路径别名时同时核对 Vite 和 TypeScript 配置，避免只有其中一方能够解析。
- 沿用项目配置进行类型检查，不为局部代码另写宽松配置、使用 `@ts-ignore` 或无理由的 `any` 掩盖问题。
- 不将脚手架示例当作已完成业务功能；修改页面前核实真实需求与已有组件。

## 组件与工具复用

- 新建基础组件、工具或交互前先搜索 `src/components/`、`src/components/ui/` 和 `src/lib/`，不要重复实现同一能力。
- Button 等基础组件保留 Reka UI 的语义与交互支持，通过已有 `variant`、`size` 等接口使用，不在业务页面复制整套样式。
- 新基础组件沿用 `src/components/ui/<name>/` 的组织方式；当前 Button 的 [index.ts](src/components/ui/button/index.ts) 提供组件导出和 `cva` 变体，可作为已存在的参考。
- 类名合并使用现有 `cn`。共享入口是 `@/lib/utils`；已有 Button 从 `cn` 包直接导入，不将其视为不同工具，也不为统一 import 做无关重构。
- props、emits 和插槽明确组件契约；基础组件不耦合特定业务请求，业务规则不藏进样式变体。
- 状态尽量局部管理，派生值使用 `computed` 等派生机制，不用多个可变状态复制同一事实；只有实际共享时再提升状态。

## 样式与主题

- Tailwind v4 通过 `@tailwindcss/vite` 接入，样式入口是 `src/style.css`；不要按 Tailwind v3 模板新增无关的 `tailwind.config.js`。
- 主题值位于 `:root`、`.dark`，通过 `@theme inline` 映射为工具类。调整主题时同时核对变量定义、映射及使用方。
- 优先使用语义 token，例如 `bg-background`、`text-foreground`、`bg-primary`，不要在业务组件中重复硬编码主题颜色。
- 沿用已有尺寸、圆角、焦点和禁用状态规则。新增交互覆盖 hover、focus-visible、disabled 和错误状态，并检查深浅主题的可读性。
- 局部样式控制影响范围，不为一个页面覆盖整个应用的基础样式。

## 数据与接口约束

- 接口请求和响应以真实后端契约及相关规格为准，明确字段类型、空值、校验和失败处理。
- 已约定字符串的 ID 全程保持字符串。若旧接口返回大整数 JSON 数值，仅在前端转字符串不能恢复已丢失的精度；需要在明确任务中协调契约调整。
- TypeScript 类型不能代替运行时边界验证；不通过强制类型断言把未检查的外部数据伪装成可靠对象。
- 当前没有已建立的 Router、Store 或统一 API 客户端，不假定存在 Vue Router、Pinia、axios 或拦截器。
- 新增路由、状态管理、API 层等基础能力时先核实需要和现有基础，按任务形成一致方案，落地后更新本指南，不同时引入多套同类机制。
- 不把模拟数据或占位请求描述成真实后端接入，不将服务端密钥放入前端代码或会打包公开的环境变量。

## 交互完整性

- 列表和数据区域按场景覆盖加载、成功、空态、错误和重试，避免用户无法区分“无数据”和“加载失败”。
- 表单包含必填／格式／长度校验、字段提示、服务端错误反馈和提交中状态，防止重复提交；成功后的列表刷新与弹窗关闭行为要一致。
- 需要定位大量条目的场景提供检索或过滤。列表搜索放内容区左上并与列表对齐，右上留给主要操作。
- 检查键盘可达、可见焦点、表单标签和纯图标按钮的可访问名称；对话框保留焦点管理和关闭行为。
- 根据任务检查窄屏布局、长文本和深浅主题；没有建立主题切换能力时，不声称已具备完整主题切换功能。
- 对用户未点名但场景明显需要的能力主动补齐并标明可否决；若涉及新的需求边界，则说明遗漏并确认，不静默省略。

## 验证与交付

- 修改 Vue、TypeScript、样式或构建配置后运行 `pnpm build`，并检查实际输出；纯文档改动核对引用和规则即可，不强制构建。
- 构建验证类型与打包，不证明点击、校验、请求和状态流转正确。交互验证根据任务需要进行，未做浏览器验证必须如实说明。
- 使用浏览器验证时覆盖此次改动的正常和异常路径，并核对控制台／网络问题；不只确认页面能够打开。
- 已有自动化测试后按改动范围运行相关测试；当前没有测试设施时，提供实际验证方式和限制，不宣称测试全绿。
- `node_modules/`、`dist/` 和类型检查缓存不是业务源码，不直接编辑；调整依赖或配置以修正问题，不改生成产物掩盖失败。
