# WP01 — R1 方法/来源选择卡

**状态：**来源研究完成；选择是 WP03 的 provisional implementation input，不是视觉迁移已成功的证据，也不解除 WP03/WP04/后续独立审查门。

## 工作包边界与版本

- 合同：`.scratch/35-r1-articulated-study/spec.md`，R1-01 行。只产出本卡；不画图、不写代码、不运行 vendor、不触碰 WP02 sealed holdout。
- 项目工作树基线 HEAD：`24693d4b764755165509fc206695ebca03ee44fe`（工作树已有其他 dirty/staged 项，保留）。vendor `huashu-art-motion` HEAD：`f178bd7754a71d6d399473af1501634548efa6cb`。
- 深读预算最多 3 源单位：选 `scripts/engine/lib/rig.js`（机制实现）、`scripts/engine/scenes/09_postimp.js`（实际组合用例）、`scripts/engine/lib/rig_huashu.js`（对比的 FK/刚体构造）。不把引文当学习实证。合同指定的 `references/04-纯代码绘制.md`、`references/07-正面经验.md`、`tests/test_capabilities.py`、`tests/test_images.py` 与 coverage issue/spatial SSOT 均作任务所需的定向定位/核对，不扩展为额外深读源码家族；测试内容不相关，详见下文。
- 文本链接均为仓库相对路径，可从 WP 输出所在项目根目录定位。源版本以 vendor commit 与下列 SHA-256 绑定；源码本地存在，本文未运行/vendor 行为未验证。

## 选择与迁移构造规则

### 1) 选用：语义关节锚点 + 二骨 IK 解弯臂，不用刚体旋转作主构造

**来源/机制：** [`rig.js`](../../../vendor/huashu-art-motion/scripts/engine/lib/rig.js) `R.ik2(S,T,a,b,bendSign)`（肩/目标/两段长度/肘侧符号，返回 E、H）；`R.girl` 以语义 shoulder `S`、手目标 `handT` 求 elbow/wrist，并导出 `G.A.shoulder/elbow/wrist/hand`。真实用法见同文件 `R.girl` 的举杯目标插值与 `R.GIRL_ORDER`。独立且更简单的 FK 对照 [`rig_huashu.js`](../../../vendor/huashu-art-motion/scripts/engine/lib/rig_huashu.js) `HS.build`/`arm`：由 shoulder、ua/fa 角生成 elbow/wrist 及 `J` 锚点；姿势由 `HS.pose` 提供角度。

**WP03 具体映射：**肩锚应由躯干/肩部组件关系推出，不在画布补坐标；肘由肩到手腕/掌部目标及上臂、前臂比例规则推出，明确肘弯向；腕锚接掌，手掌/拇指与指根/指尖由局部手形规则派生。目标点对应手与衣领的有意接触关系。衣领接触端作为语义接触锚/关系记录，不据参考手工挪路径点。躯干、袖筒、上臂、前臂、掌/指的轮廓各自在局部 `(u,v)` artwork 上构造，再挂到适当 torso/shoulder/arm support；IK 只给可复现关节锚，不负责支持面绑定、碰撞或可见性。

**保留/改造/排除：**保留紧凑的目标驱动二骨几何与具名锚点概念；改造其输出为支持面局部锚及现有 3D 支持/深度管线的输入，不照搬像素坐标/Canvas 点列。弯臂长度不可达目标时需显式报不可能/受限，不盲信供应商只对上臂+前臂和臂长上限 `a+b-0.01` 的实现；R1不引入完整 IK 系统。

**预期可见变化：**变更目标和一个比例后肩—肘—腕/掌仍是连接的弯臂，肘方向有意，手抵达领口关系随姿态更新，而不是整组手臂连手一起转。**候选失败：**目标不可达、关节链与躯干/领口穿插、接触只在投影近似、支持面扭曲后局部艺术断裂或深度不符。每项由 WP03构造、WP05几何、WP06深度、WP07真实图像门分别验证；本文不宣告通过。

