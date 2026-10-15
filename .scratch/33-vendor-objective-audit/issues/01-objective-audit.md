# 目标与学习主线审计（审计记录，不改事实 SSOT）

## 范围、方法与边界

依据用户最新澄清，审计目标是：在不使用生图模型的约束下，尽可能全面吸收 `vendor/huashu-art-motion` 中值得学的精华，再站在既有原语/模仿/创作与空间目标上推进；成果最终应是感性、易读、可判断合理性的可视化，而非以文档为交付。此审计只记录证据、冲突和建议，不改 roadmap/STATUS/代码/旧证据；S1a perception/readability 与 transfer 明确仍未通过。本 ticket 是唯一新增文件。

有针对性地读取 `.scratch/30-vendor-learning-plan-reset/handoff.md`、当前 STATUS、空间模型/roadmap/method、active-work、31/32 exercise records、vendor 指定文档及相关 `rig.js` / `motion.js`；枚举 vendor references / scene / engine lib 内容后仅读相关文件；检视 `figure_scaffold.py` 当前差异及 compose runner。未运行 vendor、生成图像、模型或供应商服务。仓库初始已存在 staged `.gitmodules`、vendor additions 以及大量其他 dirty/untracked 内容；本审计没有写它们。

## 1. 用户确认目标与现计划：相合处及偷换处

**仍相合：** spatial-model 的最终能力（可识别、位置大致正确的组件化人物；2D artwork 在 3D 支持面；实际深度算可见性；文本/代码输出、无生成资产）并未被用户撤销。roadmap 的紧凑语义规则、真实使用先于抽象、结构/线/着色分层，也都可服务于“吸收范本后继续原项目”。用户指出手、头发、下半身和非法相交的问题，与其强调可视化可读性、真实遮挡不能掩盖穿模完全一致。

**偏差：** 当前计划把“学习范本”收窄成有限的 ribbon/S1a 教学材料，再按旧 S1a→S1b 继续走；roadmap 的静态构图原则被接受，动画、节奏、运动语法被整体延期/排除。用户最新明确说尽可能全面吸收所有值得学的精华，且不自动排除所有动态思想；静态绘画与可迁移运动构造应分别审查。因此不应把“动态/非静态”当成一刀切排除，而要剔除只有视频制作才有意义的端到端设施，保留能帮助形体构造、运动验证或可视化叙事的机制。

roadmap 将“artifact review”“perception/readability”“transfer”分开，这点合理且不得混淆；但把独立接受的 S1a code/method teaching artifact 描述为“Delivered”，容易与阶段名 S1a 混淆，尤其 STATUS/active-work 当前 `Next task` 仍为 roadmap 的 S1a，和 handoff 又说“continue bounded vendor code/method learning”并列，未定义该 work 与正式 S1a 的边界。用户说学习板“没明显问题”不等同正式 S1a 全门通过。S1a perception/readability、transfer 未通过这一事实必须保留。

交付定义偷换：31 是文字教学卡，32 是两张双视角构图渲染，但现计划把继续代码/方法学习产物作为 next task；用户本次明确最终交付应为可感知 visual，而不是文档。ticket/教学说明可以佐证，不可替代可判断的新画面。

## 2. Vendor 学习覆盖地图

方法“覆盖状态”判据：仅在 repo 可核到实现/差异/结果时记为已试；路线图引用或文字解释记为仅引用；当前实现无该能力为未学；用户/项目边界确实冲突才记排除。供应商自称 QA/35 配方不能视为本项目已学会。

