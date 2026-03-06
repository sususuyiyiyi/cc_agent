# 新闻源配置

本文档配置了 CC Agent 资讯su 的所有新闻源。

---

## 一、AI垂直媒体（国内）

### 新智元
- **URL**: https://www.zhidx.com
- **特点**: 国内AI新闻非常快，很多论文解读和大模型进展
- **频率**: 每日更新
- **重点**: AI论文解读、大模型进展

### AI科技评论（雷锋网）
- **URL**: https://www.leiphone.com
- **特点**: 偏技术深度和产业分析
- **频率**: 每日更新
- **重点**: 技术分析、产业趋势

### PaperWeekly
- **URL**: https://www.paperweekly.site
- **特点**: 论文解读质量很高
- **频率**: 周刊更新
- **重点**: 学术论文解读

### AI前线（InfoQ）
- **URL**: https://www.infoq.cn/topic/ai
- **特点**: 技术架构、工程实践比较多
- **频率**: 每日更新
- **重点**: 工程实践、技术架构

### 极市平台
- **URL**: https://www.cvmart.net
- **特点**: 偏计算机视觉
- **频率**: 不定期更新
- **重点**: 计算机视觉、图像处理

---

## 二、科技媒体（国内）

### 36氪
- **URL**: https://36kr.com
- **特点**: 科技创业、投资资讯
- **频率**: 每日多次更新
- **重点**: 创业、投资、科技

### 钛媒体
- **URL**: https://www.tmtpost.com
- **特点**: 深度科技报道
- **频率**: 每日更新
- **重点**: 深度报道、科技趋势

### 虎嗅
- **URL**: https://www.huxiu.com
- **特点**: 产业洞察和商业分析很强
- **频率**: 每日更新
- **重点**: 商业分析、产业洞察

### 极客公园
- **URL**: https://www.geekpark.net
- **特点**: AI产品和科技公司报道
- **频率**: 每日更新
- **重点**: 产品报道、公司动态

### IT之家
- **URL**: https://www.ithome.com
- **特点**: 更新速度极快，适合刷新闻
- **频率**: 每日多次更新
- **重点**: 快讯、科技新闻

### 晚点LatePost
- **URL**: https://www.latepost.com
- **特点**: 深度报道质量非常高
- **频率**: 不定期深度报道
- **重点**: 深度报道、独家新闻

---

## 三、国际AI媒体

### TechCrunch
- **URL**: https://techcrunch.com
- **特点**: 科技创业和投资
- **频率**: 每日更新
- **重点**: 创业、投资、AI

### AI News
- **URL**: https://artificialintelligence-news.com
- **特点**: AI行业新闻
- **频率**: 每日更新
- **重点**: AI行业动态

### The Information
- **URL**: https://www.theinformation.com
- **特点**: AI和科技商业内幕（质量极高）
- **频率**: 每周更新
- **重点**: 商业内幕、独家新闻

### VentureBeat AI
- **URL**: https://venturebeat.com/ai
- **特点**: 企业AI、Agent、LLM动态
- **频率**: 每日更新
- **重点**: 企业AI、LLM、Agent

### MIT Technology Review
- **URL**: https://www.technologyreview.com
- **特点**: MIT官方科技媒体
- **频率**: 每日更新
- **重点**: 深度科技分析

### Synced Review
- **URL**: https://www.syncedreview.com
- **特点**: 偏AI研究
- **频率**: 不定期更新
- **重点**: AI研究、学术

---

## 四、AI研究资讯（非常重要）

### Hugging Face Blog
- **URL**: https://huggingface.co/blog
- **特点**: 开源AI平台官方博客
- **频率**: 不定期更新
- **重点**: 开源模型、工具

### OpenAI Blog
- **URL**: https://openai.com/blog
- **特点**: OpenAI官方博客
- **频率**: 不定期更新
- **重点**: GPT、ChatGPT、DALL-E

### DeepMind Blog
- **URL**: https://deepmind.google/blog
- **特点**: DeepMind官方博客
- **频率**: 不定期更新
- **重点**: AlphaGo、AlphaFold等

### Anthropic News
- **URL**: https://www.anthropic.com/news
- **特点**: Anthropic官方新闻
- **频率**: 不定期更新
- **重点**: Claude、AI安全

---

## 五、AI日报/聚合站（高效）

### The Rundown AI
- **URL**: https://www.therundown.ai
- **特点**: AI新闻日报
- **频率**: 每日更新
- **重点**: AI新闻摘要

### Ben's Bites
- **URL**: https://www.bensbites.co
- **特点**: AI新闻简报
- **频率**: 每日更新
- **重点**: AI新闻总结

### TLDR AI
- **URL**: https://www.tldr.tech/ai
- **特点**: AI新闻简报
- **频率**: 每日更新
- **重点**: 快速了解AI新闻

### Import AI（Andrew Ng）
- **URL**: https://www.deeplearning.ai/the-batch/
- **特点**: Andrew Ng的AI新闻
- **频率**: 每周更新
- **重点**: AI行业动态

---

## 🎯 新闻源优先级

### 第一优先级（每日必看）
1. OpenAI Blog - Claude相关
2. 新智元 - 国内AI快讯
3. IT之家 - 科技快讯
4. The Rundown AI - AI日报

### 第二优先级（深度阅读）
1. The Information - 商业内幕
2. 晚点LatePost - 深度报道
3. MIT Technology Review - 深度分析
4. AI科技评论（雷锋网）- 技术分析

### 第三优先级（定期查看）
1. Hugging Face Blog - 开源动态
2. DeepMind Blog - 研究进展
3. VentureBeat AI - 企业AI
4. 36氪 - 创投资讯

---

## 🔧 配置说明

这些新闻源可以用于：

1. **自动抓取** - 使用 WebFetch 抓取内容
2. **RSS订阅** - 如果有RSS Feed
3. **API调用** - 如果网站提供API
4. **搜索索引** - 使用 WebSearch 搜索最新内容

---

## 📝 使用建议

- **快速浏览**: IT之家、新智元
- **深度阅读**: The Information、晚点LatePost
- **技术分析**: AI科技评论、MIT Technology Review
- **研究跟踪**: OpenAI Blog、DeepMind Blog
- **综合日报**: The Rundown AI、Ben's Bites

---

**最后更新**: 2026-03-06
**维护者**: susu
