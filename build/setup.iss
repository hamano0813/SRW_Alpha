#define MyAppName "Super Robot Wars Alpha ROM Editor"
#define MyAppVersion "0.3.0"
#define MyAppPublisher "Hamano"
#define MyAppExeName "SRW_Alpha.exe"
#define MyAppShortName "SRW_Alpha"
#define MyAppShortCutName "SRW Alpha ROM Editor"
#define UVLocal "{userdocs}\..\.local\bin"

[Setup]
AppId={{B8E4A293-8D3E-4A1F-9C2E-7F5B1D3E6A4C}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppShortName}
DefaultGroupName={#MyAppShortName}
DisableProgramGroupPage=yes
SetupIconFile=C:\Softwares\Inno Setup\SetupClassicIcon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern dynamic windows11
Output=yes
OutputDir=.\
OutputBaseFilename={#MyAppShortName}-{#MyAppVersion}-x64
ExtraDiskSpaceRequired=1181116000
ChangesEnvironment=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Dirs]
Name: "{app}\.venv"; Flags: uninsalwaysuninstall

[UninstallDelete]
Type: filesandordirs; Name: "{app}\.venv"

[Files]
Source: "uv.exe"; DestDir: "{#UVLocal}"; Flags: ignoreversion onlyifdoesntexist
Source: "uvx.exe"; DestDir: "{#UVLocal}"; Flags: ignoreversion onlyifdoesntexist
Source: "uvw.exe"; DestDir: "{#UVLocal}"; Flags: ignoreversion onlyifdoesntexist
Source: "uv.toml"; DestDir: "{userappdata}\uv"; Flags: ignoreversion
Source: "uv.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "{#MyAppExeName}"; DestDir: "{app}"; Flags: ignoreversion
Source: "uninstall_helper.ps1"; DestDir: "{app}"; Flags: ignoreversion
Source: ".python-version"; DestDir: "{app}"; Flags: ignoreversion
Source: "pyproject.toml"; DestDir: "{app}"; Flags: ignoreversion
Source: "uv.lock"; DestDir: "{app}"; Flags: ignoreversion
Source: "upx.exe"; DestDir: "{app}"; Flags: ignoreversion deleteafterinstall
Source: "upx.1"; DestDir: "{app}"; Flags: ignoreversion deleteafterinstall
Source: "script\*"; DestDir: "{app}\script"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "tools\*"; DestDir: "{app}\tools"; Flags: ignoreversion recursesubdirs createallsubdirs

[Registry]
Root: HKCU; Subkey: "Environment"; ValueType: string; ValueName: "PATH"; ValueData: "{#UVLocal};%PATH%"; Flags: preservestringtype

[Icons]
Name: "{commondesktop}\{#MyAppShortCutName}"; Filename: "{app}\{#MyAppExeName}"; Comment: "{#MyAppName}"

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppShortCutName, '&', '&&')}}"; Flags: postinstall skipifsilent unchecked

[Code]
var
  MirrorPage: TInputQueryWizardPage;
  DeployPage: TWizardPage;
  DeployLog: TNewMemo;
  UninstallChoice: Integer;

procedure AppendLog(const S: string);
begin
  DeployLog.Lines.Add(S);
  DeployLog.SelStart := Length(DeployLog.Lines.Text);
end;

function GetPythonVer(const AppDir: string): string;
var
  VerFile: string;
  Lines: TArrayOfString;
begin
  Result := '3.14';
  VerFile := AppDir + '\.python-version';
  if LoadStringsFromFile(VerFile, Lines) and (GetArrayLength(Lines) > 0) then
    Result := Trim(Lines[0]);
end;

procedure DoDeploy;
var
  AppDir: string;
  PyVer: string;
  TmpBat: string;
  TmpLog: string;
  ResultCode: Integer;
  Lines: TArrayOfString;
  I: Integer;
begin
  AppDir := ExpandConstant('{app}');
  PyVer := GetPythonVer(AppDir);
  TmpBat := ExpandConstant('{tmp}\_deploy.bat');
  TmpLog := ExpandConstant('{tmp}\_deploy.log');

  AppendLog('Target: ' + AppDir);
  AppendLog('Python: ' + PyVer);
  AppendLog('');

  SaveStringToFile(TmpBat,
    '@echo off' + Chr(13) + Chr(10) +
    'cd /d "' + AppDir + '"' + Chr(13) + Chr(10) +
    'echo --- Installing Python ---' + Chr(13) + Chr(10) +
    '"' + AppDir + '\uv.exe" python install ' + PyVer + Chr(13) + Chr(10) +
    'echo.' + Chr(13) + Chr(10) +
    'echo --- Installing dependencies ---' + Chr(13) + Chr(10) +
    '"' + AppDir + '\uv.exe" sync' + Chr(13) + Chr(10) +
    'echo.' + Chr(13) + Chr(10) +
    'if exist "' + AppDir + '\upx.exe" (' + Chr(13) + Chr(10) +
    '  echo --- Compressing ---' + Chr(13) + Chr(10) +
    '  for /r "' + AppDir + '\.venv" %%f in (*.pyd) do "' + AppDir + '\upx.exe" -1qq "%%f" 2>nul' + Chr(13) + Chr(10) +
    '  "' + AppDir + '\upx.exe" -9qq "' + AppDir + '\.venv\Scripts\python.exe" 2>nul' + Chr(13) + Chr(10) +
    '  "' + AppDir + '\upx.exe" -9qq "' + AppDir + '\.venv\Scripts\pythonw.exe" 2>nul' + Chr(13) + Chr(10) +
    '  echo [DONE] Compression complete.' + Chr(13) + Chr(10) +
    ')' + Chr(13) + Chr(10) +
    'echo [DONE] Deployment complete.' + Chr(13) + Chr(10),
    False);

  Exec('cmd.exe', '/c ""' + TmpBat + '" > "' + TmpLog + '" 2>&1"',
    AppDir, SW_HIDE, ewWaitUntilTerminated, ResultCode);

  if LoadStringsFromFile(TmpLog, Lines) then
    for I := 0 to GetArrayLength(Lines) - 1 do
      AppendLog(Lines[I]);

  DeleteFile(TmpBat);
  DeleteFile(TmpLog);

  AppendLog('');
  if ResultCode = 0 then
    AppendLog('[INFO] Deployment complete.')
  else
    AppendLog('[ERROR] Failed (exit ' + IntToStr(ResultCode) + ').');
