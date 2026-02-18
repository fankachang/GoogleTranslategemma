namespace TranslateGemma.Models
{
    public class TranslationResponse
    {
        public string TranslatedText { get; set; } = string.Empty;
        public string? DetectedSourceLang { get; set; }
        public string? ModelName { get; set; }
    }
}
