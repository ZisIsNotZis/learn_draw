# Roadmap 重整决策与执行记录

## 目标、依据与权威

用户授权重整路线 SSOT，并要求独立审查。目标是借参考临摹/模仿逐步获得合理、有艺术性的程序化创作能力，最终能无参考原创；范本 `vendor/huashu-art-motion` 中所有值得迁移的非生图方法应系统审查，并与项目既有原语、空间支持面和深度引擎融合。视觉作品和能力是 milestone，文档、引擎、测试仅为手段。不能承诺艺术必达或降低门槛；每个用户交付后的反馈门必须停下等待。

输入：用户任务合同；`.scratch/33-vendor-objective-audit/issues/01-objective-audit.md`（审计与建议）；现存 `STATUS.md`、`docs/drawing/{roadmap,spatial-model,method}.md`、`.scratch/active-work.md`、`.scratch/30-vendor-learning-plan-reset/handoff.md` 和实际状态。覆盖阶段原报告曾只保存到配置输出；在本次后续任务获得该来源前，writer没有 `issues/01-coverage.md` ticket 内容，故原路线稿基于审计及已读源起草而非该报告。当前已从配置输出归档原文到 `.scratch/34-vendor-learning-roadmap-reset/issues/01-coverage.md`，明确标注是后续归档并保留其当时过程陈述；不得追称原票此前已存在。旧 S0→S3事实保留为历史映射，不视为新路线通过。

## 选项与建议

1. 保留旧 S1a→S3 顺序，局部补充 vendor：不采纳，仍把旧技术假设当产品阶段且延续文档/测试主导交付。
2. 暂停绘图直至 S1a/transfer 门解决：不采纳，用户允许继续重整与执行，旧门未过不能阻塞独立新作品学习，但也不能冒称通过。
3. 建立方法覆盖地图 + 由可见纵向作品驱动的重排路线：采纳。保留未通过门作为显式遗留事实；先做小而可判断的人体/关节作品，再逐步扩展、迁移、参考临摹与无参考原创；方法技术顺序由工作包证据自治调整，用户只在可感知交付后反馈。

## 范围/排除

本次改当前事实文档及入口/一致性文字，创建本 ticket 与 vendor 覆盖家、指定输出报告；不绘图、不修 scaffold、不改代码/环境/AGENTS/证据，不运行生图或供应商服务，不提交/暂存，不改 append-only principles，不改历史 ticket。保存所有既有 staged/dirty/untracked 内容，特别 `.gitmodules`、vendor、`.agents/` 与原证据。roadmap 与 coverage map 紧耦合，采用一个 writer 维护一致性；coverage map 是来源/迁移覆盖事实的唯一家，roadmap 只规定产品阶段和执行合同，避免重复 vendor 清单。

## 验收与预算

验收：具体完整路径包含 vendor 方法审查融合、参考模仿、变化迁移、无参考原创；每个阶段有可见作品/能力、源方法、迁移对比/变体、用户观察、独立结构/视觉审查及经验门、依赖复用、范围/非目标、可验证退出条件、风险/不降标备选；三种空间/绘画验收独立；各阶段WP类别、输入输出、独占所有权、并行 seam、集成/审查角色、版本证据、有限尝试/停机重规划、自治边界；近期首个里程碑有可开工任务；历史事实与未通过门保留；pointer一致；链接/差异/哈希验证。

有限资源：文档写作一轮，执行命令均≤120秒；本次不执行绘画或图像审查；末尾记录尚未进行的独立 review/经验审查。后续每 milestone 最多两轮不同结构假设，仍未满足退出条件则停并重规划；不以耗尽预算判通过。实际模态图像审查只对真实渲染作品运行，代码检查不得替代。

## 所有权和权威

本票是历史过程/理由家；roadmap 是目标/路线合同；vendor-learning-map 是供应商方法覆盖事实家；spatial-model 是空间架构；STATUS 是当前观测状态；active-work 和 handoff 仅为入口指针。用户拥有作品反馈门；内部技术拆分、试验和替代由项目在上述目标与标准下自治。路线 writer 独占紧耦合 roadmap/map seam；后续WP每个文件/产物仅一个owner，fresh independent reviewer检查全切片，review不是用户验收。

