# A v4 acceptance disposition

## 结论：PASS — 仅当前 A 的有限可读 imitation/art gate

原两个 P1 **均关闭**：领片现在形成可见的颈口包绕与前缘展开；腰部背景色断带消失，衣料连续。当前没有证据支持新增 blocking regression。

**不等于完整 R1 PASS、transfer PASS 或用户接受；也不是允许跳过其余内部 gates 直接投递。**

### 版本与证据

审查对象：`.scratch/35-r1-articulated-study/evidence/A-cloth-construction-v4/`

- Manifest：`0a1e42a46e9f733cd0da82e3acf4f3934a918d4cb67fdfc9421923aa72ec0a12`
- PNG：`07998d71693039294008f7c402ee46ed86a0a43edc8e0c9115a39d7e25284da3`

本轮实际查看完整 `artwork-a.png`、registered `check-a/side-by-side.png` 与 `region-2.png`，读取 source-isolated `v4-qualified-image-observations.md`、独立 `v4-delta-and-sight-validation.md`，再检查公开 spec/freeze 和必要源代码。

哈希、像素及 17 项测试结果**复用独立验证报告，不声称由本轮重新执行**。该报告逐项验证了 manifest 的 16 个文件、PNG 像素对应和 v3→v4 scoped delta。

## Review

- **Correct:** 当前图可读成一件浅色衣物，蓝领围绕粉色颈口展开，胸前有相连的 gather/两瓣 bow，右肩短袖延伸至深色横袖口；不是代码图或 detached geometry。
- **Fixed（先前缺陷已由新候选修复，非本 reviewer 修改）:** 原领型 P1 与腰部断带 P1，关闭证据见下表。
- **Finding:** 无新增 P0/P1。保留原有平面化、松量与连接提示不足的 P2；没有把开放观察中的每个参考差异升格。
- **Merge verdict: OK with notes**，范围仅当前 A 可读 imitation/art gate。

**本轮 scoped delta：No issues found.**

## 原 AC 未变

依据 `.scratch/35-r1-articulated-study/spec.md` “User-visible outcome and acceptance” 及 `work/task-freeze.md` “A: reference-imitation study / Acceptance and user experience”，A 需要是实际 authored drawing，有可辨认的 observed clothing/shoulder correspondence、identity/readability 和有意的图像组织。

此要求不等于全参考复制：不要求完整脸、发型、手、全部皱褶、准确隐藏尾带路径或完整 hem。相反，artist hypothesis 也不能豁免可见衣物身份替换或断裂。以下判断沿用原 adjudication 的这条边界。

## Findings disposition

坐标为完整 400×480 A 的近似 crop-local 坐标；映射到源图需加 `(500,320)`。