| 可学方法 | 具体位置 | 对本项目的迁移价值 | 本项目证据/状态 |
|---|---|---|---|
| 语义场景/骨架与外观 renderer 分离；可复用锚点、身体局部变形、IK、taper | `references/04-纯代码绘制.md` §工程/角色；`scripts/engine/lib/rig.js` 的 `R.ik2`、`R.taper`、`RIG.girl`、`G.A` | 把姿态/附着参数从画法分开；可转成空间支架上的 limb/joint constraints，先让手臂与手形成连续肢体，再选2D外观 | roadmap 仅引用 separation。Ex32 的 `compose.py` 仅把两个既有 ellipsoid 绕肩旋转，未引入 IK、taper、锚点/关节 rig 或 renderer 分层。对本项目能力而言仅引用、未实学。
| 部件语义插槽、画序/遮挡线与材料处理接口 | `rig.js` `GIRL_ORDER` / `drawGirl` / `visibleLines` / hooks；`04` §角色 | 让手、袖、裙、发束的结构归属和线条责任明确；语义边界而非 mesh 全边 | 只引用“线条后做”总体原则；S1/S2 结构尚未到此能力，无迁移实现。可学的是语义插槽思想，不是其 2D 全局画序作为空间 visibility。
| 先做真实范例，再以多次成功用例提炼共用 API；保存失败、用不友好例子试接口 | `07-正面经验.md` §23–25；roadmap learning unit | 降低过早抽象风险，并检验接口能否处理手/头发接触、跨比例变化 | 31/32 的 exercise 形式与对照/限制仅部分引用此原则；32 只有同一旧 scaffold 两种姿势，尚非第二种独立真实构造用途或 API 迁移证据。
| 视觉母题、焦点/形状节奏、场景固定锚点；“场景骨架 × 每幕活画” | `02-机制.md` §1–3；`07` §1/5/31 | 固定观察锚点以比较结构变化；母题启发组件身份、局部节奏。运动可作为检查动作能否读懂的工具，不等于必须做影片 | roadmap 引用静态焦点/剪影，但没有视觉对照产物证明吸收。动态做法整体列为 defer/outside，尚未区分可迁移构造法与视频专属编排。
| 以绘画材料的实际生成过程构造 renderer；区域色板、不同语义区域的绘画规律 | `04` §五层/renderer 表；`07` §6–10；`lib/paint.js` | 后续结构成立后，能把区域身份、材质和造型理由变成可解释画法，而非噪声/逐像素拟合 | roadmap 写 defer 到 S3a；无当前 artifact 学习证据。作为顺序候选而非已吸收。
| 参考实现/姿态数据/轮廓测量、AI 角色帧或 sprites | `04` §角色、`07` §20、SKILL 生成角色线 | 某些细节可能读得准，但不是当前合同允许的产物/坐标来源方式 | 长手填轮廓和生成 sprite 明确违反已确认约束，属于排除；参考只可教学，不成为 runtime geometry。不是因其不值得，而是边界排除。
| painter-order 线稿提取与角色全图可见线 sentinel | `rig.js` `R.visibleLines`；`07` §16 | 可启发验证“被挡线是否误穿”或后处理线语义 | 其核心是2D同层绘制的可见线差分，不等同项目要求的独立曲面深度；不迁移算法本体。未学/当前不适用。
| 时间→数值纯函数、连续时间动作、动作响应/姿态过渡 | `scripts/engine/lib/motion.js` `MO.seg/anim/step/spring/settle/float/lagged`；`02` §2；`07` §3/12–14 | 用动作使“手接触何物、发束如何响应、坐姿受力/平衡”显性化；短姿势序列可测试构造约束，不必输出视频 | 本地只在 Ex32 固定角度变形，未采用时间函数、弹性/连续动作、反馈关系。motion.js 说明时间接口，roadmap 对 animation/beat-grid 过宽地全排除；应挑选构造验证有用部分。
| 全片 beat、转场、帧差、渲染性能、口播、音频、生成图 | SKILL、`02` §4–5、`04` §工程、`07` §17–19/33–38、engine render pipeline | 特定视频/交付任务才有价值；多数不能增进静态人物结构接受 | 当前目标不是视频/配音成片，无必要迁移的部分可以排除；未调用供应商/生成服务。确定性、分层缓存等通用工程点未来按真实需要再判断，不等于现阶段需复建整套引擎。

其他已枚举但未读的 vendor scenes / 风格配方数量多，不因枚举即纳入学习；本表覆盖指定机制以及已读的必要 rig/motion 源码，不宣称逐文件吸收 vendor 全部内容。

## 3. Ex31/32 实际新增能力与覆盖盲点

**Ex31** `.scratch/31-s1a-teaching-artifact/spec.md` 是不改代码的链接型教学记录：整理 `ribbon_family.py` 语义参数→连接 UV 条带→support/depth 的接口，引用 case/测试和已记录失败/限制。其 `spec` 明说只证明 construction/interface、不是 viewer/learner 能读懂或复现；未证明新能力，也未达到 S1a 可读门。现有 “独立 artifact accepted” 不能扩张为正式图像可读性或 transfer。

