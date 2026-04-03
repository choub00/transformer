param(
    [Parameter(Mandatory = $false)]
    [string]$InputPath = "D:\transformer\thesis\基于Transformer的股票预测系统_论文初稿.docx",

    [Parameter(Mandatory = $false)]
    [string]$OutputPath = "D:\transformer\thesis\基于Transformer的股票预测系统_论文初稿_公式修复版.docx",

    [switch]$Visible
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Get-ParagraphText {
    param([object]$Paragraph)

    $text = $Paragraph.Range.Text
    if ($text.Length -gt 0 -and ($text[-1] -eq "`r" -or $text[-1] -eq [char]7)) {
        $text = $text.Substring(0, $text.Length - 1)
    }
    return $text.Trim()
}

function Test-IsDisplayEquationParagraph {
    param([string]$Text)

    if ([string]::IsNullOrWhiteSpace($Text)) {
        return $false
    }

    if ($Text -match "[\u4e00-\u9fff]") {
        return $false
    }

    $latexSignals = @(
        "\\frac", "\\math", "\\hat", "\\bar", "\\tilde", "\\sum", "\\prod",
        "\\sqrt", "\\left", "\\right", "\\text", "\\mathrm", "\\mathbf",
        "\\begin", "\\end", "\\cdot", "\\top", "\\in", "\\cup", "\\cap"
    )

    foreach ($signal in $latexSignals) {
        if ($Text.Contains($signal)) {
            return $true
        }
    }

    if ($Text.StartsWith("\")) {
        return $true
    }

    if ($Text -match "^[A-Za-z0-9_\^\{\}\(\)\[\]\+\-\=\.,:\|<>\s\\]+$" -and $Text.Length -ge 8) {
        return $true
    }

    return $false
}

function Convert-RangeToEquation {
    param(
        [object]$Document,
        [object]$Range,
        [string]$Latex
    )

    $Range.Text = $Latex
    $math = $Document.OMaths.Add($Range)
    $math.BuildUp()
}

if (-not (Test-Path -LiteralPath $InputPath)) {
    throw "Input file not found: $InputPath"
}

$word = $null
$doc = $null

try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = [bool]$Visible
    $word.DisplayAlerts = 0

    $doc = $word.Documents.Open($InputPath)

    $displayConverted = 0
    $inlineConverted = 0

    for ($p = $doc.Paragraphs.Count; $p -ge 1; $p--) {
        $paragraph = $doc.Paragraphs.Item($p)
        $text = Get-ParagraphText -Paragraph $paragraph

        if ([string]::IsNullOrWhiteSpace($text)) {
            continue
        }

        $matches = [regex]::Matches($text, '(?<!\\)\$(.+?)(?<!\\)\$')
        if ($matches.Count -gt 0) {
            for ($m = $matches.Count - 1; $m -ge 0; $m--) {
                $match = $matches[$m]
                $latex = $match.Groups[1].Value
                $start = $paragraph.Range.Start + $match.Index
                $end = $start + $match.Length
                $range = $doc.Range($start, $end)
                Convert-RangeToEquation -Document $doc -Range $range -Latex $latex
                $inlineConverted++
            }
            continue
        }

        if (Test-IsDisplayEquationParagraph -Text $text) {
            $end = $paragraph.Range.End
            if ($end -gt $paragraph.Range.Start) {
                $range = $doc.Range($paragraph.Range.Start, $end - 1)
                Convert-RangeToEquation -Document $doc -Range $range -Latex $text
                $displayConverted++
            }
        }
    }

    $doc.SaveAs([ref]$OutputPath)
    Write-Output "DONE"
    Write-Output "InputPath=$InputPath"
    Write-Output "OutputPath=$OutputPath"
    Write-Output "InlineConverted=$inlineConverted"
    Write-Output "DisplayConverted=$displayConverted"
}
finally {
    if ($doc -ne $null) {
        $doc.Close()
    }
    if ($word -ne $null) {
        $word.Quit()
    }
}
