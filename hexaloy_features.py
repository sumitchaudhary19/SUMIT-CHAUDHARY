# ══════════════════════════════════════════════════════════════════════════════
#   HEXALOY AI — EXTENDED FEATURES & UTILITIES MODULE
#   hexaloy_features.py
#   This module provides additional components for HEXALOY v7.0
#   Import into app.py or use as reference for integration
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import json
import datetime
import os
import re
import random
import hashlib
import time
import base64
import urllib.parse
from typing import Optional, List, Dict, Any, Generator, Tuple


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 1: KEYBOARD SHORTCUTS JAVASCRIPT INJECTOR
# ──────────────────────────────────────────────────────────────────────────────

KEYBOARD_SHORTCUTS_JS = """
<script>
// HEXALOY Keyboard Shortcuts v7.0

const shortcuts = {
    'ctrl+k':  () => document.querySelector('[data-testid="stChatInputContainer"] textarea')?.focus(),
    'ctrl+l':  () => window.location.reload(),
    'escape':  () => document.querySelector('[data-testid="stChatInputContainer"] textarea')?.blur(),
};

document.addEventListener('keydown', (e) => {
    const key = (e.ctrlKey ? 'ctrl+' : '') + (e.altKey ? 'alt+' : '') + e.key.toLowerCase();
    if (shortcuts[key]) {
        e.preventDefault();
        shortcuts[key]();
    }
});

// Auto-scroll to bottom on new messages
const observer = new MutationObserver(() => {
    const messages = document.querySelectorAll('[data-testid="stChatMessage"]');
    if (messages.length > 0) {
        messages[messages.length - 1].scrollIntoView({ behavior: 'smooth', block: 'end' });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    observer.observe(document.body, { childList: true, subtree: true });
});

// Typing animation for placeholder
const updatePlaceholder = () => {
    const textarea = document.querySelector('[data-testid="stChatInputContainer"] textarea');
    if (!textarea) return;
    const placeholders = [
        "Ask HEXALOY anything...",
        "Write me a Python script for...",
        "Explain quantum computing...",
        "Draw a futuristic city...",
        "What's the best approach to...",
        "Help me debug this code...",
        "Translate this to Hindi...",
    ];
    let idx = 0;
    setInterval(() => {
        if (document.activeElement !== textarea) {
            textarea.placeholder = placeholders[idx % placeholders.length];
            idx++;
        }
    }, 3000);
};

setTimeout(updatePlaceholder, 1500);

// Add copy button to code blocks
const addCopyButtons = () => {
    document.querySelectorAll('pre:not(.has-copy)').forEach(pre => {
        pre.classList.add('has-copy');
        pre.style.position = 'relative';
        const btn = document.createElement('button');
        btn.className = 'copy-btn';
        btn.textContent = '⎘ Copy';
        btn.onclick = () => {
            const code = pre.querySelector('code')?.textContent || pre.textContent;
            navigator.clipboard.writeText(code).then(() => {
                btn.textContent = '✓ Copied!';
                setTimeout(() => btn.textContent = '⎘ Copy', 2000);
            });
        };
        pre.appendChild(btn);
    });
};

setInterval(addCopyButtons, 1000);

console.log('🔵 HEXALOY Keyboard Shortcuts + Enhancements loaded');
</script>
"""