**Ex32** `.scratch/32-s1b-composition/work/compose.py` 从 `scripts/figure_scaffold.py` 动态 import scene，输出旧姿态的两个相机和把 right arm + hand 一起绕肩转 38° 的同相机输出；改动发生在投影前的世界坐标，继承旧的 `visible_fragments`，没有新的部件/构造模型、无人工可见范围。它证明一种旧场景可以受参数变换重新渲染，不证明新构造方法、人物可辨、姿态合理/附着健全或 vendor 迁移。

旧资产占绝大部分：几何来源是 `figure_scaffold.py` 的 ellipsoid 身体、头发 sheet/fall、裙/lap、bow、hat/eyes 与 continuous ribbon；32 仅在新 runner 复用全部这些对象并变右臂/手角度。虽然 log/spec 清单称有 `hand`，用户观察仍指出手缺失/穿裙或与身体关系不成立；“部件名存在”不等于渲染后可读手。头发仍为静态两面 sheet 与独立 hair-fall ellipsoid；没有随手/头/肩运动的发束响应约束。裙/lap 是白/深色椭球的重叠，用户看成“下半身白球黑盘”，表明参数化部件不是可读的人体/衣物表达。

本轮对 `figure_scaffold.py` 的实际代码差异：提取 `HEAD_CENTER` / `HEAD_RADII` 常量，并把 hair-sheet root 的 z 从旧常量/曲线计算改为头椭球表面公式，再令其沿 u 线性插值到旧 z 曲线；增加“root 在椭球面”数值测试。此处改的是后端几何附着点，非来自已读 vendor 方法的可追溯迁移（不是 rig.js 的局部关节/头发约束），只证明离散根点满足该公式，不证明整条发片与头部/发束连续接触，也不解决手穿头发或响应。没有依据声称它是唯一改动；32 新 exercise runner/evidence 是另一个新增路径。

32 的检查覆盖了 Python tests、渲染成功、文件存在、部件标签、链接、代码编译和深度函数调用；未覆盖用户指出的语义阅读问题：下半身是否读成躯干/裙/腿，手是否清晰且不穿裙，手-头发相交与物理发束反馈，部件是否真实附着，两个表面是真实遮挡还是非法实体相交，静止/变姿势时服饰/头发的因果响应。`visible_fragments` 仅做投影深度比较，深度正确并不判定曲面互相穿透；不能用遮挡正确代替实体合理性。用户反馈实质上是 S1b 可视化本身未达可读性目标，不是继续做旧 scaffold 一个角度补丁的理由。

## 4. SSOT 一致性、过程/门与执行偏差

**冲突和过期事实（具体位置）：**
- STATUS “Next task”明确叫继续 bounded vendor code/method learning；同一段称 S1a code/method teaching artifact delivered；roadmap 标题仍为 “Current next learning milestone: S1a bounded construction-and-teaching slice”，并含具体 deliverable / finite budget。若教学 artifact 已完成，这个 next task 指针过期；若 S1a 仍为现行 milestone，则应明确 teaching slice 与 formal visual gates/其他学习单位的关系，而不是同一 S1a 名称被复用。
- roadmap S1b 仍只定义“accepted components compose seated figure and changed pose”；但 S1a 可读性仍开放时，把此当下一纵向门会与 roadmap 自己的 component gate 顺序冲突。32 spec 声明按 S1b composition 路线开始，使用 S1a component construction/interface 已 accepted 的说法；同文仍声明 S1a readability OPEN。要精确定义可复用的是 API/技术部分，而不是“accepted component”视觉门。
- roadmap vendor table 将 palette/material deferred 到 S3a、motion/beat-grid“outside static drawing objective”；最新 user 反而授权吸收所有值得学且强调原目标继续。此表的边界需要更新/细化，但本 ticket 不擅改 SSOT。
- “visual deliverable not documentation”与 STATUS/roadmap 当前以“代码/教学 artifact 学习”为下一交付的重心不相容。需定义第一个可见可判断的学习产物，再决定说明文档为佐证。

