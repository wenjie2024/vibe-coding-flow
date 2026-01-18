### 1. 一句话需求（One-liner）

做一个可复用的 Web 应用：用户粘贴“小古文资料”→系统严格按固定字段生成 Stage1（含三套风格配方、锚点文本、母 prompt、逐格 prompts、海报正文、文字层补丁等）并输出 READY；随后用户用极简指令（A/B/C + 1/2/两张 + 4/6格 + 轻量/快速 或 修字）进入 Stage2，只输出**一个 Markdown 代码块**内的最终可投喂 prompts，且遵守“中文零错误 + 叙事一致性零偏差”的硬规则。

---

### 2. 背景与动机（Context & Motivation）

* 你已经把“小古文 → 连环画+海报 prompts”沉淀成一套非常严格的 Gem Instruction：字段固定、锚点锁死、两阶段交互、返工可控。
* 你希望把这套规则做成可复用的 Web 工具，解决：

  * **输出结构不稳定**（字段缺失、格式漂移）
  * **中文错误不可控**（错字/标点/字体/排版）
  * **串格/换序/方向反**（叙事一致性问题）
  * **返工成本高**（不能局部强化、不能只重文字层）
* 优先级明确：**中文准确性 > 可读性 > 版式稳定 > 画面美感/创新**，且严格只读用户提供资料，不引用外部信息、不编造出处。

---

### 3. 目标（Goals）

