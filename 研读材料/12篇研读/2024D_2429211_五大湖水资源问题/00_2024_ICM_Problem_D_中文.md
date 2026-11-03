> 2024 ICM Problem D：Great Lakes Water Problem

# 五大湖水资源问题

## 背景（Background）

美国和加拿大的五大湖（Great Lakes）是世界上最大的淡水湖群。这五个湖泊以及相互连接的水道构成了一个巨大的流域（drainage basin），其中包含这两个国家的许多大型城市区域，气候多样，天气条件具有局地性。

湖水被用于许多目的（渔业、休闲娱乐、发电、饮用、航运、动植物栖息地、建筑、灌溉等）。因此，众多不同的利益相关方（stakeholders）都对流入和流出湖泊的水的管理抱有利益关切。特别是，如果从湖泊中排走或蒸发的水太少，就可能发生洪水，沿湖岸的住宅和商业设施将遭受损失；如果排走的水太多，大型船舶就无法通过水道运送物资、支撑地方经济。主要问题在于调节水位，使所有利益相关方都能受益。

每一湖泊的水位取决于进出该湖的水量。这些水位是温度、风、潮汐、降水、蒸发、水深测量（bathymetry，即湖底形状）、河流流量与径流、水库调度政策、季节周期以及长期气候变化之间复杂相互作用的结果。在五大湖水系的水流中有两个主要的调控机制——位于苏圣玛丽（Sault Ste. Marie）的苏闸（Soo Locks）补偿性工程（Compensating Works）（三座水电站、五座通航船闸，以及位于急流上游的一座带闸门的大坝），以及位于康沃尔（Cornwall）的摩西—桑德斯坝（Moses-Saunders Dam），如附录（Addendum）所示。

尽管这两座控制坝、许多河道与运河以及流域内的水库可能由人类控制，但降雨、蒸发、侵蚀、冰塞（ice jams）以及其他水流现象的速率却超出人类操纵的范围。地方管辖区的政策可能产生与预期不同的效果，水域的季节性和环境变化也是如此。这些变化又反过来影响该地区的生态系统，进而影响湖中及湖泊周边动植物区系（flora and fauna）的健康，以及生活在该流域内的居民。尽管五大湖似乎具有规律的年度模式，但水位较正常值偏离两到三英尺（two to three feet）就可能显著影响某些利益相关方。

这个动态网络流（dynamic network flow）问题是“棘手”（wicked）的——由于相互依赖、复杂的要求以及内在的不确定性，它异常难以求解。对于这些湖泊问题，我们面对的是不断变化的动态过程以及利益相关方之间相互冲突的利益。

更多信息请参见 D 题附录（Problem D Addendum）。

## 要求（Requirement）

国际联合委员会（International Joint Commission，IJC）请求贵公司 International network Control Modelers – ICM 提供支持，协助对直接影响五大湖水流网络水位的控制机制（两座坝——如附录所示的补偿性工程与摩西—桑德斯坝）进行管理与建模。你的 ICM 主管已让你们的团队牵头开发该模型以及实施该模型的管理方案。你的主管指出，有几项考虑可能有助于达成这一目标，首先要为五大湖以及从苏必利尔湖（Lake Superior）到大西洋（Atlantic Ocean）的连接河流流量建立一个网络模型。你的主管提到的其他一些可选考虑或问题包括：

- 确定五大湖在一年中任何时候的最优水位，同时考虑各利益相关方的意愿（对每个利益相关方而言，成本与收益可能不同）。
- 依据湖泊的入流与出流数据，建立使五个湖泊维持最优水位的算法。
- 理解你的控制算法对两座控制坝出流（outflow）的敏感性（sensitivity）。给定 2017 年的数据，你的新控制方案能否为该年各利益相关方带来令人满意或优于实际记录水位的结果？
- 你的算法对环境条件变化（例如降水、冬季积雪、冰塞）的敏感性如何？
- 将你的深入分析仅集中于影响安大略湖（Lake Ontario）的利益相关方与因素，因为近期对这座湖泊水位管理的关注更多。

IJC 还关心你使用哪些历史数据来为模型提供依据并确定参数，因为他们很想比较你的管理与控制策略与以往模型的差异。请提供一份一页的备忘录（memorandum）给 IJC 领导层，说明你模型的关键特征，以说服他们选择你的模型。

你们的 PDF 解答总计不得超过 25 页，应当包含：

- 一页的摘要页（summary sheet），在问题的背景下清楚描述你解决问题的方法以及你从分析中得出的最重要结论。
- 目录（Table of Contents）。
- 你们的完整解答。
- 一页的备忘录（memo）。
- 参考文献列表（Reference List）。
- AI 使用报告（AI Use Report）（若使用）。

注：完整的 ICM 提交没有具体的必需最小页数。你最多可使用总计 25 页来呈现你全部的解答工作以及你想包含的任何附加信息（例如：图、示意图、计算、表格）。部分解答也会被接受。我们允许谨慎使用 ChatGPT 等 AI，尽管本题的解答并不必需使用 AI。如果你选择使用生成式 AI（generative AI），必须遵守 COMAP 的 AI 使用政策。这将导致需要额外提交一份 AI 使用报告，你必须将其附在 PDF 解答文件的末尾，且该报告不计入你解答的 25 页总页数限制。

## 提供的文件（Files provided）

- D 题附录（Problem D Addendum）——补充背景信息。
- 数据示例（Data Examples）——这些是可能的数据来源。其中一些被用于填充 `Problem_D_Great_Lakes.xlsx` 数据集。这些示例可在 D 题附录第 4 页找到。注：成功构建解答并不要求使用这些示例。
- `Problem_D_Great_Lakes.xlsx` —— 各湖泊入流、出流与水位的相关数据。

## 参考文献（References）（除所附背景数据文件之外）

1. 关于 IJC 管理五大湖流域工作的说明：National Research Council; The Royal Society of Canada. (2006). Review of Lake Ontario-St. Lawrence River Studies. Washington D.C.: National Research Council of the National Academies. 取自 https://nap.nationalacademies.org/catalog/11481/review-of-the-lake-ontario-st-lawrence-river-studies
2. 关于五大湖航运系统的说明：Great Lakes Seaway Navigation System. (2023). 取自 American Great Lakes Ports Association：https://www.greatlakesports.org/industry-overview/the-great-lakes-seaway-navigation-system/#:~:text=Lake%20Erie%20drains%20into%20Lake,in%20elevation%20approximately%20600%20feet

## 附：COMAP 的 AI 使用政策

> 本题 PDF 末尾附有 COMAP《竞赛中大型语言模型与生成式 AI 工具的使用》政策全文（与题目本身无关）。为避免 6 篇重复收录，该政策已统一整理到 `资料\规则\AI使用政策(中文).md`。