**AGENTS 执行/验收偏差证据与限制：**
- AGENTS 定义 Main 只做用户沟通和 routing，实质 inspection/implementation/review/documentation 必须委派；`.scratch/30.../issues/01-plan-reset.md` 的任务记录将 Main 描述为 user dialogue/routing only，并明确 worker 负责事实文档、fresh reviewer 后续验收。当前不能从现有文件证明谁实际运行了哪些未留痕操作，故不推定身份或笼统指控；但如果 Main 做了 roadmap/STATUS 实质编辑、审查或验证，即违反角色规则，按该计划角色合同必须由 worker/reviewer 执行。需要复核其 author/操作记录，而不能将 parent 的汇总表述当作作者证据。
- 30 ticket 写“Main retains user dialogue/routing, but does no substantive…”并记录 reset 的具体事实文档变更，也记录独立 reviewer 为 post-edit 必须；这是满足分工的书面意图证据，不足以核实全部实际执行者。
- `31` 文本明确 review of teaching artifact ≠ formal readability/transfer，遵守了分门原则。32 log/spec 也承认 independent recognition/pose/front-back review pending、S1a readability open、transfer UNRUN；但“已开始 S1b”及已实现 pose-variation 如果被当作 milestone PASS 就是越门。当前文件并未声称视觉通过；用户意见进一步否定其可读性。没有找到本次 32 独立视觉验收记录；exercise record 把 review pending 作为剩余条件，不能由自测覆盖。
- 按 AGENTS ticket 是历史/证据家，当前 roadmap/STATUS 是事实 SSOT；仅靠“文档过期”归因不足。上列是可指出的事实冲突/next pointer 与最新目标语义变化，须票据确认后更新事实文件。此审计不是 SSOT 修改授权。
- 31/32 的产物是 code/method board 与技术 scaffold，而用户最终要可判断合理的画面；它们不能充当面向用户的完成交付。S1a/transfer 未过、独立 review 未完成则必须如实保留，不允许文档文字或技术测试晋级。

## 5. 建议的重排与需变更合同

建议明确要求更新 roadmap 的 vendor dispositions / next learning contract / S1b exit criteria，并同步 STATUS 和 active-work 的当前 next pointer；明确旧 S1a 仍 open、transfer UNRUN。不是废弃空间目标，也不盲保旧里程碑顺序：先做一个短的、可感知的 vendor-inspired spatial construction vertical slice，结果反过来决定 S1a component readability 如何补门及 S1b composition 如何重新切片。

建议合同将“吸收范本”定义为逐项判定：静态画法、语义构造/rig、表演/运动验证、渲染材质/质量控制；保留无生图约束；不把视频整片管线做成目标。产品 milestone 每步必须有可视化 artifact 与用户能直观判断合理性的核心问题；教学卡/代码/test 是解释与复现材料，不是替代交付。每个切片分开报告：方法来源和具体变化、旧资产比例/迁移证据、组件可读性/空间关系、合理性（碰撞 vs 遮挡）证据、外部/转移门是否运行。运动先用少量姿势/轨迹对照验证构造因果，不以帧差/运动量指标作为艺术目标。