## 独立审查修复处置与边界

- **首轮 independent review BLOCK 的 P1 接受：** review report 指出 coverage map 遗漏单独 vendored `huashu-design`。map 补入边界受限的 supplementary row，不声称完整评估或迁移；主学习范本仍为 `huashu-art-motion`，不建立UI/product-design路线。
- **首轮 independent review BLOCK 的 P2 接受：** review report 指出 STATUS State 有过时 M3/M4当前态文字。该段已改为历史事实，保留历史基线与当前架构约束。
- **首轮修复后的 independent rereview BLOCK 的 P2 接受：** 报告指出 STATUS 的 `Current experiment` 仍将 S0/S1描述为当前。整段现改为 `Historical S0/S1 technical and scaffold evidence (not current experiment)`，正文各事实统一过去时，并明确这不是里程碑/艺术接受，不删证据；S1a readability/transfer仍 OPEN/UNRUN，Ex32非人物PASS，禁止旧scaffold修补。
- **Coverage依赖缺口收口：** coverage原报告见配置输出而缺少目标issue票。收到来源后，原文归档至 `issues/01-coverage.md`，保留来源地址和原写作时“目录不存在 / output override限制”过程说法，明确本次为后续存档，非事前存在。证据与具体方法盘点以归档报告为据。
- **候选/阶段吸收及R1选择边界：** coverage报告强调不应把手部研究定为唯一/已证最优主线，且静态构图、风格、材质和动态构造都应评价。当前路线把R1明确为一个有界articulated arm/hand/torso纵向试片：它能同时考察局部语义连接、姿态变化与现有support/depth体系，且相对一张完整构图降低首个结构试验的耦合；这是可执行性/诊断价值的项目选择，不是证明hand-first艺术收益最大。R3明确承载静态视觉语法/构图、线色结构与适用的style/material renderer；R2明确承载pose variation、时间响应/连续形变等可迁移动态构造，而非视频制作。coverage map相应记录来源、未学习状态及排除范围。`huashu-art-motion`是主范本；`huashu-design`只作为具体绘画问题相关时的补充参考，不延伸至UI交付学习。
- **review引用与结果：** first review `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/dd5a1c21-e969-4175-9321-70dea317fa65/planning/independent-review.md` = BLOCK (遗漏huashu-design、STATUS旧M3/M4当前态)；first repair记录 `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/dd5a1c21-e969-4175-9321-70dea317fa65/planning/repair.md`；rereview `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/dd5a1c21-e969-4175-9321-70dea317fa65/planning/independent-rereview.md` = BLOCK (STATUS仍标Current experiment)。均为文档review，不是用户艺术验收。
- **Host acceptance 与独立文档review分别记录：** 本工作session可查看的历史记录包括用户/工具交互和两份独立review verdict，但没有 host acceptance rejection事件、原因代码或具体拒绝理由。因此host acceptance rejected 的原因在此证据范围内为 **unknown/unavailable**，不能归因于独立review的BLOCK，也不声称通过。不改runtime、不规避host gate；由授权协调者决定后续门处理。
- 本次按review只修可核证文档缺口，没有改里程碑验收、代码、图像或旧证据；未把任何文档/host gate结果冒充用户视觉门。

## Final consistency proof for this repair

`git diff --check` passed. Relative-link scan over STATUS, active-work, roadmap, map and both issue tickets found no broken links; cross-SSOT assertions confirmed STATUS historical section/no Current experiment heading, active-work and roadmap R1 pointer alignment, explicit R2/R3 subject coverage, palette/material and dynamics entries, and coverage ticket pointer. The archived coverage body was compared with configured `coverage.md` and matched exactly after the provenance wrapper. No drawing/test suite was run (documentation-only scope). Commands were bounded under 120s.

