using System;
using System.Collections.Generic;
using System.IO;
using System.Net.Http;
using System.Net.Http.Json;
using System.Runtime.CompilerServices;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using TranslateGemma.Models;

namespace TranslateGemma.Services
{
    public class TranslationService : ITranslationService
    {
        private readonly HttpClient _http;

        public TranslationService(HttpClient http)
        {
            _http = http;
        }

        public async Task<TranslationResponse?> TranslateAsync(TranslationRequest req, CancellationToken ct = default)
        {
            try
            {
                var resp = await _http.PostAsJsonAsync("/api/translate", new
                {
                    text = req.Text,
                    source_lang = req.SourceLang,
                    target_lang = req.TargetLang,
                    stream = false,
                }, ct);

                if (!resp.IsSuccessStatusCode)
                    return null;

                return await resp.Content.ReadFromJsonAsync<TranslationResponse>(cancellationToken: ct);
            }
            catch
            {
                return null;
            }
        }

        public async IAsyncEnumerable<StreamToken> TranslateStreamAsync(
            TranslationRequest req,
            [EnumeratorCancellation] CancellationToken ct = default)
        {
            HttpResponseMessage resp;
            try
            {
                resp = await _http.PostAsJsonAsync("/api/translate", new
                {
                    text = req.Text,
                    source_lang = req.SourceLang,
                    target_lang = req.TargetLang,
                    stream = true,
                }, ct);
            }
            catch (Exception ex)
            {
                yield return new StreamToken("", true, Error: ex.Message);
                yield break;
            }

            if (!resp.IsSuccessStatusCode)
            {
                yield return new StreamToken("", true, Error: $"HTTP {resp.StatusCode}");
                yield break;
            }

            using var stream = await resp.Content.ReadAsStreamAsync(ct);
            using var reader = new StreamReader(stream);

            while (!reader.EndOfStream && !ct.IsCancellationRequested)
            {
                var line = await reader.ReadLineAsync();
                if (string.IsNullOrEmpty(line)) continue;
                if (!line.StartsWith("data: ")) continue;

                var json = line[6..];
                StreamToken token;
                try
                {
                    using var doc = JsonDocument.Parse(json);
                    var root = doc.RootElement;
                    var done = root.TryGetProperty("done", out var doneEl) && doneEl.GetBoolean();
                    var tokenStr = root.TryGetProperty("token", out var tokEl) ? tokEl.GetString() ?? "" : "";
                    var error = root.TryGetProperty("error", out var errEl) ? errEl.GetString() : null;
                    var sourceLang = root.TryGetProperty("source_lang", out var slEl) ? slEl.GetString() : null;
                    var targetLang = root.TryGetProperty("target_lang", out var tlEl) ? tlEl.GetString() : null;
                    var detected = root.TryGetProperty("detected", out var detEl) && detEl.GetBoolean();
                    token = new StreamToken(tokenStr, done, sourceLang, targetLang, detected, error);
                }
                catch
                {
                    token = new StreamToken("", true, Error: "解析錯誤");
                }

                yield return token;
                if (token.Done) break;
            }
        }
    }
}

