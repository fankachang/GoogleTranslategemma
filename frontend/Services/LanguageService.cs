using System.Collections.Generic;
using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;
using TranslateGemma.Models;

namespace TranslateGemma.Services
{
    public class LanguageService
    {
        private readonly HttpClient _http;
        private List<Language>? _cache;

        public LanguageService(HttpClient http)
        {
            _http = http;
        }

        public async Task<List<Language>> GetLanguagesAsync()
        {
            if (_cache != null)
                return _cache;

            try
            {
                _cache = await _http.GetFromJsonAsync<List<Language>>("/api/languages")
                         ?? new List<Language>();
            }
            catch
            {
                // 網路失敗時回傳預設語言清單
                _cache = new List<Language>
                {
                    new Language { Code = "zh-TW", Name = "Chinese (Traditional)", NativeName = "繁體中文" },
                    new Language { Code = "en",    Name = "English",               NativeName = "English"  },
                };
            }

            return _cache;
        }

        public void InvalidateCache() => _cache = null;
    }
}
