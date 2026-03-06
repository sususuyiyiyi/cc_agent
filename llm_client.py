#!/usr/bin/env python3
"""
最小化的 LLM 客户端（Anthropic Messages API 兼容）

设计目标：
- 不在仓库里保存任何密钥，只从环境变量读取
- 默认兼容智谱的 Claude API 兼容网关（open.bigmodel.cn）
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx


class LLMConfigError(RuntimeError):
    pass


class LLMRequestError(RuntimeError):
    pass


@dataclass(frozen=True)
class AnthropicCompatConfig:
    base_url: str
    auth_token: str
    model: str = "glm-4.5-air"
    timeout_s: float = 60.0


def _env(name: str) -> str:
    return os.getenv(name, "").strip()


def load_anthropic_compat_config() -> AnthropicCompatConfig:
    """
    从环境变量读取配置：
    - ANTHROPIC_BASE_URL: 例如 https://open.bigmodel.cn/api/anthropic
    - ANTHROPIC_AUTH_TOKEN: 智谱 API Key（或 Anthropic API key）
    - ANTHROPIC_MODEL: 可选，默认 glm-5
    """
    base_url = _env("ANTHROPIC_BASE_URL") or "https://open.bigmodel.cn/api/anthropic"
    auth_token = _env("ANTHROPIC_AUTH_TOKEN") or _env("ANTHROPIC_API_KEY")
    model = _env("ANTHROPIC_MODEL") or "glm-4.5-air"

    if not auth_token:
        raise LLMConfigError(
            "未检测到 ANTHROPIC_AUTH_TOKEN（或 ANTHROPIC_API_KEY）。"
            "请先在运行 CC Agent 的环境里 export 该变量。"
        )

    return AnthropicCompatConfig(base_url=base_url, auth_token=auth_token, model=model)


def _extract_text_from_messages_response(data: Dict[str, Any]) -> str:
    """
    Anthropic Messages API 通常返回：
    { "content": [ { "type": "text", "text": "..." }, ... ] }
    """
    content = data.get("content")
    if isinstance(content, list):
        texts: List[str] = []
        for part in content:
            if isinstance(part, dict) and part.get("type") == "text":
                t = part.get("text")
                if isinstance(t, str) and t.strip():
                    texts.append(t)
        if texts:
            return "\n".join(texts).strip()

    # 兼容某些网关/代理直接返回 text 字段
    if isinstance(data.get("text"), str) and data["text"].strip():
        return data["text"].strip()

    raise RuntimeError(f"无法从模型响应中提取文本：keys={list(data.keys())}")


def anthropic_messages_create(
    *,
    system: Optional[str],
    user: str,
    model: Optional[str] = None,
    max_tokens: int = 1024,
    temperature: float = 0.3,
    extra_headers: Optional[Dict[str, str]] = None,
) -> str:
    """
    调用 Anthropic Messages API 兼容接口，返回文本结果。
    """
    cfg = load_anthropic_compat_config()
    endpoint = cfg.base_url.rstrip("/") + "/v1/messages"

    headers = {
        "Content-Type": "application/json",
        # 智谱文档：支持 Bearer 或 x-api-key；这里两者都带上，最大化兼容性
        "Authorization": f"Bearer {cfg.auth_token}",
        "x-api-key": cfg.auth_token,
        # Anthropic 原生会要求版本头；兼容网关一般忽略但不会报错
        "anthropic-version": "2023-06-01",
    }
    if extra_headers:
        headers.update(extra_headers)

    payload: Dict[str, Any] = {
        "model": model or cfg.model,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "messages": [{"role": "user", "content": user}],
    }
    if system:
        payload["system"] = system

    with httpx.Client(timeout=cfg.timeout_s) as client:
        try:
            resp = client.post(endpoint, headers=headers, json=payload)
            resp.raise_for_status()
        except httpx.HTTPStatusError as e:
            status = e.response.status_code if e.response else None
            body_preview = ""
            body_json: Dict[str, Any] = {}
            try:
                body_preview = (e.response.text or "").strip()
                if len(body_preview) > 300:
                    body_preview = body_preview[:300] + "..."
            except Exception:
                body_preview = ""
            try:
                body_json = e.response.json() if e.response is not None else {}
            except Exception:
                body_json = {}

            if status == 401:
                raise LLMRequestError(
                    "模型调用返回 401（鉴权失败）。请检查：\n"
                    "- `ANTHROPIC_AUTH_TOKEN` 是否正确\n"
                    "- `ANTHROPIC_BASE_URL` 是否为 `https://open.bigmodel.cn/api/anthropic`\n"
                    f"- endpoint: {endpoint}\n"
                    f"- body: {body_preview or '(empty)'}"
                ) from e
            if status == 429:
                # 智谱常见：429 + 特定业务错误码（例如模型权限不足）
                try:
                    err = body_json.get("error", {}) if isinstance(body_json, dict) else {}
                    code = str(err.get("code", "")).strip()
                    msg = str(err.get("message", "")).strip()
                except Exception:
                    code, msg = "", ""

                if code == "1311" and msg:
                    raise LLMRequestError(
                        "模型调用返回 429，但实际原因是：当前套餐对该模型无权限。\n"
                        f"- message: {msg}\n"
                        "解决：把 `ANTHROPIC_MODEL` 换成你账号有权限的模型（例如 `glm-4.5-air` / `glm-4.7` 等），再重试。\n"
                        f"- endpoint: {endpoint}"
                    ) from e

                raise LLMRequestError(
                    "模型调用返回 429（请求过于频繁/额度限制）。建议稍后重试，或降低调用频率/并发。\n"
                    f"- endpoint: {endpoint}\n"
                    f"- body: {body_preview or '(empty)'}"
                ) from e

            raise LLMRequestError(
                f"模型调用失败（HTTP {status}）。\n"
                f"- endpoint: {endpoint}\n"
                f"- body: {body_preview or '(empty)'}"
            ) from e
        except httpx.RequestError as e:
            raise LLMRequestError(
                "模型调用网络错误（无法连接/超时/DNS 等）。\n"
                f"- endpoint: {endpoint}\n"
                f"- error: {type(e).__name__}: {e}"
            ) from e

        data = resp.json()
        return _extract_text_from_messages_response(data)