def inject_keyboard_shortcuts():
    """Inject JavaScript enhancements into the Streamlit page."""
    st.markdown(KEYBOARD_SHORTCUTS_JS, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 2: EXPORT / DOWNLOAD UTILITIES
# ──────────────────────────────────────────────────────────────────────────────

def export_chat_as_markdown(history: list, session_name: str) -> str:
    """
    Convert chat history to beautifully formatted Markdown.
    Returns the Markdown string.
    """
    lines = [
        f"# 💠 HEXALOY AI — Chat Export",
        f"",
        f"**Session:** {session_name}",
        f"**Exported:** {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        f"**Messages:** {len(history)}",
        f"",
        "---",
        "",
    ]
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        ts = msg.get("ts", "")
        model = msg.get("model", "")

        if role == "user":
            lines.append(f"### 🧑‍💼 You{' · ' + ts if ts else ''}")
        else:
            lines.append(f"### 💠 HEXALOY{' · ' + ts if ts else ''}{' · ' + model if model else ''}")

        lines.append("")
        lines.append(content)
        lines.append("")
        lines.append("---")
        lines.append("")

    lines.append(f"*Generated by HEXALOY AI v7.0 — Architected by VINIT MAAN*")
    return "\n".join(lines)


def export_chat_as_json(history: list, session_name: str) -> str:
    """Export chat history as formatted JSON."""
    data = {
        "hexaloy_version": "7.0",
        "session_name": session_name,
        "exported_at": datetime.datetime.now().isoformat(),
        "message_count": len(history),
        "messages": history,
        "metadata": {
            "architect": "VINIT MAAN",
            "platform": "HEXALOY Enterprise AI",
        }
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_chat_as_html(history: list, session_name: str) -> str:
    """Export chat history as a standalone beautiful HTML file."""
    msgs_html = ""
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        ts = msg.get("ts", "")
        is_user = role == "user"

        # Escape HTML
        content_escaped = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

        avatar  = "🧑‍💼" if is_user else "💠"
        label   = "You" if is_user else "HEXALOY"
        bg      = "#EEF2FF" if is_user else "#FFFFFF"
        border  = "#C7D7FF" if is_user else "#E2E8F0"

        msgs_html += f"""
        <div style="
            background:{bg}; border:1px solid {border};
            border-radius:16px; padding:18px 22px; margin-bottom:14px;
        ">
            <div style="font-weight:700;margin-bottom:8px;color:#0D1B4B;">
                {avatar} {label}
                <span style="font-weight:400;font-size:0.75rem;color:#7A8BB0;margin-left:8px;">{ts}</span>
            </div>
            <div style="color:#1E293B;line-height:1.7;white-space:pre-wrap;font-size:0.95rem;">{content_escaped}</div>
        </div>
        """

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>HEXALOY Chat Export — {session_name}</title>
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        body {{ font-family:'Outfit',sans-serif; background:#F0F4FF; color:#0D1B4B; margin:0; padding:0; }}
        .container {{ max-width:820px; margin:0 auto; padding:40px 20px; }}
        .header {{ text-align:center; margin-bottom:36px; padding:32px; background:white; border-radius:20px; border:1px solid #E8EEFF; box-shadow:0 4px 24px rgba(43,92,230,0.10); }}
        h1 {{ font-size:2rem; margin:0 0 8px; color:#2B5CE6; }}
        .meta {{ color:#7A8BB0; font-size:0.85rem; }}
        .footer {{ text-align:center; margin-top:40px; color:#AAB4CC; font-size:0.78rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>💠 HEXALOY Chat Export</h1>
            <div class="meta">
                Session: <strong>{session_name}</strong> &nbsp;·&nbsp;
                {len(history)} messages &nbsp;·&nbsp;
                {datetime.datetime.now().strftime('%B %d, %Y')}
            </div>
        </div>
        {msgs_html}
        <div class="footer">HEXALOY AI v7.0 &nbsp;·&nbsp; Architected by VINIT MAAN</div>
    </div>
</body>
</html>"""


def render_export_panel(history: list, session_name: str):
    """Render an export panel with download buttons in Streamlit."""
    if not history:
        st.warning("No messages to export yet.")
        return

    st.markdown("#### 📥 Export Chat")

    md_content   = export_chat_as_markdown(history, session_name)
    json_content = export_chat_as_json(history, session_name)
    html_content = export_chat_as_html(history, session_name)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.download_button(
            label="📄 Markdown",
            data=md_content,
            file_name=f"hexaloy_{session_name.replace(' ', '_')}.md",
            mime="text/markdown",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            label="📊 JSON",
            data=json_content,
            file_name=f"hexaloy_{session_name.replace(' ', '_')}.json",
            mime="application/json",
            use_container_width=True,
        )
    with col3:
        st.download_button(
            label="🌐 HTML",
            data=html_content,
            file_name=f"hexaloy_{session_name.replace(' ', '_')}.html",
            mime="text/html",
            use_container_width=True,
        )


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 3: ANALYTICS DASHBOARD
# ──────────────────────────────────────────────────────────────────────────────

def compute_analytics(sessions: dict) -> dict:
    """Compute comprehensive analytics from all sessions."""
    total_sessions = len(sessions)
    total_messages = 0
    total_words    = 0
    total_tokens   = 0
    user_messages  = 0
    ai_messages    = 0
    longest_msg    = 0
    session_lengths = []
    word_freq: Dict[str, int] = {}

    for sname, history in sessions.items():
        session_lengths.append(len(history))
        for msg in history:
            content = msg.get("content", "")
            if not isinstance(content, str):
                continue
            total_messages += 1
            words = content.split()
            total_words += len(words)
            total_tokens += len(content) // 4
            longest_msg = max(longest_msg, len(content))

            if msg.get("role") == "user":
                user_messages += 1
                for w in words:
                    w_clean = re.sub(r'[^\w]', '', w.lower())
                    if len(w_clean) > 4:
                        word_freq[w_clean] = word_freq.get(w_clean, 0) + 1
            else:
                ai_messages += 1

    top_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
    avg_session_length = (sum(session_lengths) / len(session_lengths)) if session_lengths else 0

    return {
        "total_sessions":     total_sessions,
        "total_messages":     total_messages,
        "total_words":        total_words,
        "total_tokens":       total_tokens,
        "user_messages":      user_messages,
        "ai_messages":        ai_messages,
        "longest_msg_chars":  longest_msg,
        "avg_session_length": round(avg_session_length, 1),
        "top_words":          top_words,
        "session_lengths":    session_lengths,
    }


def render_analytics_panel(sessions: dict):
    """Render a full analytics dashboard in Streamlit."""
    analytics = compute_analytics(sessions)

    st.markdown("""
    <h3 style="font-family:'Playfair Display',serif;color:#0D1B4B;margin-bottom:20px;">
        📊 Session Analytics
    </h3>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        (col1, "💬 Messages",   analytics["total_messages"],     None),
        (col2, "📝 Words",      f"{analytics['total_words']:,}", None),
        (col3, "🪙 ~Tokens",    f"{analytics['total_tokens']:,}",None),
        (col4, "📂 Sessions",   analytics["total_sessions"],     None),
    ]
    for col, label, value, delta in metrics:
        with col:
            st.metric(label=label, value=value, delta=delta)

    st.markdown("---")

    col_a, col_b = st.columns(2)

    with col_a:
        st.markdown("**Message Breakdown**")
        u = analytics["user_messages"]
        a = analytics["ai_messages"]
        total = u + a or 1
        u_pct = round(u / total * 100)
        a_pct = 100 - u_pct
        st.markdown(f"""
        <div style="background:#F0F4FF;border-radius:12px;padding:16px;border:1px solid #C7D7FF;">
            <div style="margin-bottom:8px;">
                <span style="font-weight:600;color:#2B5CE6;">You:</span>
                <span style="float:right;color:#3B4B7E;">{u} messages ({u_pct}%)</span>
            </div>
            <div style="height:8px;background:#E8EEFF;border-radius:4px;overflow:hidden;margin-bottom:12px;">
                <div style="height:100%;width:{u_pct}%;background:linear-gradient(90deg,#2B5CE6,#0FBFBF);border-radius:4px;"></div>
            </div>
            <div style="margin-bottom:8px;">
                <span style="font-weight:600;color:#0FBFBF;">HEXALOY:</span>
                <span style="float:right;color:#3B4B7E;">{a} messages ({a_pct}%)</span>
            </div>
            <div style="height:8px;background:#E8EEFF;border-radius:4px;overflow:hidden;">
                <div style="height:100%;width:{a_pct}%;background:linear-gradient(90deg,#0FBFBF,#22C55E);border-radius:4px;"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("**Top Keywords You've Used**")
        if analytics["top_words"]:
            max_count = analytics["top_words"][0][1] if analytics["top_words"] else 1
            for word, count in analytics["top_words"][:6]:
                width = int(count / max_count * 100)
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
                    <span style="width:80px;font-size:0.82rem;font-weight:500;color:#0D1B4B;">{word}</span>
                    <div style="flex:1;height:6px;background:#E8EEFF;border-radius:3px;overflow:hidden;">
                        <div style="height:100%;width:{width}%;background:linear-gradient(90deg,#2B5CE6,#0FBFBF);border-radius:3px;"></div>
                    </div>
                    <span style="font-size:0.75rem;color:#7A8BB0;width:20px;text-align:right;">{count}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("*Start chatting to see keyword analytics!*")

    st.markdown("---")
    st.markdown(f"""
    <div style="display:flex;gap:16px;flex-wrap:wrap;">
        <div style="background:#F0F4FF;border:1px solid #C7D7FF;border-radius:10px;padding:12px 18px;">
            <span style="font-size:0.75rem;color:#7A8BB0;display:block;">Avg Session Length</span>
            <span style="font-size:1.2rem;font-weight:700;color:#2B5CE6;">{analytics['avg_session_length']} msgs</span>
        </div>
        <div style="background:#F0FDF4;border:1px solid #BBF7D0;border-radius:10px;padding:12px 18px;">
            <span style="font-size:0.75rem;color:#7A8BB0;display:block;">Longest Message</span>
            <span style="font-size:1.2rem;font-weight:700;color:#16A34A;">{analytics['longest_msg_chars']:,} chars</span>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 4: SMART PROMPT TEMPLATES
# ──────────────────────────────────────────────────────────────────────────────

PROMPT_TEMPLATES = {
    "💻 Code Review": {
        "template": "Please review the following code and provide:\n1. **Bugs & Issues** found\n2. **Security vulnerabilities** if any\n3. **Performance improvements**\n4. **Best practices** recommendations\n5. **Refactored version**\n\n```\n{code}\n```",
        "placeholder": "Paste your code here...",
        "category": "Development",
    },
    "📝 Blog Post": {
        "template": "Write a comprehensive, engaging blog post about **{topic}**.\n\nRequirements:\n- Target audience: {audience}\n- Tone: {tone}\n- Length: ~{length} words\n- Include: Introduction, main sections with subheadings, actionable takeaways, conclusion\n- SEO-optimized with natural keyword usage",
        "placeholder": "Blog post topic...",
        "category": "Writing",
    },
    "📊 Data Analysis": {
        "template": "Analyze the following data and provide:\n1. **Key Insights** (top 5)\n2. **Trends** observed\n3. **Anomalies** or outliers\n4. **Recommendations** based on findings\n5. **Visualization suggestions**\n\nData:\n{data}",
        "placeholder": "Paste your data or describe it...",
        "category": "Analytics",
    },
    "🎯 Marketing Copy": {
        "template": "Create compelling marketing copy for:\n\n**Product/Service:** {product}\n**Target Audience:** {audience}\n**Key Benefits:** {benefits}\n**Tone:** {tone}\n\nDeliver: Headline, Subheadline, Body copy, CTA, Email subject line, Social media captions (LinkedIn, Twitter, Instagram)",
        "placeholder": "Describe your product...",
        "category": "Marketing",
    },
    "🐛 Debug Code": {
        "template": "I have a bug in my {language} code. Here's the issue:\n\n**Error message:** {error}\n\n**My code:**\n```{language}\n{code}\n```\n\nPlease:\n1. Identify the root cause\n2. Explain why this error occurs\n3. Provide the fixed code\n4. Explain what you changed and why",
        "placeholder": "Describe the error...",
        "category": "Development",
    },
    "📚 Study Guide": {
        "template": "Create a comprehensive study guide for **{topic}**.\n\nInclude:\n1. **Core concepts** explained simply\n2. **Key terms & definitions**\n3. **Important formulas/rules** (if applicable)\n4. **Common misconceptions** to avoid\n5. **Practice questions** with answers\n6. **Memory tricks** / mnemonics\n7. **Real-world applications**",
        "placeholder": "Subject or topic to study...",
        "category": "Education",
    },
    "💌 Professional Email": {
        "template": "Write a professional email:\n\n**From:** {sender}\n**To:** {recipient}\n**Purpose:** {purpose}\n**Key points to cover:** {points}\n**Tone:** {tone}\n\nInclude appropriate subject line, greeting, body, and sign-off.",
        "placeholder": "Describe the email purpose...",
        "category": "Communication",
    },
    "🔍 Research Summary": {
        "template": "Provide a comprehensive research summary on **{topic}**.\n\nCover:\n1. **Background & Context**\n2. **Current state of knowledge**\n3. **Key findings & discoveries**\n4. **Controversies & debates**\n5. **Future directions**\n6. **Practical implications**\n7. **Key researchers/sources**",
        "placeholder": "Research topic...",
        "category": "Research",
    },
}


def render_prompt_templates_panel() -> Optional[str]:
    """
    Render a prompt template picker.
    Returns the selected & filled template string, or None.
    """
    st.markdown("#### 📋 Prompt Templates")
    st.markdown("*Choose a template to get started quickly:*")

    categories = list(set(v["category"] for v in PROMPT_TEMPLATES.values()))
    selected_cat = st.selectbox("Filter by category", ["All"] + sorted(categories), key="template_cat")

    filtered = {
        k: v for k, v in PROMPT_TEMPLATES.items()
        if selected_cat == "All" or v["category"] == selected_cat
    }

    selected_template_name = st.selectbox(
        "Select template",
        list(filtered.keys()),
        key="template_picker"
    )

    if selected_template_name:
        tmpl = filtered[selected_template_name]
        template_str = tmpl["template"]

        # Find all {placeholders} in template
        placeholders = re.findall(r'\{(\w+)\}', template_str)
        filled_values = {}

        if placeholders:
            st.markdown("**Fill in the details:**")
            for ph in placeholders:
                val = st.text_input(f"{ph.replace('_', ' ').title()}:", key=f"tmpl_ph_{ph}")
                filled_values[ph] = val if val else f"[{ph}]"

        # Fill template
        result = template_str
        for ph, val in filled_values.items():
            result = result.replace("{" + ph + "}", val)

        with st.expander("👀 Preview Template", expanded=False):
            st.markdown(result)

        if st.button("✦ Use This Template", use_container_width=True, type="primary", key="use_template_btn"):
            return result

    return None


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 5: AI PERSONA SYSTEM
# ──────────────────────────────────────────────────────────────────────────────

AI_PERSONAS = {
    "💠 Default HEXALOY": {
        "prompt": "You are HEXALOY, an elite AI assistant engineered by VINIT MAAN. Professional, precise, comprehensive.",
        "emoji": "💠",
        "description": "Your all-purpose intelligent assistant"
    },
    "👨‍💻 Senior Dev": {
        "prompt": "You are a Senior Software Engineer with 15+ years of experience across Python, JavaScript, Go, Rust, and system design. You write clean, efficient, well-documented code. You always consider edge cases, performance, and security. Code reviews are thorough and educational.",
        "emoji": "👨‍💻",
        "description": "Expert coder & system architect"
    },
    "🧑‍🔬 Research Scientist": {
        "prompt": "You are a PhD-level research scientist with expertise across physics, biology, chemistry, and mathematics. You explain complex concepts clearly, cite reasoning carefully, acknowledge uncertainty, and always distinguish between established fact and current research frontiers.",
        "emoji": "🧑‍🔬",
        "description": "Deep research & scientific analysis"
    },
    "✍️ Creative Writer": {
        "prompt": "You are an award-winning creative writer with a gift for storytelling, poetic language, and emotional resonance. You write with vivid imagery, compelling characters, and masterful pacing. Every piece of writing you create is memorable and beautifully crafted.",
        "emoji": "✍️",
        "description": "Stories, poetry & creative content"
    },
    "📈 Business Strategist": {
        "prompt": "You are a seasoned business strategist and entrepreneur with deep expertise in market analysis, financial modeling, startup growth, and corporate strategy. You think in frameworks (SWOT, Porter's Five Forces, OKRs) and give actionable, data-driven recommendations.",
        "emoji": "📈",
        "description": "Business strategy & entrepreneurship"
    },
    "🧘 Life Coach": {
        "prompt": "You are an empathetic, insightful life coach and psychologist. You help people gain clarity, overcome challenges, and achieve their goals. You ask powerful questions, offer perspective, validate feelings, and provide practical, compassionate guidance.",
        "emoji": "🧘",
        "description": "Personal growth & wellbeing"
    },
    "🌍 Language Tutor": {
        "prompt": "You are a gifted polyglot and language educator fluent in 50+ languages. You teach grammar intuitively, explain cultural context, provide natural examples, correct errors kindly, and make language learning engaging and effective.",
        "emoji": "🌍",
        "description": "Languages & cultural knowledge"
    },
    "🎓 Socratic Teacher": {
        "prompt": "You are a Socratic teacher who guides students to discover answers through thoughtful questions rather than direct answers. You break down complex topics, challenge assumptions gently, and build deep understanding through dialogue and discovery.",
        "emoji": "🎓",
        "description": "Guided learning through dialogue"
    },
}


def render_persona_selector() -> str:
    """Render persona selection UI. Returns the system prompt for selected persona."""
    st.markdown("#### 🎭 AI Persona")

    selected = st.selectbox(
        "Choose a persona",
        list(AI_PERSONAS.keys()),
        key="persona_selector",
        label_visibility="collapsed"
    )

    persona = AI_PERSONAS[selected]
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #EEF2FF, rgba(15,191,191,0.06));
        border: 1px solid #C7D7FF;
        border-radius: 12px;
        padding: 12px 16px;
        margin-top: 8px;
    ">
        <div style="font-size:0.8rem;color:#3B4B7E;">{persona['emoji']} {persona['description']}</div>
    </div>
    """, unsafe_allow_html=True)

    return persona["prompt"]


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 6: CONVERSATION SEARCH
# ──────────────────────────────────────────────────────────────────────────────

def search_conversations(sessions: dict, query: str) -> List[Dict]:
    """Search across all sessions for a query string."""
    if not query or len(query) < 2:
        return []

    results = []
    query_lower = query.lower()

    for session_name, history in sessions.items():
        for i, msg in enumerate(history):
            content = msg.get("content", "")
            if not isinstance(content, str):
                continue
            if query_lower in content.lower():
                # Extract snippet around match
                idx = content.lower().find(query_lower)
                start = max(0, idx - 60)
                end   = min(len(content), idx + 120)
                snippet = ("…" if start > 0 else "") + content[start:end] + ("…" if end < len(content) else "")

                results.append({
                    "session": session_name,
                    "msg_index": i,
                    "role": msg.get("role", "user"),
                    "snippet": snippet,
                    "ts": msg.get("ts", ""),
                })

    return results[:20]  # Max 20 results


def render_search_panel(sessions: dict):
    """Render conversation search UI."""
    st.markdown("#### 🔍 Search Conversations")
    query = st.text_input("Search across all chats", placeholder="Type to search…", key="search_query")

    if query:
        results = search_conversations(sessions, query)
        if results:
            st.markdown(f"*Found {len(results)} result(s) for **\"{query}\"***")
            for r in results:
                emoji = "🧑‍💼" if r["role"] == "user" else "💠"
                highlighted = r["snippet"].replace(
                    query, f"**{query}**"
                )
                st.markdown(f"""
                <div style="
                    background:#F0F4FF; border:1px solid #C7D7FF;
                    border-radius:10px; padding:12px 16px; margin-bottom:8px;
                ">
                    <div style="font-size:0.72rem;color:#7A8BB0;margin-bottom:4px;">
                        {emoji} {r['role'].title()} · {r['session']} {' · ' + r['ts'] if r['ts'] else ''}
                    </div>
                    <div style="font-size:0.88rem;color:#0D1B4B;line-height:1.5;">{highlighted}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown(f"*No results found for **\"{query}\"***")


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 7: SMART RESPONSE ACTIONS
# ──────────────────────────────────────────────────────────────────────────────

RESPONSE_ACTIONS = [
    ("📋 Summarize",    "Please provide a concise bullet-point summary of your last response."),
    ("🔍 Expand",       "Please expand on your last response with more detail, examples, and depth."),
    ("💡 Simplify",     "Please explain your last response as if I'm a complete beginner with no technical background."),
    ("🌐 Translate",    "Please translate your last response to Hindi."),
    ("💻 Show Code",    "Based on your last response, provide a working code implementation with comments."),
    ("🎯 Key Points",   "Extract exactly 5 key actionable takeaways from your last response."),
    ("⚡ Shorter",      "Give me a much shorter version of your last response — maximum 3 sentences."),
    ("🔄 Alternative",  "Provide an alternative perspective or approach to what you just described."),
]


def render_response_actions() -> Optional[str]:
    """Render quick action buttons for the last response. Returns action prompt or None."""
    st.markdown("**⚡ Quick Actions for Last Response:**")
    cols = st.columns(4)
    for i, (label, prompt) in enumerate(RESPONSE_ACTIONS):
        with cols[i % 4]:
            if st.button(label, key=f"action_{i}", use_container_width=True):
                return prompt
    return None


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 8: IMAGE GENERATION SETTINGS
# ──────────────────────────────────────────────────────────────────────────────

IMAGE_STYLES = {
    "🎨 Realistic":      "photorealistic, highly detailed, professional photography, 8K",
    "🖼️ Oil Painting":  "oil painting, classical art style, rich colors, canvas texture, masterpiece",
    "✏️ Sketch":         "pencil sketch, detailed line art, black and white, professional illustration",
    "🌈 Anime":          "anime style, vibrant colors, Studio Ghibli inspired, beautiful",
    "🚀 Sci-Fi":         "science fiction, cyberpunk, futuristic, neon lights, ultra detailed",
    "🎭 Fantasy":        "fantasy art, magical, epic, high fantasy, digital painting",
    "📸 Portrait":       "professional portrait photography, studio lighting, bokeh, DSLR",
    "🌿 Watercolor":     "watercolor painting, soft colors, artistic, delicate brushstrokes",
    "🏛️ 3D Render":     "3D render, octane render, ultra realistic, studio lighting, detailed",
    "🎪 Cartoon":        "cartoon style, colorful, fun, Pixar-like, detailed",
}

IMAGE_MOODS = {
    "🌟 Epic":       "dramatic lighting, epic composition, cinematic",
    "☁️ Dreamy":     "soft lighting, ethereal, dreamy atmosphere",
    "⚡ Dynamic":    "action shot, motion blur, energetic",
    "🌙 Dark":       "dark atmosphere, dramatic shadows, noir",
    "🌞 Bright":     "bright and cheerful, natural light, vivid",
    "🌿 Natural":    "natural light, organic, peaceful",
}


def build_enhanced_image_prompt(base_prompt: str, style: str, mood: str, quality: str = "ultra") -> str:
    """Build an enhanced image prompt with style and mood modifiers."""
    style_modifier = IMAGE_STYLES.get(style, "")
    mood_modifier  = IMAGE_MOODS.get(mood, "")
    quality_tag    = "masterpiece, best quality, ultra detailed, 8K" if quality == "ultra" else "high quality"
    return f"{base_prompt}, {style_modifier}, {mood_modifier}, {quality_tag}"


def render_image_settings() -> Tuple[str, str]:
    """Render image style/mood selectors. Returns (style, mood)."""
    col1, col2 = st.columns(2)
    with col1:
        style = st.selectbox("Image Style", list(IMAGE_STYLES.keys()), key="img_style")
    with col2:
        mood = st.selectbox("Mood", list(IMAGE_MOODS.keys()), key="img_mood")
    return style, mood


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 9: CHAT STATISTICS & INSIGHTS
# ──────────────────────────────────────────────────────────────────────────────

def get_chat_insights(history: list) -> Dict[str, Any]:
    """Generate insights from a single chat session."""
    if not history:
        return {}

    user_msgs  = [m for m in history if m.get("role") == "user"]
    ai_msgs    = [m for m in history if m.get("role") == "assistant"]
    all_words  = []

    for m in user_msgs:
        content = m.get("content", "")
        if isinstance(content, str):
            all_words.extend(content.lower().split())

    # Question rate
    questions = sum(1 for m in user_msgs if "?" in str(m.get("content", "")))
    question_rate = round(questions / max(len(user_msgs), 1) * 100)

    # Avg message length
    user_lengths = [len(str(m.get("content", ""))) for m in user_msgs]
    avg_user_len = round(sum(user_lengths) / max(len(user_lengths), 1))

    ai_lengths = [len(str(m.get("content", ""))) for m in ai_msgs]
    avg_ai_len = round(sum(ai_lengths) / max(len(ai_lengths), 1))

    return {
        "total_exchanges":   min(len(user_msgs), len(ai_msgs)),
        "question_rate":     question_rate,
        "avg_user_length":   avg_user_len,
        "avg_ai_length":     avg_ai_len,
        "engagement_score":  min(100, question_rate + min(50, avg_user_len // 10)),
    }


def render_chat_insights(history: list):
    """Render chat insights panel."""
    insights = get_chat_insights(history)
    if not insights:
        st.info("Start a conversation to see insights!")
        return

    st.markdown("#### 💡 Chat Insights")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Exchanges", insights.get("total_exchanges", 0))
    with c2:
        st.metric("Question Rate", f"{insights.get('question_rate', 0)}%")
    with c3:
        score = insights.get("engagement_score", 0)
        label = "🔥 High" if score > 60 else ("⚡ Medium" if score > 30 else "💤 Low")
        st.metric("Engagement", label)

    st.markdown(f"""
    <div style="background:#F0F4FF;border:1px solid #C7D7FF;border-radius:10px;padding:12px 16px;margin-top:8px;">
        <div style="font-size:0.8rem;color:#3B4B7E;">
            📝 Avg. your message: <strong>{insights['avg_user_length']} chars</strong> &nbsp;|&nbsp;
            💠 Avg. AI response: <strong>{insights['avg_ai_length']} chars</strong>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 10: NOTIFICATION / TOAST SYSTEM
# ──────────────────────────────────────────────────────────────────────────────

def show_toast(message: str, emoji: str = "✦", duration: int = 3):
    """Display a toast notification."""
    placeholder = st.empty()
    placeholder.markdown(f"""
    <div class="toast">
        <span style="font-size:1.1rem;">{emoji}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)
    time.sleep(duration)
    placeholder.empty()


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 11: THEME CUSTOMIZER CSS GENERATOR
# ──────────────────────────────────────────────────────────────────────────────

THEME_PRESETS = {
    "🔵 Ocean Blue (Default)": {
        "--blue-500":    "#2B5CE6",
        "--accent-teal": "#0FBFBF",
        "--bg-primary":  "#F0F4FF",
        "--navy":        "#0D1B4B",
    },
    "🟢 Forest Green": {
        "--blue-500":    "#16A34A",
        "--accent-teal": "#0891B2",
        "--bg-primary":  "#F0FDF4",
        "--navy":        "#14532D",
    },
    "🟣 Royal Purple": {
        "--blue-500":    "#7C3AED",
        "--accent-teal": "#EC4899",
        "--bg-primary":  "#FAF5FF",
        "--navy":        "#3B0764",
    },
    "🟠 Sunset Orange": {
        "--blue-500":    "#EA580C",
        "--accent-teal": "#D97706",
        "--bg-primary":  "#FFF7ED",
        "--navy":        "#7C2D12",
    },
    "⚫ Midnight": {
        "--blue-500":    "#6366F1",
        "--accent-teal": "#22D3EE",
        "--bg-primary":  "#F8FAFF",
        "--navy":        "#0F0F1A",
    },
}


def generate_theme_css(theme_vars: dict) -> str:
    """Generate CSS override for a given theme."""
    vars_str = "\n".join(f"    {k}: {v};" for k, v in theme_vars.items())
    return f"<style>:root {{\n{vars_str}\n}}</style>"


def render_theme_selector() -> str:
    """Render theme selector. Returns CSS override string."""
    theme_name = st.selectbox(
        "Color Theme",
        list(THEME_PRESETS.keys()),
        key="theme_selector"
    )
    preset = THEME_PRESETS[theme_name]
    return generate_theme_css(preset)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 12: MULTI-TURN CONTEXT MANAGER
# ──────────────────────────────────────────────────────────────────────────────

def compress_history(history: list, max_messages: int = 20, max_chars: int = 12000) -> list:
    """
    Intelligently compress conversation history to fit token limits.
    Keeps the most recent messages and summarizes older ones if needed.
    """
    if len(history) <= max_messages:
        return history

    # Keep the last N messages
    recent = history[-max_messages:]

    # Calculate total chars
    total_chars = sum(len(str(m.get("content", ""))) for m in recent)

    if total_chars <= max_chars:
        return recent

    # Further trim if still too long
    while recent and total_chars > max_chars:
        removed = recent.pop(0)
        total_chars -= len(str(removed.get("content", "")))

    return recent


def build_context_summary(history: list) -> str:
    """Build a brief summary of older conversation context."""
    if len(history) < 6:
        return ""

    older = history[:-4]
    topics = []
    for msg in older:
        if msg.get("role") == "user":
            content = str(msg.get("content", ""))
            if content:
                topics.append(content[:50] + "…" if len(content) > 50 else content)

    if not topics:
        return ""

    return f"[Earlier context: discussed {'; '.join(topics[:3])}]"


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 13: CONTENT SAFETY CHECKER (Client-side Keywords)
# ──────────────────────────────────────────────────────────────────────────────

SENSITIVE_PATTERNS = [
    r'\b(password|secret|api.?key|token|credential)\b',
    r'\b\d{16}\b',  # Credit card pattern
    r'\b\d{3}-\d{2}-\d{4}\b',  # SSN pattern
]


def check_sensitive_content(text: str) -> List[str]:
    """Detect potentially sensitive information in user input."""
    warnings = []
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            if 'password' in pattern or 'key' in pattern:
                warnings.append("⚠️ Possible credentials detected — avoid sharing passwords or API keys")
            elif r'\d{16}' in pattern:
                warnings.append("⚠️ Possible credit card number detected — do not share financial data")
            elif 'SSN' in pattern or r'\d{3}-\d{2}' in pattern:
                warnings.append("⚠️ Possible personal ID number detected — protect your identity")
    return warnings


def render_safety_warnings(text: str):
    """Display safety warnings if sensitive content detected."""
    warnings = check_sensitive_content(text)
    for w in warnings:
        st.warning(w)


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 14: RANDOM INSPIRATION PROMPTS
# ──────────────────────────────────────────────────────────────────────────────

INSPIRATION_PROMPTS = [
    "What would happen if gravity suddenly became 10x stronger for 24 hours?",
    "Design an AI-powered city of the future — what problems does it solve?",
    "Write a mystery story where the detective is an AI and the crime is digital.",
    "Explain blockchain technology using only a pizza delivery analogy.",
    "What are 5 business ideas that could only work in India?",
    "Create a 30-day learning plan to master machine learning from scratch.",
    "Write a speech that would inspire a team through a major company crisis.",
    "If you could redesign the human education system from scratch, what would it look like?",
    "What are the ethical implications of having AI make medical diagnoses?",
    "Create a startup pitch for a company that uses AI to reduce food waste.",
    "Explain the concept of time dilation in a way that gives me goosebumps.",
    "What would Mahatma Gandhi think about social media if he were alive today?",
    "Design a mobile app that helps people build better daily habits — describe every feature.",
    "Write a short film script about the last human programmer in an AI-dominated world.",
    "What are 10 unconventional ways to learn a new language in just 90 days?",
]


def get_random_inspiration() -> str:
    """Return a random inspiration prompt."""
    return random.choice(INSPIRATION_PROMPTS)


def render_inspiration_widget():
    """Render a random inspiration prompt button."""
    col1, col2 = st.columns([3, 1])
    with col2:
        if st.button("🎲 Inspire Me!", use_container_width=True, key="inspire_btn"):
            st.session_state["inspiration_prompt"] = get_random_inspiration()

    with col1:
        if "inspiration_prompt" in st.session_state:
            st.info(f"💡 {st.session_state['inspiration_prompt']}")
            if st.button("Use this prompt →", key="use_inspiration"):
                return st.session_state.pop("inspiration_prompt")

    return None


# ──────────────────────────────────────────────────────────────────────────────
# FEATURE MODULE 15: WELCOME ONBOARDING FLOW
# ──────────────────────────────────────────────────────────────────────────────

def render_onboarding_tips():
    """Render first-time user tips."""
    if st.session_state.get("onboarding_done"):
        return

    st.markdown("""
    <div style="
        background: linear-gradient(135deg, #EEF2FF 0%, rgba(15,191,191,0.06) 100%);
        border: 1px solid #C7D7FF;
        border-radius: 16px;
        padding: 20px 24px;
        margin-bottom: 24px;
        animation: fadeSlideDown 0.6s ease both;
    ">
        <div style="font-weight:700;font-size:1rem;color:#0D1B4B;margin-bottom:12px;">
            ✦ Welcome to HEXALOY v7.0
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;">
            <div style="font-size:0.82rem;color:#3B4B7E;">⌨️ <strong>Ctrl+K</strong> — Focus input</div>
            <div style="font-size:0.82rem;color:#3B4B7E;">🎨 Say "draw" or "image" to generate art</div>
            <div style="font-size:0.82rem;color:#3B4B7E;">📸 Upload images for vision analysis</div>
            <div style="font-size:0.82rem;color:#3B4B7E;">🎛️ Switch models in the sidebar</div>
            <div style="font-size:0.82rem;color:#3B4B7E;">⚡ Click chips for quick prompts</div>
            <div style="font-size:0.82rem;color:#3B4B7E;">📥 Export chats as MD/JSON/HTML</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("✓ Got it, let's go!", key="onboarding_dismiss"):
        st.session_state["onboarding_done"] = True
        st.rerun()


# ──────────────────────────────────────────────────────────────────────────────
# MODULE EXPORTS / USAGE REFERENCE
# ──────────────────────────────────────────────────────────────────────────────
"""
INTEGRATION GUIDE — hexaloy_features.py
==========================================

To integrate these features into your main app.py:

    from hexaloy_features import (
        inject_keyboard_shortcuts,
        render_export_panel,
        render_analytics_panel,
        render_prompt_templates_panel,
        render_persona_selector,
        render_search_panel,
        render_response_actions,
        render_image_settings,
        render_chat_insights,
        show_toast,
        render_theme_selector,
        compress_history,
        render_safety_warnings,
        render_inspiration_widget,
        render_onboarding_tips,
        build_enhanced_image_prompt,
    )

Usage examples:

    # At the top of your app, inject JS enhancements:
    inject_keyboard_shortcuts()

    # In sidebar for theme:
    theme_css = render_theme_selector()
    st.markdown(theme_css, unsafe_allow_html=True)

    # In sidebar for persona:
    system_prompt = render_persona_selector()

    # In sidebar for search:
    render_search_panel(st.session_state.sessions)

    # Before sending a message:
    render_safety_warnings(user_input)

    # Show analytics in an expander:
    with st.expander("📊 Analytics"):
        render_analytics_panel(st.session_state.sessions)

    # Show export panel:
    with st.expander("📥 Export"):
        render_export_panel(current_history, session_name)

    # Show onboarding on first visit:
    render_onboarding_tips()

    # After displaying messages, show response actions:
    action_prompt = render_response_actions()
    if action_prompt:
        # inject as new user message

    # Inspiration widget:
    inspired = render_inspiration_widget()
    if inspired:
        # inject as new user message

==========================================
"""
