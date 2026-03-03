from backend.src.language_detect import detect_language


def test_detect_chinese():
    assert detect_language("你好，世界") == 'zh-TW'


def test_detect_english():
    assert detect_language("Hello, world!") == 'en'


def test_detect_mixed_chinese_dominant():
    """中文比例 ≥ 20%，判定為 zh-TW"""
    assert detect_language("Hello 世界") == 'zh-TW'


def test_detect_mixed_english_dominant():
    """英文為主體，少量中文（< 20%），判定為 en"""
    # "The server is running" = 17 Latin, "請確認" = 3 CJK → 3/20 = 15%
    assert detect_language("The server is running 請確認") == 'en'


def test_detect_mixed_chinese_heavy():
    """大量中文夾雜英文縮寫，應判為 zh-TW"""
    # "這個API用來翻譯文字" = 9 CJK, "API" = 3 Latin → 9/12 = 75%
    assert detect_language("這個API用來翻譯文字") == 'zh-TW'


def test_detect_empty():
    assert detect_language("") == 'en'


def test_detect_custom_threshold():
    """自訂高門檻：需超過 50% CJK 才算中文"""
    # "Hello 世界" = 2 CJK, 5 Latin → 2/7 ≈ 29%，低於 0.5 → en
    assert detect_language("Hello 世界", cjk_threshold=0.5) == 'en'
    # "你好 Hi" = 2 CJK, 2 Latin → 2/4 = 50%，達到 0.5 → zh-TW
    assert detect_language("你好 Hi", cjk_threshold=0.5) == 'zh-TW'
