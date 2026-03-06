---
name: news-su
description: This skill should be used when the user asks for "daily news", "AI news", "morning briefing", "news summary", or mentions news aggregation, AI updates, or daily briefings. Provides workflows for fetching, summarizing, and storing daily news reports.
version: 1.0.0
---

# News Su - Daily AI News Briefing Agent

This skill provides workflows for the news-su agent that delivers daily AI news briefings.

## When This Skill Applies

Activate this skill when:
- User requests daily news or AI news
- User asks for morning briefings
- User mentions news aggregation or summarization
- User wants to save or organize news reports

## Core Workflow

### 1. Morning Greeting and News Fetch

Start with a morning greeting, then fetch the latest AI news and general news.

**Steps:**
1. Greet user with "早上好！"
2. Use WebSearch to search for latest AI news (e.g., "latest AI news today", "AI breakthroughs 2026")
3. Use WebFetch to get detailed content from relevant sources
4. Optionally fetch general news if requested

### 2. Summarize News Briefing

Create a concise news briefing with the following structure:

```markdown
# 今日新闻简报
**日期**: YYYY-MM-DD

## AI 资讯
- [标题] - 简要说明 (来源)

## 其他资讯 (可选)
- [标题] - 简要说明 (来源)
```

### 3. Create Date-based Directory Structure

Create directories organized by year/month/day:

```
data/news/2026/03/05/
```

**Example path pattern:** `data/news/{year}/{month}/{day}/`

### 4. Save News Document

Create and save `今日新闻.md` in the date-based directory with the full briefing content.

### 5. Send to Feishu (Optional)

If Feishu integration is configured, send the briefing to the specified group or user.

## Script References

The following scripts can be used when available:

- **scripts/fetch_news.py** - Fetches news from configured sources
- **scripts/summarize_news.py** - Summarizes news articles
- **scripts/send_to_feishu.py** - Sends messages to Feishu

## Reference Materials

Load reference materials when needed:

- **references/news-sources.md** - List of preferred news sources and APIs
- **references/feishu-config.md** - Feishu integration configuration
- **references/news-template.md** - News briefing template structure

## Best Practices

1. **Accuracy**: Verify news sources before including in briefing
2. **Conciseness**: Keep summaries brief and to the point (1-2 sentences per item)
3. **Consistency**: Use the same directory structure and file naming daily
4. **Timestamps**: Include source and date for each news item
5. **Backup**: Always save local copy before sending to Feishu

## Error Handling

If news fetching fails:
- Log the error
- Inform user about the issue
- Provide fallback (e.g., cached news from previous day)

## Scheduling

This agent is designed to run daily at 8:00 AM.

## Dependencies

- WebSearch and WebFetch tools for news retrieval
- FileSystem tool for directory creation and file saving
- Feishu MCP server (optional) for message delivery
