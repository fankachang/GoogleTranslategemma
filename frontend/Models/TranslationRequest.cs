using System.Collections.Generic;
using System.ComponentModel.DataAnnotations;

namespace TranslateGemma.Models
{
    public class TranslationRequest
    {
        [Required]
        [StringLength(5000, MinimumLength = 1)]
        public string Text { get; set; } = string.Empty;

        public string? SourceLang { get; set; }
        public string? TargetLang { get; set; }
        public bool Stream { get; set; } = false;

        public List<GlossaryEntry>? Glossary { get; set; }
    }
}