* G1：Stage1 输出字段完整且字段名不变，满足“只输出以下字段”的结构约束，完整率 ≥ 99%。
* G2：锚点文本 100% 可复现：`TITLE_EXACT / SOURCE_EXACT / CAPTIONS_EXACT / PARENT_POSTER_TEXT_CHINESE` 在 Stage2 默认不可变（除非强制改格数）。
* G3：CAPTIONS_EXACT 与【原文】逐字逐标点一致（含全角标点、换行规则），抽检准确率 ≥ 99.5%。
* G4：Stage2 Render Mode 严格：**只输出一个 fenced code block（```markdown）**，无任何额外文字；P95 响应 < 3s（不含外部模型调用）。
* G5：显著降低串格/方向反：对命中方向词典的格子强制 Motion Vector + Anchors + 1 条反向禁止项；叙事顺序严格硬绑定。

---

### 4. 非目标（Non-Goals / Out of Scope）

* 不在 MVP 内直接调用绘图模型生成图片/拼版出图（先把 prompts 生产闭环固化）。
* 不做外部资料检索、自动补充作者生平/年代/典故（严禁引入外部信息）。
* 不做任意格数：图1 只允许 **4格(2×2)** 或 **6格(2×3)**，不支持 5/7/8 格等。
* 不做自由编辑器式的可视化排版（拖拽文本框/分镜编辑）；返工通过指令与规则强化完成。

---

### 5. 用户画像与使用场景（Users & Scenarios）

* 用户画像

  * 家长/内容创作者：要“可复制、可控、可修字”的 prompts，用于孩子背诵与亲子讨论。
  * 语文老师/教培编辑：更在意中文零错误、可批量复用、规则一致。
* 使用场景

  1. 粘贴资料 → Stage1 一次产出全字段 → 复制去绘图工具出图。
  2. 输入 `A+1` 直接拿到图1最终 prompt（含母 prompt + panel prompts）。
  3. 输入 `A+1+6格` 强制 6 格并重切分 CAPTIONS，仍保持标题/出处与海报正文不漂移。
  4. 输入 “修字/文字层/重文字” → 只拿 `TEXT_LAYER_PROMPT` 后期叠字修错。

---

### 6. 用户故事（User Stories）

**P0**

* 我想粘贴小古文资料并生成 Stage1，输出字段名与顺序固定，末尾带 READY 指引。
* 我想用 `A/B/C + 1/2/两张` 进入 Stage2，系统只输出一个 markdown 代码块内的最终 prompts。
* 我想强制 `+4格/+6格`，触发“格数重置权”：重切分 CAPTIONS 并重建图1 prompts。
* 我想在错字时输入“修字/文字层/重文字”，只输出 TEXT_LAYER_PROMPT 用于后期替换文字层。
* 我想确保图1图内中文只来自 TITLE/SOURCE/CAPTIONS，图2正文只来自 PARENT_POSTER_TEXT_CHINESE。

**P1**

* 我想支持“容错输入”（如“风格1/画图1/6格”），系统自动映射到 A/B/C 与 +4格/+6格。
* 我想看到 Panel Count Decision 的逻辑链与结果（Panels/Layout）并可追溯。
* 我想一键复制 Stage2 代码块与导出 JSON（用于流水线/批处理）。

**P2**

* 我想保存与复用常用风格配方与版式偏好（Image1 Mode / Poster Layout 默认值）。
* 我想对不同版本（A/B/C、4/6格、轻量/完整）做差异对比与回滚。

---

### 7. 功能需求（Functional Requirements）

#### 模块 A：输入解析与数据源锁定（P0）

* A1 资料输入（Markdown/纯文本）

  * 输入：用户粘贴资料
  * 处理：识别【原文】为唯一权威文本；识别标题/出处/释义解析拓展段落（缺失可占位）
  * 输出：标准化 `SourceMaterial`
  * 异常：缺少【原文】→阻止 Stage1，提示必须包含【原文】
* A2 “只读用户资料”约束

  * 处理：所有输出内容仅基于输入资料重组表达；禁止外部检索与编造出处/生平

#### 模块 B：Stage1 固定字段生成器（P0）

> Stage1 必须 **只输出以下字段，字段名不得增删**：

* `Style Recipes`（3个，每个含 7 子字段）
* `Selected Recipe`（默认=候选1 Recipe Name；不输出 No. 编号）
* `ReRender Hint`（固定句式：A/B/C + 1/2/两张；+6格/+4格示例）
* `Panel Count Decision`（逻辑链文本）
* `Panels`（4 or 6）
* `Layout`（2x2 or 2x3）
* `TITLE_EXACT`
* `SOURCE_EXACT`（无出处必须为“出处：无”；若标题缺失可为“待用户提供”）
* `CAPTIONS_EXACT`（数组；逐字逐标点来自原文；强制改格数需重切分）
* `IMAGE_1_PROMPT`
* `PANEL_PROMPTS`（数组；每格必须含 caption EXACT 与排版指令）
* `IMAGE_2_PROMPT`
* `PARENT_POSTER_TEXT_CHINESE`（四段：重点/难点/拓展/亲子讨论问题）
* `SPOT_ILLUSTRATION_PROMPTS`（1-3条）
* `TEXT_LAYER_PROMPT`（只渲染文字层：图1标题/出处/题签 + 图2四块文字）
* Stage1 结尾追加：`READY: ...`（不加额外解释）

#### 模块 C：格数智能判定与切分（P0）

* C1 Panel Count Decision（升级倾向 6 格）

  * 逻辑链：

    1. 若用户强制“+4格/+6格”→从之
    2. 否则：若分句≥5 或 动作复杂 或 总字数>50 或 起因-经过-结果链条完整 → 必选 6 格(2x3)
    3. 否则选 4 格(2x2)
    4. 当 4 与 6 均可 → 倾向 6
* C2 CAPTIONS_EXACT 切分规则

  * 只能在原文已有标点（，。；：？！）或自然分句处切分
  * 每格尽量短，但必须覆盖全文文意；禁止润色/同义替换/合并/拆句跨格
  * 强制顺序复核：转折词必须落在正确格，禁止提前/延后

#### 模块 D：硬规则引擎（P0）

* D1 图内中文来源限制

  * 图1：仅允许 TITLE_EXACT / SOURCE_EXACT / CAPTIONS_EXACT 出现在图内中文
  * 图2：海报正文仅允许来自 PARENT_POSTER_TEXT_CHINESE（可重组表达但不可引入外部信息）
* D2 字体与排版硬约束

  * 字体：正楷/楷书风印刷体（Kaishu），横排
  * 禁止：竖排、弧形字、透视倾斜字、潦草手写
  * 所有中文必须在干净浅色底框/留白块上，高对比、大字号、舒适行距
  * 禁止最终图像出现英文/水印/Logo/乱码/奇怪符号
* D3 文字稳定条款注入（必须原样写入 prompts）

  * COPY-PASTE RULE 等固定英文条款
  * Panel-to-Text Hard Binding 固定条款
* D4 Global NEGATIVE 顶层一次（只写进 IMAGE_1_PROMPT 顶层）

  * 包含：禁止裁切人物、禁止错误方向、禁止串格、禁止乱序合并拆分、禁止乱码英文水印、禁止文字扭曲等
* D5 Negative 限额规则（V5.4）

  * 不要求每格都写 negative
  * 仅当 caption 命中方向词典：该格必须包含 1 条反向禁止项

#### 模块 E：叙事顺序锁定（P0）

* E1 Panel-to-Text Hard Binding

  * 每格 i 只能表现 CAPTIONS_EXACT[i]
  * 禁止换序/对调/合并两句/拆一句到两格/跳格/借用相邻格内容
  * 若难画：宁可更简单也不改顺序

#### 模块 F：人物出镜全身规则 + 安全例外（P0）

* F1 全身规则（出现身体不止手）

  * 必须全身入镜（头到脚可见），留 5–8% 安全边距
  * 镜头景别锁定：full shot / long shot，禁止 close-up / medium close-up
  * 强调物体可用“前景物体放大 + 背景人物全身”但仍保证头脚不被遮挡
* F2 安全例外：no-person close shot（只手+物体）

  * 仅当 caption 核心是操作/器物细节动词（取/贮/饮/写/系/开/合/放/拾等）
  * 允许 close-up，但不得出现躯干/人脸

#### 模块 G：方向向量锁定（P0）

* G1 方向词典命中时强制输出：

  * Motion Vector（OUTSIDE->INSIDE / INSIDE->OUTSIDE / LOW->HIGH / HIGH->LOW / FORWARD->BACK / BACK->FORWARD / CHASER->TARGET / STATIC FACE-TO-FACE）
  * Anchors：从锚点库任选 1–2（门框/帘子/材质分界/台阶/明暗带/视线重心/追逐距离变化等；禁止每格都模板化门口）
  * 反向禁止项：仅 1 条（防方向翻转）
* G2 Direction Lock 句写入 prompt（松正向，不绑门口模板）

#### 模块 H：Image1 Prompt 生成（P0）

* H1 Image1 结构硬约束

  * Panels 仅 4 或 6；Layout 仅 2x2 或 2x3
  * 顶部标题区（TITLE_EXACT）与出处区（SOURCE_EXACT）必须为浅色底框
  * 每格题签条显示 CAPTIONS_EXACT[i]（逐字逐标点）
* H2 Image1 创新模式（软规则但必须声明）

  * 在 IMAGE_1_PROMPT 开头显式声明：Image1 Mode（A/B/C/D）

    * A：分镜条+小编号①②③④（或①~⑥）
    * B：Recurring Prop
    * C：Verb Focus
    * D：Shot Progression（但人物仍全身；特写仅限 no-person close shot）

#### 模块 I：Panel Prompts 生成（P0）

* I1 每格 prompt 必含“三件套”

  1. Camera（全身 long shot 或 no-person close shot）
  2. Caption EXACT + 文本框位置（浅色题签条，建议下方）
  3. Scene（只画该句一个动作/一个意思，不串格）
* I2 方向命中时额外补充 Motion Vector / Anchors / 1条反向禁止项

#### 模块 J：Image2 海报 Prompt 生成（P0）

* J1 硬约束

  * 竖版 portrait
  * 四类信息齐全：重点/难点/拓展/亲子讨论问题
  * 海报正文严格来自 PARENT_POSTER_TEXT_CHINESE（不带引用标号，不学术腔）
  * 1–3 个同风格小插图，克制不抢字
* J2 海报版式（软规则但必须声明）

  * IMAGE_2_PROMPT 开头显式声明：Poster Layout（1/2/3）

    * 1：三卡片 + 问题栏
    * 2：导图式 Mindmap
    * 3：Checklist

#### 模块 K：Text Layer Prompt（文字层补丁）（P0）

* K1 只渲染文字框 + 文字（纯净背景/透明或浅底）

  * 图1：标题框/出处框/每格题签框
  * 图2：四类信息文字区域
* K2 同样注入文字稳定条款与叙事一致性条款

#### 模块 L：Stage2 Render Mode 指令解释器（P0）

* L1 支持极简指令

  * `A/B/C + 1/2/两张`，可追加 `+4格/+6格/+轻量/+快速`
  * 单独输入：`修字/重文字/文字层`
* L2 支持容错输入（P1）

  * “风格1/画图1/6格”等自动映射到 A/B/C 与 +4格/+6格
* L3 Render Mode 防漂移硬规则

  * 不再重读资料；不改动锚点：Panels/Layout/TITLE/SOURCE/CAPTIONS/海报正文
  * 例外：指令含 +4格 或 +6格 → 启动格数重置权：重切分 CAPTIONS，重生成 IMAGE_1_PROMPT 与 PANEL_PROMPTS
  * 切换 B/C：仅重写风格视觉描述，中文锚点不变
  * 含 轻量/快速：省略 TEXT_LAYER_PROMPT 段落

#### 模块 M：Stage2 输出模板（P0）

* M1 Stage2 输出格式强制

  * 只能输出一个 fenced code block：`markdown … `
  * 代码块外不得输出任何文字
* M2 根据指令选择模板

  * 模板A：Image1（含 IMAGE_1_PROMPT + PANEL_PROMPTS + 可选 TEXT_LAYER_PROMPT）
  * 模板B：Image2（含 IMAGE_2_PROMPT + SPOT_ILLUSTRATION_PROMPTS + 可选 TEXT_LAYER_PROMPT）
  * 模板C：两张
  * 模板D：修字（仅 TEXT_LAYER_PROMPT）

---

### 8. 非功能需求（Non-Functional Requirements）

* 可复现性：同一输入 + 同一指令（含格数/风格/轻量）→输出一致（除时间戳等元信息）。
* 可靠性：字段 schema 校验 + 硬规则校验（中文锚点来源、格数合法、输出模板合法）。
* 可用性：复制友好（Stage2 一键复制代码块），Stage1 字段可折叠查看。
* 性能：Stage1 P95 < 5s；Stage2 P95 < 3s（不含外部绘图）。
* 隐私：默认本地/私有可部署；历史记录可清空；不外发内容（若未来接 LLM/绘图 API 必须显式开关）。
* 可维护性：规则版本化（例如 V5.4 Negative 限额），输出结果携带 rule_version 便于回溯（P1）。

---

### 9. 约束与偏好（Constraints & Preferences）

* 约束（硬）

  * 只处理用户提供资料；【原文】为唯一权威文本。
  * 图1只允许 4/6 格；布局只允许 2x2/2x3。
  * 图内中文必须 100% 正确、楷书印刷体、横排、浅底框、无英文无水印无乱码。
  * Stage1 字段名不得增删；Stage2 只能输出一个 markdown 代码块。
* 偏好（默认）

  * 文本优先版：宁可画面简单，也不牺牲文字与叙事一致性。
  * 默认选中风格 Recipe 1（最稳妥）。

---

### 10. 数据与接口（Data & Interfaces）

* 数据对象（概念）

  * `SourceMaterial`：raw_text + parsed_sections（原文/标题/出处/解析拓展）
  * `Stage1Payload`：固定字段集合（严格 schema）
  * `RenderCommand`：风格(A/B/C) + 目标(1/2/两张) + modifiers（4/6格、轻量、修字等）
  * `Stage2Payload`：模板化最终 prompts（单代码块内容）
  * `RuleSet`：规则版本（含方向词典/锚点库/固定条款文本）
* 接口建议（概念）

  * `POST /stage1`：输入资料 → Stage1Payload
  * `POST /stage2`：Stage1Payload_id + RenderCommand → Stage2Payload（代码块）
  * `POST /revise`：Stage1Payload_id + patch_request（第X格方向/串格等）→ 更新后的 Stage1Payload（或直接 Stage2Payload）
  * `GET /export/{id}?format=md|json`

---

### 11. 验收标准（Acceptance Criteria）

1. Stage1 输出仅包含规定字段（字段名完全一致、无增删），末尾追加 `READY: ...`。
2. 当资料无出处时，`SOURCE_EXACT` 必为“出处：无”，且在图1 prompts 中明确要求显示。
3. `Panels` 只能为 4 或 6；`Layout` 只能为 2x2 或 2x3；任何其他值校验失败。
4. `CAPTIONS_EXACT` 必为数组且每条与【原文】逐字逐标点匹配（含全角标点与换行规则）；不匹配则 Stage1 失败并提示定位。
5. `IMAGE_1_PROMPT` 顶层包含 Global NEGATIVE（只出现一次）与固定“文字稳定条款 + 叙事一致性条款”原样注入。
6. 任一 panel 若出现人物身体（不止手），其 PANEL_PROMPTS 必包含 full-body/long shot 与 5–8% safe margin 等约束语句；否则判失败。
7. 任一 caption 命中方向词典，该 panel prompt 必含 Motion Vector + 1–2 Anchors + 仅 1 条反向禁止项；未命中方向词典则不强制该反向禁止项。
8. Stage2 接收 `A+1` 时，输出必须只有一个 ```markdown 代码块，块外无任何文字；代码块内容符合模板A结构。
9. Stage2 接收 `修字/文字层/重文字` 时，只输出模板D（仅 TEXT_LAYER_PROMPT），且仍包含文字稳定条款。
10. Stage2 接收 `A+1+6格` 时必须触发格数重置权：重切分 CAPTIONS_EXACT 并重建图1相关 prompts；海报正文不改变。

