using System.Collections.Generic;

namespace TranslateGemma.Models
{
    public class GlossaryEntry
    {
        public string Source { get; set; } = string.Empty;
        public string Target { get; set; } = string.Empty;
        public string SourceLang { get; set; } = string.Empty;
        public string TargetLang { get; set; } = string.Empty;
        public bool CaseSensitive { get; set; }
    }

    public class GlossaryResult
    {
        public bool Enabled { get; set; }
        public List<GlossaryEntry> Entries { get; set; } = new();
    }
}