### 2) 选用：端点/中段宽度控制的 taper 作袖筒/肢段轮廓生成器

**来源/机制：**[`rig.js`](../../../vendor/huashu-art-motion/scripts/engine/lib/rig.js) `R.taper(A,B,wA,wB,bulge)` 用两端与中段宽度生成闭合平滑带状轮廓；相邻 `R.smooth` 将稀疏语义点列转曲线。`R.girl` 对 upperArm、foreArm、cuff 分别使用 taper，显示分段的形宽意图与袖口边界。

**WP03映射：**用肩/肘与肘/腕锚作为段端点；宽度参数表达肩端袖笼/上臂厚度、肘收束、前臂/袖口宽度。衣袖外形与皮肤/手部是分开的语义层，袖口接手腕/掌端；躯干肩头轮廓须连接袖窿。局部生成的轮廓先映射到支持面，不能把输出路径当全局平面遮挡方案。可将同一 taper 规则用于袖层，但不把衣袖和裸露手的材料/线责任混为一个形状。

**选择限制：**taper 值得试作紧凑的受控轮廓规则，不代表关节真实解剖、厚度/体积、衣褶、表面法线或实体碰撞。大幅弯肘需要局部内侧折叠/分段美术规则；不能期待两段 capsule 自动连续、无缝、无自交。**预期变化：**肩臂形状随锚/比例一致收放，袖口过渡不靠逐 panel 点修。**失败：**内弯折出尖角/穿插，局部 art 失真，宽度更改导致支持面边界不匹配；复查形状规则，而非补坐标。

### 3) 隔离采用：语义部件与 renderer/线责任分离；不迁移全局画序可见性

**来源/机制：**[`rig.js`](../../../vendor/huashu-art-motion/scripts/engine/lib/rig.js) `R.GIRL_ORDER`、`R.drawGirl` 按部件填色/调用 `pal.paint`，提供 `before/after/hooks` 语义插槽；`visibleLines` 是两种线色渲染差异的像素处理。实用组合样例 [`09_postimp.js`](../../../vendor/huashu-art-motion/scripts/engine/scenes/09_postimp.js)：按 `RIG.girl` 生成姿势，再分别做角色平涂、纹理、最后 `visibleLines` 补线；可见供应商把角色姿态几何与造型/风格绘制分层，但其深度仍是扁平部件画序。文档来源 `references/04-纯代码绘制.md` §1–4、`references/07-正面经验.md` §2、§7–8、§16 是方法主张/经验文字，不是本项目迁移实证。

**WP03/WP04映射：**组件 ID 与线/材料责任应明确分开；衣领作为躯干/服装上的局部艺术部件，肩袖/手可各自指定边界与线责任，样式渲染不反向决定锚、支撑面或遮挡。领口线在手与衣领发生接触处可以成为刻意接触线；最终取舍留给线稿设计，不自动画出所有网格边。

**不迁移：**禁止将 `GIRL_ORDER`、Canvas绘制先后或 `visibleLines` 像素差算法作为本项目支持面深度真值、碰撞证据或 `visible_ranges` 替代品。R1架构要求投影/深度引擎据支持面实际深度决定前后；vendor flat painter order 不能处理空间交叉/沿表面深度变化。可见线算法的白哨兵两次栅格渲染不支持本项目 SVG/矢量可见片段管线，也不能判定实体相交。语义 renderer/style 分离可借鉴，vendor实现隔离。

**预期变化：**服装、皮肤、线稿各有清晰职责，局部服饰可依附语义锚点，结构变化不用把样式重写。**失败：**组件 ID/层级看似正确却深度错、重复描边/接触被隐藏、线边暗示错误空间关系；必须由深度和图像评审独立揭示。

## 反例对照：Ex32旧 scaffold 旋转为什么不够

