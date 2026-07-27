$word = New-Object -ComObject Word.Application
$word.Visible = $false

# 转换BPM32FC积算仪协议说明
$doc1 = $word.Documents.Open("d:\work\CTI\流量计\BPM32FC系列积算仪MODBUS RTU协议说明(1).doc")
$doc1.Content.Text | Out-File -FilePath "d:\work\CTI\流量计\BPM32FC_modbus.txt" -Encoding UTF8
$doc1.Close()

# 转换微小流量计485通讯协议
$doc2 = $word.Documents.Open("d:\work\CTI\流量计\微小流量计485通讯（Modbus协议）(4).docx")
$doc2.Content.Text | Out-File -FilePath "d:\work\CTI\流量计\微小流量计_485.txt" -Encoding UTF8
$doc2.Close()

$word.Quit()
Write-Output "转换完成"
