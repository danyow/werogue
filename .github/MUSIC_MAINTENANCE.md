# WeRogue 每日一首

这是 www.werogue.com 的音乐收藏站，唯一源码仓库 danyow/werogue，生产分支 master。不要修改 danyow.cn 的仓库。此文档只说明格式，不授权超出用户/任务明确授权的操作。

## 内容边界

- 初始个人歌曲池是 _posts 下15首2020年旧收藏，不是完整收听历史，也不能推断播放频率。新歌需有用户明确提供的收藏/歌单证据，否则只能列为推荐候选。
- 先选未做过每日一首的旧收藏；全部轮过后可明确标记为回看，避免连续同一音乐人。没有值得新增的内容就说明情况，不能伪造。
- 历史原评逐字保留，新短记另写。短评自然口语，60–160字为参考，不要堆文艺套话，不捏造用户经历或无法实际听取的音频细节。生成文本 review_status: generated，不冒充本人亲写。
- 查证曲目版本、专辑、发行日期和署名。优先作者/厂牌官方发布页，保留来源及核对日期；未知留空。收藏日不等于发行日。
- 封面必须匹配具体版本，保留来源与版权说明；不要拿其他封面替代。仅在确实取得图片文件时说已存入仓库，外链不是本地归档。不搬运音频、完整歌词或他人长评，不自动播放。

## 每日文件

使用 `_posts/YYYY-MM-DD-daily-<slug>.md`。必需字段：layout: post；kind: daily；date（含+0800，建议08:00，避免旧站UTC日期显示偏移）；permalink: /daily/YYYY-MM-DD/；title；music；artist（数组）；cover；resource.music与resource.artist（数组）；tags；summary；original_post；original_collected_at；listening_evidence；review_status；sources（label/url/checked_at）。`album`、`release_date`、`credits` 仅填写已核实资料。参考2026-09-18首篇。

一天最多一篇；先查当天记录，重试接续校验，不重发。永久封面墙排除 kind: daily，避免一首歌的多次回看重复占据唱片架。原收藏文件、正文、日期、URL不因每日回看而改写。

## 提交与核验

先读取当前分支和文件SHA；校验YAML、重复、来源和链接。以条件更新/非强制快进提交，冲突重读，不覆盖并发修改。只改每日正文和必要封面/来源记录，不在日常任务中改变主题、域名、工作流、依赖或权限。

提交成功后回读文件、检查对应构建/发布，再打开正式网站的 `/daily/YYYY-MM-DD/` 和首页。排队、已提交、构建成功、公开可访问是不同状态，分别报告。受保护时开PR，不绕过审批。失败保留原稿和commit，下一次接续，不能声称已上线。

## 主题与安全

采用 Minimal Mistakes 4.28.1 dark 的Sass基础，独立 music-base 布局与封面唱片架。保留旧文章与旧导航URL；旧评论、追踪和密钥配置不再载入。公开Git历史中的旧OAuth client_secret必须由账户所有人撤销/轮换，删掉当前字段不等于撤销。

主题改动通过 `Validate music shelf` 的Jekyll构建与页面检查，成功后才考虑上线；不更改域名/DNS。ChatGPT每日任务负责研究和内容生成，GitHub工作流只负责测试，不是另一个AI生成任务。