SHA-256 after content edits (this ticket's own digest is reported in the configured final output, avoiding a self-referential hash):
- `STATUS.md`: `a08fd8264f3d53b58816361705342d309344cfd4f14a4900c3e52fa3b9fd6a16`
- `.scratch/active-work.md`: `f7a71cb5b82f8e315aec67b4a359ad5528493814c607aa8915413b7f1c944475`
- `docs/drawing/roadmap.md`: `71a9e35ffad0964add6263f2d78743b3beff3f0633a709d0d7819b870c6d54a5`
- `docs/drawing/vendor-learning-map.md`: `21bb2b2c3fcbc7e33835cf65f2d53572edf1d4ff5f484d434e7a430cdab49ec0`
- `.scratch/34-vendor-learning-roadmap-reset/issues/01-coverage.md`: `97cdc7e6fcaa1fd2e16a6d7d69ea25ba6dc2393abf66b78c393e3281b76d633a`

Staged inventory is unchanged: `.gitmodules`, `vendor/huashu-art-motion`, `vendor/huashu-design`; no task staging or commit. Existing unrelated changes were preserved.

## Final independent-review BLOCK dispositions (R1 execution contract / legacy process wording)

- **Accept P1:** Fresh report `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/633211a0-d62b-474a-a2df-7ed5e14862cd/planning/final-independent-review.md` found roadmap contained only a WP template, not a populated R1 plan. Created `.scratch/35-r1-articulated-study/spec.md` as a task contract only, not implementation. It provides eight filled WPs with precise exclusive paths/owners, semantic fields, dependencies and parallel boundaries, integrator/reviewer roles, source-method selection, authored reference-led art/variants/control, separate geometry and depth reviews, blind actual-image review, user presentation/feedback responsibility and fixed numeric budget/checkpoints. It specifies an actual reference-free held-out drawing task/prompt, not a parameter table; no gate or artwork expectation reduced. `roadmap.md` R1 and `active-work.md` now link directly to that contract; STATUS likewise points to it.
- **Accept P2:** The same review identified `method.md`'s “staged structural proof” pointer and `spatial-model.md`'s “Bounded structural sketch / proof” plus “Validation at each stage” as residual old process. Marked the particular S0/S1 ribbon-sketch→hair/figure→old 2D assembly sequence and old small-VLM procedure as archival, past-tense evidence, not current execution, not art/S1a/transfer acceptance, and not authorization to auto-advance. Preserved spatial support/depth architecture and actual-image/user gate principles. `method.md` now points to the R1 WP contract, labels L1-L6 curriculum/3-fix note historical, and defers current gates/budgets to roadmap/R1 contract. No history or raw evidence was deleted.
- **Host gate remains distinct/unknown:** earlier host acceptance was reported rejected, but accessible prior session evidence had no event or reason code. Cause remains unknown/unavailable, not attributed to this fresh independent review and not a PASS; no runtime adjustment or circumvention.

Revision-bound self-check performed after content edits: `git diff --check`; Markdown local-link scan over STATUS, active-work, method, spatial-model, roadmap, R1 spec and both issues; assertions for exact task-contract pointers, eight populated WP rows, sealed actual-image holdout, historical phrasing, architecture preservation and no residual obsolete headings. An initial assertion expected the exact phrase `report.txt image lists` and failed because the spec expresses this as `report.txt` paths plus “image lists”; this was a verifier wording mismatch, not a document defect. A corrected assertion and complete validation rerun passed. No code/test/render/drawing command ran.

Latest required reviewer artifact: `/home/z/.pi/agent/sessions/--home-z-vibe-learn_draw--/subagent-artifacts/outputs/633211a0-d62b-474a-a2df-7ed5e14862cd/planning/final-independent-review.md`. Its P1/P2 are accepted and addressed above. Fresh independent rereview of these repairs remains outstanding; no document or artwork PASS is claimed. The host acceptance rejection cause remains unknown as described above. Existing staged `.gitmodules`, `vendor/huashu-art-motion`, and `vendor/huashu-design` were preserved; no staging/commit. Final SHA-256 values for all touched facts/tickets are recorded in the configured `concrete-r1-contract.md` report.