end;

procedure DeployPageActivate(Sender: TWizardPage);
begin
  WizardForm.NextButton.Enabled := False;
  try
    DoDeploy;
  finally
    WizardForm.NextButton.Enabled := True;
  end;
end;

procedure InitializeWizard();
var
  IsZh: Boolean;
begin
  IsZh := (ActiveLanguage() = 'chinesesimplified');

  if IsZh then
    MirrorPage := CreateInputQueryPage(wpSelectDir,
      '下载镜像', '配置 Python 包下载源',
      '程序需要在线安装 Python 环境和依赖库，请确认网络畅通。' + Chr(13) + Chr(10) +
      '如需使用自定义镜像，请修改下方地址：')
  else
    MirrorPage := CreateInputQueryPage(wpSelectDir,
      'Download Mirror', 'Configure Python Package Mirror',
      'This setup requires network to install Python and dependencies.' + Chr(13) + Chr(10) +
      'Customize mirror addresses if needed:');
  if IsZh then
  begin
    MirrorPage.Add('PyPI 镜像', False);
    MirrorPage.Add('Python 镜像', False);
  end
  else
  begin
    MirrorPage.Add('PyPI Mirror', False);
    MirrorPage.Add('Python Mirror', False);
  end;
  MirrorPage.Values[0] := 'https://mirrors.aliyun.com/pypi/simple/';
  MirrorPage.Values[1] := 'https://mirror.nju.edu.cn/github-release/astral-sh/python-build-standalone/';

  if IsZh then
    DeployPage := CreateCustomPage(wpInstalling, '正在部署环境',
      '正在安装 Python 和项目依赖...')
  else
    DeployPage := CreateCustomPage(wpInstalling, 'Deploying Environment',
      'Setting up Python and dependencies...');
  DeployLog := TNewMemo.Create(DeployPage);
  DeployLog.Parent := DeployPage.Surface;
  DeployLog.Align := alClient;
  DeployLog.ScrollBars := ssVertical;
  DeployLog.ReadOnly := True;
  DeployLog.Font.Name := 'Consolas';
  DeployLog.Font.Size := 9;
  DeployPage.OnActivate := @DeployPageActivate;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  ConfigLines: string;
begin
  if CurStep = ssPostInstall then
  begin
    ConfigLines :=
      'python-install-mirror = "' + MirrorPage.Values[1] + '"' + Chr(13) + Chr(10) +
      Chr(13) + Chr(10) +
      '[[index]]' + Chr(13) + Chr(10) +
      'url = "' + MirrorPage.Values[0] + '"' + Chr(13) + Chr(10) +
      'default = true' + Chr(13) + Chr(10);
    SaveStringToFile(ExpandConstant('{userappdata}\uv\uv.toml'), ConfigLines, False);
  end;
end;

// ======================== Uninstall ========================

function InitializeUninstall(): Boolean;
var
  ResultCode: Integer;
  Ps1Path: string;
begin
  Ps1Path := ExpandConstant('{app}\uninstall_helper.ps1');
  if not FileExists(Ps1Path) then
  begin
    UninstallChoice := 1;
    Result := True;
    Exit;
  end;

  Exec('powershell.exe', '-NoProfile -ExecutionPolicy Bypass -File "' + Ps1Path + '"',
    '', SW_SHOW, ewWaitUntilTerminated, ResultCode);

  if ResultCode = 9 then
  begin
    Result := False;
    Exit;
  end;

  UninstallChoice := ResultCode;
  Result := True;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
var
  AppDir: string;
begin
  if CurUninstallStep = usPostUninstall then
  begin
    AppDir := ExpandConstant('{app}');

    case UninstallChoice of
      2:
        if DirExists(AppDir + '\.venv') then
          DelTree(AppDir + '\.venv', True, True, True);
      3:
      begin
        if DirExists(AppDir + '\.venv') then
          DelTree(AppDir + '\.venv', True, True, True);
        if DirExists(AppDir + '\cache') then
          DelTree(AppDir + '\cache', True, True, True);
        DeleteFile(AppDir + '\config.json');
        DeleteFile(AppDir + '\cache.xml');
      end;
    end;
  end;
end;
