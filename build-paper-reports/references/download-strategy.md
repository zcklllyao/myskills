# 论文 PDF 下载与校验策略

## 来源优先级

1. 会议、期刊或出版社官方论文页。
2. arXiv 的摘要页与对应 PDF。
3. 作者主页、项目主页或高校机构仓储。

搜索结果只用于定位，不能把搜索摘要当作论文证据。避开来源不明的转载站、绕过付费墙的镜像和标题相近但内容不同的文件。

## 下载前核对

- 标题和作者与用户所指论文一致。
- 年份、版本、会议状态能被可靠来源支持。
- URL 指向 PDF，或官方落地页明确提供 PDF 链接。
- 同名论文存在时，用作者、摘要和任务定义消歧。

## Windows 下载顺序

优先使用 `scripts/download_pdf.py`。它先写入 `.part`，确认 PDF 文件头和最低大小后再原子替换最终文件。

如果站点不接受 Python 客户端，可使用 PowerShell：

```powershell
Invoke-WebRequest -UseBasicParsing -Uri "<url>" -OutFile "<target>.part" -TimeoutSec 120
```

大文件或连接不稳定时可使用 BITS：

```powershell
Start-BitsTransfer -Source "<url>" -Destination "<target>.part" -DisplayName "Codex-Paper-PDF"
```

仅在 `.part` 通过校验后改名为 `.pdf`。若环境限制网络访问，按运行环境要求申请网络权限，不要用网页内容伪装成本地 PDF。

## 完整性验证

至少检查：

- 文件不是空文件，大小合理。
- 前 1024 字节包含 `%PDF-`，而不是 HTML 登录页或错误页。
- PDF 解析器能打开文件且页数大于 0。
- 文件没有无法解除的加密。
- 抽样页能正常读取；纯扫描件允许无文本，但后续要用页面渲染或 OCR。

运行：

```powershell
python scripts/validate_pdfs.py "<pdf-or-directory>"
```

批量任务中，逐篇记录下载来源和验证结果，失败项不得阻塞其他独立论文。

## 版本与版权

优先保留论文的公开合法版本。报告中区分预印本、已接收版本和正式出版版本。不要根据未来年份或用户提供的标签直接断言论文已被某会议接收。