项目旧 [`figure_scaffold.py`](../../../scripts/figure_scaffold.py) 以椭球组件构造固定几何，示例手臂/hand 是已摆定的 ellipsoid；Ex32 被项目 vendor-learning-map 与空间架构记录为旋转已有 arm/hand 几何对，而非 IK/taper/具名关节/renderer split（此处只采用项目既有事实，非重跑 Ex32）。整体旋转只改变一组既定几何姿态，并未由新 hand target 求 elbow/wrist，不能因手目标、臂长或肘侧变化自动生成一致肢体形状；椭球也不给袖口/手掌局部 artwork 与线责任。WP01新方法至少增加目标驱动的关节链、按姿态生成段轮廓、接触语义锚点及结构/绘制分离这些可测试能力。仍不声称能生成高质量手、解决碰撞或支持面拓扑。

## 测试/负例核查和来源边界

合同指定的 `tests/test_capabilities.py` 是 capability/config/audio 类测试；`tests/test_images.py` 是图像生成授权/收据/导入安全测试。经定向符号检索，未发现与 `RIG.ik2`、`RIG.taper`、肩肘腕锚点、rig/renderer分离或空间深度相关的直接测试/负例；因此**没有可引用的供应商相关测试证据**。不能把这些安全测试或 vendor自述 QA 说成 rig 方法通过证明。`rig_huashu.js` 的 FK弯臂与rig.js的 IK形成有用机制对照，但仍非本地迁移结果。

本次明确不选 stretch/全身非等比形变、刚体分组/`rigidPose`、general hook绘制API、供应商绘制顺序/visibleLines，亦不看 motion、paint 与更多场景/配方：WP01的最小问题是新肩—躯干—弯臂—手—衣领接触，避免把支持面/真实深度替换为供应商的平面系统。是否之后增加须后续WP有具体画面需求，不表示这些方法无价值。手掌/拇指/手指造型并无本卡确认可复用的供应商细分方法；WP03须按接口构造并由后续视觉门检验。

## WP03交接与复核条件

**建议接纳的最小方法假设：**(A) 语义 shoulder→elbow→wrist/palm，由 hand/领口接触目标及弯肘符号驱动二骨锚；(B) taper 用于分段上臂/前臂/袖口轮廓；(C) 组件、pose/几何与风格/线责任分开。support attachment、局部 `(u,v)` artwork、相交与可见性完全留在现有 spatial model/深度引擎职责。若上述假设不能在既有架构有理地表示，交 integrator 重新规划，不可用 painter ordering/像素patch回避。

本卡不选定 hand-first 是最佳艺术题、不冻结数值/参考裁切/相机、不证明目标参考可见性，不授予执行其他WP权限。WP02可并行冻结任务；WP03开始前 integrator须审阅本卡并接受/修订接口。供应商来源只提供有根据的候选构造方法；迁移学习是否发生由后续真实作品和独立证据判断。

## 源版本证据（vendor commit `f178bd7754a71d6d399473af1501634548efa6cb`）

| 路径 | SHA-256 |
|---|---|
| `references/04-纯代码绘制.md` | `b41ba3faf32d24cb020d140ba7c0e95d9ad71462049dff2f390f4a18e532b53c` |
| `references/07-正面经验.md` | `aacda61500b54e767b193815e64363cc3acd6a11ef0274aabadd2947f54f3412` |
| `scripts/engine/lib/rig.js` | `88c4df6dc105cafdc7249a5f31c79928db6c05b372f04e2e0f14059e8620f17f` |
| `scripts/engine/lib/rig_huashu.js` | `6419306bb314f89848b0adf842db0c305c2f6bc931df34388eb5389f29c1d392` |
| `scripts/engine/scenes/09_postimp.js` | `a1806dd4dfbfe32ed9a18e70174750c0e932a2a2beca832be8dc25708c76277e` |
| `tests/test_capabilities.py` | `04ce548d5a72a11a87a3bd85c46a98e13f1aabafb096e3c59a6fc7a20bfdf4ad` |
| `tests/test_images.py` | `5fe7533ec25a2644e3685e1677186eaf1554ebbbcc390fcd56a45afbad872040` |
