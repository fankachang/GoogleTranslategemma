namespace TranslateGemma;

public class AppConfig
{
    public string AppTitle { get; set; } = "TranslateGemma";
    /// <summary>
    /// 左上角 Logo 圖片路徑（相對於 wwwroot，例如 /images/logo.png）。
    /// 空白或未設定則不顯示圖示。
    /// </summary>
    public string? AppLogoUrl { get; set; }
    /// <summary>
    /// 對話區與輸入框的內容區塊寬度（佔瀏覽器視窗的百分比）。
    /// 有效範圍 40–100，預設 80。
    /// </summary>
    public int ContentWidthPercent { get; set; } = 80;
}
