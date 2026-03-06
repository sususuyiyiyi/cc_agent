---
name: wellness-su
description: This skill should be used when the user asks for "diet suggestions", "outfit recommendations", "wellness advice", "weather-based tips", or mentions nutrition, clothing, or health recommendations based on weather conditions. Provides workflows for delivering weather-based diet and outfit advice.
version: 1.0.0
---

# Wellness Su - Daily Diet and Outfit Advisor

This skill provides workflows for the wellness-su agent that delivers daily diet and outfit recommendations based on weather conditions.

## When This Skill Applies

Activate this skill when:
- User asks for diet suggestions or nutrition advice
- User requests outfit or clothing recommendations
- User mentions wellness, health, or lifestyle tips
- User wants advice based on current or forecasted weather

## Core Workflow

### 1. Fetch Weather Information

Get current day's weather data for the user's location.

**Weather Data Required:**
- Temperature (current and forecast)
- Humidity
- Weather condition (sunny, cloudy, rainy, snowy, etc.)
- Wind speed
- UV index (if available)

**Steps:**
1. Determine user's location (default to configured location)
2. Use Weather MCP or API to fetch current weather
3. Get daily forecast if available

### 2. Generate Diet Recommendations

Provide diet suggestions based on weather conditions:

**Cold Weather (< 10°C):**
- Recommend warm, hearty meals
- Suggest hot soups, stews, or porridge
- Include warming spices (ginger, cinnamon)
- Recommend hot beverages (tea, warm water)

**Moderate Weather (10°C - 25°C):**
- Balanced meals with variety
- Fresh fruits and vegetables
- Light soups or salads
- Room temperature foods

**Hot Weather (> 25°C):**
- Light, refreshing meals
- Cold dishes and salads
- Hydrating foods (watermelon, cucumber)
- Avoid heavy, greasy foods

**Rainy/Humid Weather:**
- Foods that boost immunity (vitamin C rich)
- Warm soups
- Avoid overly oily foods
- Include ginger or garlic

### 3. Generate Outfit Recommendations

Provide clothing suggestions based on weather:

**Temperature-based:**
- **< 5°C**: Down jacket, thermal underwear, scarf, gloves, warm hat
- **5-15°C**: Heavy coat, sweater, long pants, light layers
- **15-20°C**: Light jacket, sweater, jeans or trousers
- **20-25°C**: T-shirt, light cardigan, comfortable pants
- **> 25°C**: Light, breathable clothing, shorts, sun protection

**Weather Condition-based:**
- **Sunny**: Sunscreen, sunglasses, hat
- **Cloudy**: Light layers, comfortable shoes
- **Rainy**: Raincoat or umbrella, waterproof shoes, extra socks
- **Snowy**: Waterproof boots, thermal wear, scarf and gloves
- **Windy**: Windbreaker, secured accessories

### 4. Save Wellness Report (Optional)

Create daily wellness report with structure:

```markdown
# 今日健康建议
**日期**: YYYY-MM-DD

## 天气情况
- 温度: XX°C
- 湿度: XX%
- 天气: [condition]

## 饮食建议
- [建议1]
- [建议2]

## 穿搭建议
- [建议1]
- [建议2]

## 额外提醒
- [如有特殊注意事项]
```

Save to: `data/wellness/2026/03/05/建议.md`

### 5. Send to Feishu (Optional)

If Feishu integration is configured, send the recommendations to the user.

## Script References

The following scripts can be used when available:

- **scripts/fetch_weather.py** - Fetches weather from configured API
- **scripts/diet_recommender.py** - Generates diet suggestions based on weather
- **scripts/outfit_recommender.py** - Generates clothing recommendations

## Reference Materials

Load reference materials when needed:

- **references/weather-locations.md** - User's default location(s)
- **references/diet-guidelines.md** - Nutrition guidelines and food suggestions
- **references/clothing-guide.md** - Detailed clothing recommendations by temperature
- **references/feishu-config.md** - Feishu integration configuration

## Best Practices

1. **Personalization**: Consider user's preferences when giving advice
2. **Safety**: Prioritize comfort and safety over fashion
3. **Flexibility**: Provide options rather than strict rules
4. **Context-aware**: Consider activity level and occasion if known
5. **Health-first**: Prioritize health and wellbeing recommendations

## Error Handling

If weather fetching fails:
- Use last known weather data
- Inform user about the limitation
- Provide general wellness advice that's not weather-dependent

## Scheduling

This agent is designed to run daily at 8:30 AM (after news-su).

## Dependencies

- Weather MCP server or API for weather data
- FileSystem tool for saving reports
- Feishu MCP server (optional) for message delivery