---

### 12. 成功指标（Success Metrics）

* M1：Stage1 一次通过率（无需手工修字段）≥ 80%。
* M2：CAPTIONS_EXACT 与原文一致性错误率 ≤ 0.5%（字符+标点）。
* M3：Stage2 输出格式违规率（非单代码块/夹带说明）= 0。
* M4：方向/串格相关返工率较基线下降 ≥ 30%（以用户反馈或标注统计）。
* M5：修字场景的平均修复时长 ≤ 2 分钟（拿到 TEXT_LAYER_PROMPT 后叠字完成）。

---

### 13. 风险与未知点（Risks & Unknowns）

* R1：输入资料标签不规范导致解析错误（原文/出处/解析混杂）

  * 影响：锚点不稳、海报正文来源不清
  * 缓解：提供输入模板 + 解析预览（P1），MVP 允许占位但不允许编造
* R2：严格“中文零错误”在模型端不可控

  * 影响：即使 prompt 正确，出图仍可能错字
  * 缓解：默认支持“题签留空策略”（只输出锚点供后期叠字）+ TEXT_LAYER_PROMPT 工作流（P0）
* R3：规则文本过长影响可用性/可维护性

  * 影响：prompt 冗长、用户不易读
  * 缓解：Global NEGATIVE 顶层一次 + Negative 限额（已引入），并做规则版本化
