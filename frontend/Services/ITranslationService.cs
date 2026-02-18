using System.Threading.Tasks;

public interface ITranslationService
{
    Task<TranslationResponse?> TranslateAsync(TranslationRequest req);
}
