"""
AegisSphere — Multilingual Translation Engine
==============================================
Dynamic translation support for safety notices, menu boards, allergen
disclosures, and transportation guides to serve a global audience.

Supports 10 primary languages and provides WCAG 3.1.2 compliant
HTML lang attribute management for programmatic language declaration.

In production, translation is handled by the Gemini API. This module
provides the routing logic, template management, and fallback
translations for offline operation.
"""

from __future__ import annotations

from typing import Optional

from app.schemas import TranslationRequest, TranslationResponse


# ---------------------------------------------------------------------------
# Supported Languages
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: dict[str, str] = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "pt": "Portuguese",
    "ar": "Arabic",
    "zh": "Mandarin Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "de": "German",
    "hi": "Hindi",
}

# BCP 47 language tags for HTML lang attribute (WCAG 3.1.2)
_LANG_TAGS: dict[str, str] = {
    "en": "en",
    "es": "es",
    "fr": "fr",
    "pt": "pt-BR",
    "ar": "ar",
    "zh": "zh-Hans",
    "ja": "ja",
    "ko": "ko",
    "de": "de",
    "hi": "hi",
}


# ---------------------------------------------------------------------------
# Pre-translated Safety Templates
# ---------------------------------------------------------------------------

_SAFETY_TRANSLATIONS: dict[str, dict[str, str]] = {
    "evacuation_notice": {
        "en": "⚠️ EVACUATION NOTICE: Please proceed to the nearest exit immediately. Follow steward instructions.",
        "es": "⚠️ AVISO DE EVACUACIÓN: Diríjase a la salida más cercana inmediatamente. Siga las instrucciones del personal.",
        "fr": "⚠️ AVIS D'ÉVACUATION: Veuillez vous diriger vers la sortie la plus proche immédiatement. Suivez les instructions du personnel.",
        "pt": "⚠️ AVISO DE EVACUAÇÃO: Dirija-se à saída mais próxima imediatamente. Siga as instruções dos funcionários.",
        "ar": "⚠️ إشعار إخلاء: يرجى التوجه إلى أقرب مخرج على الفور. اتبع تعليمات الموظفين.",
        "zh": "⚠️ 疏散通知：请立即前往最近的出口。请遵从工作人员的指示。",
        "ja": "⚠️ 避難通知：直ちに最寄りの出口に向かってください。スタッフの指示に従ってください。",
        "ko": "⚠️ 대피 안내: 즉시 가장 가까운 출구로 이동하세요. 안내 요원의 지시를 따르세요.",
        "de": "⚠️ EVAKUIERUNGSHINWEIS: Begeben Sie sich sofort zum nächsten Ausgang. Folgen Sie den Anweisungen des Personals.",
        "hi": "⚠️ निकासी सूचना: कृपया तुरंत निकटतम निकास की ओर जाएं। कर्मचारियों के निर्देशों का पालन करें।",
    },
    "crowd_alert": {
        "en": "🚨 CROWD ALERT: This area is experiencing high density. Please follow alternate routes displayed on screens.",
        "es": "🚨 ALERTA DE MULTITUD: Esta área tiene alta densidad. Siga las rutas alternativas en las pantallas.",
        "fr": "🚨 ALERTE FOULE: Cette zone connaît une forte densité. Suivez les itinéraires alternatifs affichés.",
        "pt": "🚨 ALERTA DE MULTIDÃO: Esta área está com alta densidade. Siga as rotas alternativas exibidas nas telas.",
        "ar": "🚨 تنبيه ازدحام: هذه المنطقة تشهد كثافة عالية. يرجى اتباع المسارات البديلة المعروضة.",
        "zh": "🚨 人群警报：该区域人流密度较高。请按屏幕显示的替代路线行走。",
        "ja": "🚨 混雑警報：このエリアは混雑しています。画面に表示された代替ルートに従ってください。",
        "ko": "🚨 인파 경보: 이 구역은 밀집도가 높습니다. 화면에 표시된 대체 경로를 따르세요.",
        "de": "🚨 MENSCHENMENGE-WARNUNG: In diesem Bereich herrscht hohe Dichte. Folgen Sie den alternativen Routen auf den Bildschirmen.",
        "hi": "🚨 भीड़ चेतावनी: इस क्षेत्र में उच्च घनत्व है। स्क्रीन पर प्रदर्शित वैकल्पिक मार्गों का अनुसरण करें।",
    },
    "weather_warning": {
        "en": "🌧️ WEATHER WARNING: Severe weather approaching. Please move to covered areas and await further instructions.",
        "es": "🌧️ ALERTA METEOROLÓGICA: Clima severo acercándose. Muévase a áreas cubiertas y espere instrucciones.",
        "fr": "🌧️ ALERTE MÉTÉO: Conditions météorologiques sévères à l'approche. Rendez-vous dans les zones couvertes.",
        "pt": "🌧️ ALERTA CLIMÁTICO: Condições climáticas severas se aproximando. Vá para áreas cobertas.",
        "ar": "🌧️ تحذير من الطقس: طقس سيء قادم. انتقل إلى المناطق المغطاة وانتظر التعليمات.",
        "zh": "🌧️ 天气警告：恶劣天气即将到来。请移至有顶棚的区域等待进一步指示。",
        "ja": "🌧️ 気象警報：悪天候が接近中です。屋根のあるエリアに移動し、指示をお待ちください。",
        "ko": "🌧️ 기상 경보: 악천후가 접근 중입니다. 지붕이 있는 구역으로 이동하여 추가 안내를 기다리세요.",
        "de": "🌧️ WETTERWARNUNG: Unwetter nähert sich. Begeben Sie sich in überdachte Bereiche.",
        "hi": "🌧️ मौसम चेतावनी: गंभीर मौसम आ रहा है। कृपया छत वाले क्षेत्रों में जाएं।",
    },
    "accessibility_info": {
        "en": "♿ Wheelchair-accessible routes available. Ask any steward or check the AegisSphere app for step-free directions.",
        "es": "♿ Rutas accesibles para sillas de ruedas disponibles. Consulte la app AegisSphere para direcciones sin escalones.",
        "fr": "♿ Itinéraires accessibles en fauteuil roulant disponibles. Consultez l'app AegisSphere pour les directions sans marches.",
        "pt": "♿ Rotas acessíveis para cadeiras de rodas disponíveis. Consulte o app AegisSphere para rotas sem degraus.",
        "ar": "♿ مسارات مخصصة للكراسي المتحركة متوفرة. استخدم تطبيق AegisSphere للحصول على اتجاهات بدون درج.",
        "zh": "♿ 无障碍路线可用。请向工作人员咨询或查看AegisSphere应用获取无台阶路线。",
        "ja": "♿ 車椅子対応ルートがあります。AegisSphereアプリでバリアフリールートをご確認ください。",
        "ko": "♿ 휠체어 접근 가능 경로 이용 가능. AegisSphere 앱에서 무단차 경로를 확인하세요.",
        "de": "♿ Rollstuhlgerechte Routen verfügbar. Prüfen Sie die AegisSphere-App für stufenfreie Wegbeschreibungen.",
        "hi": "♿ व्हीलचेयर-सुलभ मार्ग उपलब्ध। सीढ़ी-मुक्त दिशाओं के लिए AegisSphere ऐप देखें।",
    },
}


