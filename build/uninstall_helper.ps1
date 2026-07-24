Add-Type -AssemblyName System.Windows.Forms

$zh = (Get-UICulture).Name -like "zh-*"

$form = New-Object System.Windows.Forms.Form
$form.Text = "SRW Alpha ROM Editor - Uninstall"
$form.Size = New-Object System.Drawing.Size(500,260)
$form.StartPosition = "CenterScreen"
$form.FormBorderStyle = "FixedDialog"
$form.MaximizeBox = $false
$form.MinimizeBox = $false

if ($zh) {
  $labelText = "请选择卸载类型："
} else {
  $labelText = "Select uninstall type:"
}
$label = New-Object System.Windows.Forms.Label
$label.Text = $labelText
$label.Location = New-Object System.Drawing.Point(16,16)
$label.Size = New-Object System.Drawing.Size(460,20)
$label.Font = New-Object System.Drawing.Font("Segoe UI",10,[System.Drawing.FontStyle]::Bold)
$form.Controls.Add($label)

$r1 = New-Object System.Windows.Forms.RadioButton
if ($zh) {
  $r1.Text = "普通卸载 — 保留 .venv/、cache/ 和用户数据"
} else {
  $r1.Text = "Normal — keep .venv, cache, and user data"
}
$r1.Location = New-Object System.Drawing.Point(32,48)
$r1.Size = New-Object System.Drawing.Size(440,24)
$r1.Checked = $true
$form.Controls.Add($r1)

$r2 = New-Object System.Windows.Forms.RadioButton
if ($zh) {
  $r2.Text = "仅清除虚拟环境 — 移除 .venv/，保留其余数据"
} else {
  $r2.Text = "Remove .venv/ only — keep cache and user data"
}
$r2.Location = New-Object System.Drawing.Point(32,76)
$r2.Size = New-Object System.Drawing.Size(440,24)
$form.Controls.Add($r2)

$r3 = New-Object System.Windows.Forms.RadioButton
if ($zh) {
  $r3.Text = "完全卸载 — 移除 .venv/、cache/ 和用户数据"
} else {
  $r3.Text = "Full — remove .venv/, cache, and user data"
}
$r3.Location = New-Object System.Drawing.Point(32,104)
$r3.Size = New-Object System.Drawing.Size(440,24)
$form.Controls.Add($r3)

if ($zh) {
  $okText = "确定"
  $cancelText = "取消"
} else {
  $okText = "OK"
  $cancelText = "Cancel"
}

$ok = New-Object System.Windows.Forms.Button
$ok.Text = $okText
$ok.Location = New-Object System.Drawing.Point(304,156)
$ok.Size = New-Object System.Drawing.Size(80,28)
$ok.DialogResult = [System.Windows.Forms.DialogResult]::OK
$form.AcceptButton = $ok
$form.Controls.Add($ok)

$cancel = New-Object System.Windows.Forms.Button
$cancel.Text = $cancelText
$cancel.Location = New-Object System.Drawing.Point(392,156)
$cancel.Size = New-Object System.Drawing.Size(80,28)
$cancel.DialogResult = [System.Windows.Forms.DialogResult]::Cancel
$form.CancelButton = $cancel
$form.Controls.Add($cancel)

$result = $form.ShowDialog()
if ($result -eq [System.Windows.Forms.DialogResult]::Cancel) { exit 9 }
elseif ($r3.Checked) { exit 3 }
elseif ($r2.Checked) { exit 2 }
else { exit 1 }