* R4：多版本规则迭代导致历史结果不可复现

  * 缓解：每次输出携带 rule_version（P1），并允许选择旧规则回放（P2）
* 实现路径选项（建议写入产品配置）

  * 选项A：全规则化生成（最可复现，表现力较保守）
  * 选项B：规则+LLM 混合（锚点/校验规则化，海报文案/风格说明可 LLM 生成后冻结）
  * 选项C：可插拔（不同项目选 A 或 B），以 rule_version 与 prompt_template_version 固化

---

### 14. 里程碑与迭代计划（Milestones & Iterations）

**V0 (MVP)**

* Stage1：固定字段输出 + 硬规则注入（文字稳定条款、叙事一致性条款、Global NEGATIVE）
* Panel Count Decision（升级规则）+ CAPTIONS_EXACT 切分与校验
* 方向词典命中与 Motion Vector/Anchors/反向禁止项生成
* 人物全身规则 + no-person close shot 例外落地
* Stage2：指令解析（A/B/C + 1/2/两张 + 4/6格 + 轻量/快速 + 修字）
* Stage2：单代码块输出模板A/B/C/D（严格格式校验）

**V1**

* 容错输入映射（“风格1/画图1/6格”等）
* 生成历史与版本记录（含 rule_version）
* Stage1 预览：原文 vs CAPTIONS 对照高亮；方向命中标注
* 导出 Markdown/JSON（schema 校验）

