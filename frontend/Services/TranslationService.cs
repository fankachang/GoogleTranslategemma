using System.Net.Http;
using System.Net.Http.Json;
using System.Threading.Tasks;

public class TranslationService : ITranslationService
{
    private readonly HttpClient _http;
    public TranslationService(HttpClient http) { _http = http; }

    public async Task<TranslationResponse?> TranslateAsync(TranslationRequest req)
    {
        var resp = await _http.PostAsJsonAsync("/api/translate", req);
        if (!resp.IsSuccessStatusCode)
        {
            return null;
        }
        return await resp.Content.ReadFromJsonAsync<TranslationResponse>();
    }
}
