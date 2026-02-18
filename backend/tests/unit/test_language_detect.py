from backend.src.language_detect import detect_language


def test_detect_chinese():
    assert detect_language("你好，世界") == 'zh-TW'


def test_detect_english():
    assert detect_language("Hello, world!") == 'en'


def test_detect_mixed():
    assert detect_language("Hello 世界") == 'zh-TW'