| 项目 | 当前 disposition | 当前图像 / source 证据与 AC 判断 |
|---|---|---|
| **原 P1：尖 V 领替代包绕领面** | **关闭** | 约 `(139–279,79–160)`。完整图中，两侧蓝色区域有实际面积从颈侧延伸至前下缘；外缘不再是 Q→E 两根直线形成的尖三角。下方深色 trim 沿左右领面弯曲并在前方接续，粉色颈口位于两侧内缘之间。**可见蓝领包绕与衣物身份对应现在成立**。相较参考仍更规整、opening 更竖直，但不再是先前指出的零前宽尖领替换。`source/family-rules.py:203–214,221–242` 实现完整 outer curve、共享 Q′ 的有限宽 strip；`source/build_a.py:101–117` 绑定两领的共享 support seam。这些解释原因，**通过理由仍是当前 PNG 的实际包绕读法**，不是公式可行或测试数。 |
| **原 P1：waist 绿色断带** | **关闭** | 约 `(133–233,311–350)`。现为淡色横带与接缝，完整图和对照均没有旧版穿透衣物的绿背景楔形；横带上下继续读成布面。`source/family-rules.py:295–303` 当前 outline 包含完整末端截面，使用 `*right[::-1]`，与独立报告确认的 endpoint/coverage 修复一致。不是把 geometry equality 当视觉通过，也不是将旧问题淡化成 antialias。 |
| **bow 平面化、结心小、右翼聚拢提示弱** | **P2 / nonblocking，原判不变** | 约 `(117–273,155–214)`，`region-2.png` 最清楚。右瓣仍像较平的围片，参考卷折更多；但两瓣在小 gather 汇聚，左瓣有向根部收束的回折线，bow 身份和大连接关系仍可读。独立 delta 验证未发现 v4 改动 bow family；当前图也没有新的断接。现有 AC 不要求复现每条折叠线，不能在标准未变时据此重新列 P1。 |
| **长粉带直、窄、动势不同；没有自由端** | **Nonblocking；未知 terminal 不作必修** | 约 `(146–175,180–479)`。带子从 bow 根部向下延续，底端被 crop 截断。参考宽度/斜向动势不同，但当前 teacher 边界只保留 DTI2 局部 interior，DTO2 terminal 未知；不能强制补出参考完整端部或特定遮挡路线。没有新 regression。 |
| **右袖根/腋下边界含糊** | **P2 / nonblocking** | 约 `(294–375,136–305)`，尤其 `(294,207)` 邻域。肩袖大轮廓仍能辨认并延伸至 cuff；没有实际可见脱离或背景裂口。独立观察明确“能读出肩袖的大轮廓”，同时保留 seam 歧义。完整 armhole seam 不是 teacher 已证观察；不能因没有精细 seam 就改变原可读性阈值。物理接合仍由独立结构 gate 负责。 |
| **衣身向下成为长窄斜形、分区与参考不同** | **P2 / nonblocking** | 右缘约 `(299,235)→(229,337)→(196,480)`。修后腰部为连续衣料，tilt/contraction/continuation 可读。参考下部的复杂相邻区域、完整 hem 与隐藏右侧并非当前重建承诺。对轮廓松量的差异可记录，但没有当前身份消失或新断开的证据。 |
| **领边、bow 边、浅褶线与 cuff 的视觉重量不同** | **Nonblocking 风格观察** | 领片粗 trim 与 cuff 实心深带形成层级，内部皱线较淡；这同时保留了参考中 dark trim/light garment 的主组织。既有合同不要求所有边同粗或每条褶线同等醒目。没有发现粗线遮掉关键连接的 regression。 |
| **左 pink / blue band 与主体没有画内连续连接** | **Unknown / 不作 blocker** | 左框约 `(0–82,165–267)`。qualitative presence/contact 与独立 crop-exiting blue band 为当前边界；blue identity、完整 leftward centerline 和隐藏 route 未获源证。不得要求新连线去伪造已知拓扑。 |
| **缺完整脸、长颈、局部头发覆盖不同** | **完整人物部分 out of scope** | `region-1/3` 的独立观察不推断必须补画人物。完整 face/hair/hand 不在 A contract；颈口衣物关系已经按 scoped P1 复查，不能再借人物缺项重开整个 A。 |
| **cuff 技术修复 / 接触证明** | **当前无视觉 blocker；不代替结构验收** | 约 `(332–381,297–318)`。实际仍读成接在袖末端的横向深色带。继承 scoped tests 与 source 验证支持技术 delta，但本报告既不据测试宣布全物理通过，也不因像素不变制造艺术缺陷。 |

## Experience evidence 是否有效

**对本次有限 A experience 判断有效，不再笼统列“正式视觉资格未知”。**

- `docs/drawing/method.md:115–126` 要求 fresh image-only observation 与可核验 sight fact。
- `v4-qualified-image-observations.md` 仅读取指定五图，没有 source、teacher、manifest 或 writer rationale；给出完整图尺寸、两处内部色域和相对位置。
- 独立 validator 对 `(240,120)` pale blue collar 与 `(235,185)` rose bow 的真实像素、局部稳定性和图像对应进行了核验，并确认三个 draft/output PNG decoded pixels 相同。
- 本报告是后续 **scope adjudication**，不是冒充 source-isolated 第一轮观察；该独立观察角色由上述 artifact 承担。17 tests 只支持 source/delta，不提供 art verdict。

没有发现此局部视觉 gate 另缺一种合同明确要求的资格证明。

## Main 仍需优先修的阻断项

**无。** 本次不要求新 engine、新人物范围、新 teacher 循环或为 P2 重开无界修图。

以下是**独立剩余 gates，不是当前 A 视觉 blocker**：

- `task-freeze.md` “Acceptance and user experience” 列出的 source/reference boundary、support/world attachment、physical non-intersection、独立 depth、reference-free reproduction 和 final integration/hash gates，需各自有覆盖最终 revision 的证据；本报告不代审。
- 同文开头仍将 corrected teacher semantic gate 标为 `NOT RUN / NOT PASS`；本次视觉通过不追认它。
- B、heldout compatibility/actual drawing 与用户反馈不在本轮范围，未读取、未判定。
- Main 投递仍受 `spec.md` 的“required internal gates 后展示并暂停收取用户反馈”约束；A 视觉 PASS 不自动满足全部投递条件。