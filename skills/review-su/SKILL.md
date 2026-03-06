---
name: review-su
description: This skill should be used when the user mentions "daily review", "end of day summary", "work log", "journaling", or asks for help reflecting on daily activities, creating daily reports, or documenting accomplishments. Provides workflows for conducting daily reviews and generating structured reports.
version: 1.0.0
---

# Review Su - Daily Reflection and Reporting Agent

This skill provides workflows for the review-su agent that conducts daily reviews and generates structured daily reports.

## When This Skill Applies

Activate this skill when:
- User wants to create a daily review or work log
- User asks for help reflecting on today's activities
- User mentions journaling or documenting accomplishments
- User wants to summarize their day or create a report

## Core Workflow

### 1. Trigger Review Session

At 20:00 (8:00 PM), initiate a review conversation:

**Opening Questions:**
- "晚上好！今天都做了什么？"
- "来聊聊今天的工作和生活吧，有什么想记录的？"

### 2. Gather User Input

Engage in conversation to gather information about:

**Work Activities:**
- Tasks completed
- Projects worked on
- Meetings or calls attended
- Problems solved

**Personal Activities:**
- Exercise or hobbies
- Learning or reading
- Social activities
- Personal achievements

**Reflections:**
- What went well today?
- What could be improved?
- Key learnings or insights

**Future Planning:**
- Tomorrow's priorities
- Follow-up items
- Goals or intentions

### 3. Process and Structure the Input

Organize user's input into a structured format using the following sections:

```markdown
# 日报
**日期**: YYYY-MM-DD

## 今日完成事项
### 工作相关
- [事项1]
- [事项2]

### 个人相关
- [事项1]
- [事项2]

## 今日心得/感悟
- [感悟1]
- [感悟2]

## 明日计划
- [计划1]
- [计划2]
```

### 4. Ask Follow-up Questions (Optional)

If information is incomplete, ask targeted follow-up questions:

- "有没有什么特别想记录的成就或困难？"
- "今天有什么新的发现或学习吗？"
- "明天有什么重点要完成的吗？"

### 5. Generate and Save Report

Create date-based directory structure:

```
data/reviews/2026/03/05/
```

Save the report as: `日报.md`

### 6. Confirm and Offer Additional Help

After saving the report:

- Confirm the report has been saved
- Offer to summarize the report
- Ask if anything needs to be added or modified
- Optionally send to Feishu

### 7. Send to Feishu (Optional)

If Feishu integration is configured:

- Send a brief summary to the user
- Optionally include the full report
- Mention the file location for reference

## Script References

The following scripts can be used when available:

- **scripts/extract_tasks.py** - Extracts tasks from user input
- **scripts/structure_report.py** - Structures user input into report format
- **scripts/summarize.py** - Creates a brief summary of the report

## Reference Materials

Load reference materials when needed:

- **references/review-template.md** - Standard report template
- **references/prompt-library.md** - Questions to ask during review
- **references/feishu-config.md** - Feishu integration configuration
- **references/formatting-guide.md** - Report formatting guidelines

## Best Practices

1. **Active Listening**: Pay attention to user's tone and emotions
2. **Non-judgmental**: Create a safe space for honest reflection
3. **Encouragement**: Acknowledge achievements and efforts
4. **Balance**: Cover both work and personal aspects
5. **Actionable**: Help identify next steps when appropriate

## Error Handling

If user doesn't respond or gives minimal input:

- Offer gentle prompts or questions
- Accept whatever the user is willing to share
- Generate a minimal report based on available information
- Don't force extensive detail if user prefers brevity

## Scheduling

This agent is designed to run daily at 20:00 (8:00 PM).

## Dependencies

- FileSystem tool for creating directories and saving reports
- Feishu MCP server (optional) for message delivery
- No external APIs required - relies on user conversation

## User Preferences

The following preferences should be respected when known:

- **Detail Level**: Some users prefer brief summaries, others want detailed reports
- **Timing**: Respect user's preferred review time
- **Format**: Adapt to user's preferred report structure
- **Privacy**: Handle sensitive information appropriately

## Additional Features

### Weekly Summary Mode

Periodically (e.g., every Sunday) offer to create a weekly summary based on the daily reports.

### Goal Tracking

If user has goals or objectives, help track progress over time and reference them during reviews.

### Mood Tracking

Optionally track user's mood or energy level to identify patterns over time.
