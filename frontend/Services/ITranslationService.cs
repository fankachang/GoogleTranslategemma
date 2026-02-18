using System;
using System.Collections.Generic;
using System.Threading;
using System.Threading.Tasks;
using TranslateGemma.Models;

namespace TranslateGemma.Services
{
    public interface ITranslationService
    {
        Task<TranslationResponse?> TranslateAsync(TranslationRequest req, CancellationToken ct = default);
        IAsyncEnumerable<StreamToken> TranslateStreamAsync(TranslationRequest req, CancellationToken ct = default);
    }

    public record StreamToken(string Token, bool Done, string? SourceLang = null, string? TargetLang = null, bool Detected = false, string? Error = null);
}