**V2**

* 用户自定义：默认 Image1 Mode / Poster Layout、锚点库偏好、方向词典扩展（版本化）
* 批量处理与对比（同一篇古文生成多风格/多格数的差异对比）
* 可选对接绘图 API（开关式，默认关闭）

---

### 15. 待确认事项（Open Questions / To Confirm）

1. 标题缺失时 `TITLE_EXACT` 你希望输出“标题：无”还是“待用户提供”？（你在规则里对 SOURCE 更硬，对 TITLE 有“不得编造”的要求，需要统一策略）
2. “题签留空策略”的触发条件：默认始终留空，还是仅在用户显式要求/检测到高风险时留空？
3. 方向词典的“命中判定”是纯关键词匹配还是需要更强的语义判定？（影响误命中率）
4. “动作复杂/分句≥5/起因-经过-结果链条完整”的判定口径：是否需要在 UI 中可解释展示？
5. `PARENT_POSTER_TEXT_CHINESE` 的“允许重组表达”边界：是否允许合并句子/换序，但仍保持信息不增不减？
6. `SPOT_ILLUSTRATION_PROMPTS` 是否需要也携带“不要抢字/留白充足”的固定条款？
7. Web 应用部署形态：本地（NAS/内网）优先还是公网服务？是否需要登录/多用户？
8. 规则版本（如 V5.4 Negative 限额）是否需要在输出中显式显示给用户，还是只在导出 JSON 元信息中保留？