# ---------------------------------------------------------------------------
# Translation Functions
# ---------------------------------------------------------------------------

def get_supported_languages() -> dict[str, str]:
    """Return all supported languages with their display names."""
    return SUPPORTED_LANGUAGES.copy()


def get_html_lang_tag(language_code: str) -> str:
    """
    Get the BCP 47 language tag for HTML lang attribute.
    Required for WCAG 3.1.2 (Language of Parts) compliance.
    """
    return _LANG_TAGS.get(language_code, language_code)


def translate_safety_template(
    template_key: str,
    target_language: str,
) -> Optional[str]:
    """
    Retrieve a pre-translated safety notice.

    Pre-translated templates ensure critical safety messages are always
    available without API dependency.

    Args:
        template_key: Template identifier (e.g., 'evacuation_notice').
        target_language: ISO 639-1 language code.

    Returns:
        Translated safety message, or None if not available.
    """
    template = _SAFETY_TRANSLATIONS.get(template_key)
    if template is None:
        return None
    return template.get(target_language)


def translate_text(request: TranslationRequest) -> TranslationResponse:
    """
    Translate text using pre-built templates or dynamic translation.

    For safety-critical content, uses pre-validated templates.
    For general content, would route to Gemini API in production.

    Args:
        request: Translation request with source text and target language.

    Returns:
        TranslationResponse with translated text and WCAG metadata.
    """
    # Validate target language
    if request.target_language not in SUPPORTED_LANGUAGES:
        return TranslationResponse(
            original_text=request.text,
            translated_text=f"[Translation to '{request.target_language}' not supported. "
                          f"Supported: {', '.join(SUPPORTED_LANGUAGES.keys())}]",
            source_language=request.source_language,
            target_language=request.target_language,
            html_lang_attribute=get_html_lang_tag(request.source_language),
        )

    # Check for pre-translated safety templates first
    text_lower = request.text.lower()
    for template_key, translations in _SAFETY_TRANSLATIONS.items():
        # Check if the input matches an English template
        en_text = translations.get("en", "").lower()
        if en_text and (text_lower in en_text or en_text in text_lower):
            translated = translations.get(request.target_language)
            if translated:
                return TranslationResponse(
                    original_text=request.text,
                    translated_text=translated,
                    source_language=request.source_language,
                    target_language=request.target_language,
                    html_lang_attribute=get_html_lang_tag(request.target_language),
                )

    # For non-template content, provide a structured placeholder
    # In production, this would call the Gemini translation API
    return TranslationResponse(
        original_text=request.text,
        translated_text=(
            f"[{SUPPORTED_LANGUAGES[request.target_language]} translation of: "
            f"'{request.text}']"
        ),
        source_language=request.source_language,
        target_language=request.target_language,
        html_lang_attribute=get_html_lang_tag(request.target_language),
    )
