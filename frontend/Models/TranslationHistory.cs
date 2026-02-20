using System;

namespace TranslateGemma.Models
{
    public class TranslationHistory
    {
        public Guid Id { get; set; } = Guid.NewGuid();
        public string OriginalText { get; set; } = string.Empty;
        public string TranslatedText { get; set; } = string.Empty;
        public string SourceLang { get; set; } = string.Empty;
        public string TargetLang { get; set; } = string.Empty;
        public bool Detected { get; set; }
        public DateTime Timestamp { get; set; } = DateTime.Now;     // 使用者送出時間
        public DateTime CompletedAt { get; set; } = DateTime.MinValue; // 回譯 / 錯誤 / 取消完成時間
        public bool IsError { get; set; }
        public string? ErrorMessage { get; set; }
        public bool IsPending { get; set; }
    }
}