**可视化阶段提案（需由 Main 在后续授权合同中决定；非本任务事实修改）：**
1. **V1 语义关节小场景（首个新 slice）**：新建简洁、容易读的上半身/侧身局部，语义输入为肩/肘/腕/手目标、袖宽/手掌朝向和附着点；从 vendor `rig.js` 的 IK/taper/anchor 分离方法迁移，但用项目自有空间支持和 depth，不复用旧头发/裙/ribbon scaffold。输出一张静态完成图 + 一个难例（手靠近躯干/头发）+ 关节/附着 wireframe 对照；接受：独立视觉 reviewer 能指出手臂连续、手完整、部件归属/深度；改手目标能重算肘/袖而无坐标补丁；真实物体碰撞另有几何检查，合法遮挡另有深度检查；参照关闭后仍确定性重建。
2. **V2 发束/接触的动态构造对照**：在 V1 结构可读后，从 `motion.js` 纯时间函数/`07` 连续动作原则迁移一条短的头/手动作序列，发束按附着/弯曲规则作响应；交付三姿势 contact sheet 与同一支撑几何的连续构造说明。接受：手不穿头发或标明哪一者接触/遮挡；发束运动具有明确根部固定、受力方向和连续性；改变动作参数不是人工逐帧重绘；动态没有遮挡伪装物体互穿。仅视觉运动检查，不要求电影化节奏/音轨。
3. **V3 坐姿/下半身可读的空间组装**：把已接受的手臂/发束构造用于 torso/pelvis/legs/skirt 的语义 attachment 与支撑，交付 front / 3⁄4 / side 三视图和碰撞/深度诊断并排。接受：独立 reviewer 识别坐姿、裙/腿/手；变化相机/比例后接触仍合理；深度交叠处由遮挡隐藏，真正相交单独失败；保留原 M4j/ribbon 为不同迁移实例，不复制旧白球/黑盘模型。
4. **V4 学习过的方法迁移与旧项目推进**：用经审阅的规则形成一张新的、目标相关可视化，而非进一步装饰旧 scaffold；在关闭 reference 后重新生成，提供好/坏因果对照和文本/code 参数。接受：新方法至少在不同身体部件第二次独立使用后才抽象；旧 S1a 可读门由新实证再判断；reference-free、独立 artifact review 以及独立适用的 readability/transfer gate 各自报告。后续才进入线条、色彩/材质，移用 vendor 的区域 palette/material process。

S1a/transfer 当前门不因此自动通过。此处只是完整方向建议；不得把 stage id/接受标准写成既定事实，直到有后续合同更新。

## 6. 第一项最有价值的新可视化成果

首选 **“一只手臂正确连接到可辨识的手，并在躯干/发束前后关系明确的空间小画”**（V1），而不是继续修旧裙/头发 scaffold，也不是只给 arm-angle 旋转。范围可比全身小，但输出应该是清晰的具象小插图：姿态有意图、手掌/手指轮廓或可读简化手套、肩肘腕连续、袖口与手交界清楚；配一个简短的不同关节目标版本并排。要可看到从 vendor semantic rig/IK 到项目3D支持与真实深度的迁移，不要依赖椭球当手或纯技术线框当最终图。可读的局部先解决用户明确提出“手缺失/穿裙/穿发”的优先问题，同时让真实遮挡、几何互穿和关节构造有明确可判断边界。成功后再扩展头发动态/下半身，避免又从全身旧图堆砌补丁开始。

## 证据索引与审计限度

- 最新授权方向：用户本任务的澄清（本票据首段概括）。
- Reset 与职责/当前入口：`.scratch/30-vendor-learning-plan-reset/handoff.md`、`.scratch/30-vendor-learning-plan-reset/issues/01-plan-reset.md`。
- 当前事实：`STATUS.md`、`docs/drawing/spatial-model.md`、`docs/drawing/roadmap.md`、`docs/drawing/method.md`、`.scratch/active-work.md`。
- 前项产物/检查：`.scratch/31-s1a-teaching-artifact/spec.md`；`.scratch/32-s1b-composition/spec.md`、`log.md`、`work/compose.py`、`evidence/two-view.png`、`evidence/pose-variation.png`。图像由原工作记录的 render 命令生成；本审计没有自行评判图像。
- 本次源差异核对：`scripts/figure_scaffold.py` 的 `HEAD_CENTER/HEAD_RADII` 与 `hair_sheet` root-z 公式；`scripts/tests/test_figure_scaffold.py::test_hair_sheet_root_lies_on_head_surface`。`git diff -- scripts/figure_scaffold.py scripts/tests/test_figure_scaffold.py` 显示前述改动。
- vendor：`vendor/huashu-art-motion/SKILL.md`、`references/02-机制.md`、`04-纯代码绘制.md`、`07-正面经验.md`；`scripts/engine/lib/rig.js`、`motion.js`、`paint.js`。未完整审计 vendor 所有风格配方/scene，亦未运行外部 QA。
- `git status --short` 是审计前 baseline：存在用户/前项 staged `.gitmodules` 和 vendor submodules、多个修改/未跟踪文件。没有 staging 或提交操作；本票据写入后也没有暂存操作。不得将该 baseline 描述为“工作树干净”。
