; Script generated by the HM NIS Edit Script Wizard.

; HM NIS Edit Wizard helper defines
!define PRODUCT_NAME "Papywizard"
!define PRODUCT_VERSION "1.2.1-1"
!define PRODUCT_WEB_SITE "http://trac.gbiloba.org/papywizard"
!define PRODUCT_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Papywizard.exe"
!define PRODUCT_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${PRODUCT_NAME}"
!define PRODUCT_UNINST_ROOT_KEY "HKLM"

; MUI 1.67 compatible
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Language Selection Dialog Settings
!define MUI_LANGDLL_REGISTRY_ROOT "${PRODUCT_UNINST_ROOT_KEY}"
!define MUI_LANGDLL_REGISTRY_KEY  "${PRODUCT_UNINST_KEY}"
!define MUI_LANGDLL_REGISTRY_VALUENAME "NSIS:Language"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page
!insertmacro MUI_PAGE_LICENSE "..\licence_CeCILL_V2-en.txt"
; Components page
!insertmacro MUI_PAGE_COMPONENTS
; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Papywizard.exe"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"

; MUI end ------

Name "${PRODUCT_NAME} ${PRODUCT_VERSION}"
OutFile "Papywizard_${PRODUCT_VERSION}_Install.exe"
InstallDir "$PROGRAMFILES\Papywizard"
InstallDirRegKey HKLM "${PRODUCT_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

Function .onInit
  !insertmacro MUI_LANGDLL_DISPLAY
FunctionEnd

Section "SectionPrincipale" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite ifnewer
  File "dist\w9xpopen.exe"
  CreateDirectory "$SMPROGRAMS\Papywizard"
  CreateShortCut  "$SMPROGRAMS\Papywizard\Papywizard.lnk" "$INSTDIR\Papywizard.exe" "$INSTDIR\papywizard.ico"
  CreateShortCut  "$SMPROGRAMS\Papywizard\Papywizard-3D.lnk" "$INSTDIR\Papywizard-3D.exe" "$INSTDIR\papywizard.ico"
  CreateShortCut  "$SMPROGRAMS\Papywizard\Papywizard-Simul.lnk" "$INSTDIR\Papywizard-Simul.exe" "$INSTDIR\papywizard.ico"
  CreateShortCut  "$DESKTOP\Papywizard.lnk" "$INSTDIR\Papywizard.exe" "$INSTDIR\papywizard.ico"
; File "dist\python25.dll" ; already included in library.zip
  File "dist\Papywizard.exe"
  File "dist\Papywizard-3D.exe"
  File "dist\Papywizard-Simul.exe"
  File "dist\msvcr71.dll"
  File "dist\library.zip"
  File "papywizard.ico"
  ;
  ; Package
  SetOutPath "$INSTDIR\papywizard"
  SetOutPath "$INSTDIR\papywizard\common"
  File "..\papywizard\common\papywizard.conf"
  File "..\papywizard\common\presets.xml"
  SetOutPath "$INSTDIR\papywizard\view"
  File "..\papywizard\view\*.glade"
  File "..\papywizard\view\*.png"
  SetOutPath "$INSTDIR\share\locale\en\LC_MESSAGES"
  File "..\locale\en\LC_MESSAGES\papywizard.mo"
  SetOutPath "$INSTDIR\share\locale\fr\LC_MESSAGES"
  File "..\locale\fr\LC_MESSAGES\papywizard.mo"
  SetOutPath "$INSTDIR\share\locale\pl\LC_MESSAGES"
  File "..\locale\pl\LC_MESSAGES\papywizard.mo"
  SetOutPath "$INSTDIR\share\locale\de\LC_MESSAGES"
  File "..\locale\de\LC_MESSAGES\papywizard.mo"
SectionEnd

Section "GTK+ runtime" SEC02
  SetOutPath $TEMP
  File "dist\gtk+-2.10.13-setup.exe"
  ExecWait '"$TEMP\gtk+-2.10.13-setup.exe" /SP- /SILENT'
  Delete "$TEMP\gtk+-2.10.13-setup.exe"
SectionEnd

Section -AdditionalIcons
  WriteIniStr "$INSTDIR\${PRODUCT_NAME}.url" "InternetShortcut" "URL" "${PRODUCT_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\Papywizard\Website.lnk" "$INSTDIR\${PRODUCT_NAME}.url"
  CreateShortCut "$SMPROGRAMS\Papywizard\Uninstall.lnk" "$INSTDIR\Uninst.exe"
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\Uninst.exe"
  WriteRegStr HKLM "${PRODUCT_DIR_REGKEY}" "" "$INSTDIR\Papywizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "UninstallString" "$INSTDIR\Uninst.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Papywizard.exe"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "DisplayVersion" "${PRODUCT_VERSION}"
  WriteRegStr ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}" "URLInfoAbout" "${PRODUCT_WEB_SITE}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} "Papywizard"
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} "GTK+ 2.10.13 runtime"
!insertmacro MUI_FUNCTION_DESCRIPTION_END

Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "$(^Name) a ete desinstalle avec succes de votre ordinateur."
FunctionEnd

Function un.onInit
!insertmacro MUI_UNGETLANGUAGE
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Etes-vous certains de vouloir desinstaller totalement $(^Name) et tous ses composants ?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  Delete "$INSTDIR\${PRODUCT_NAME}.url"
  Delete "$INSTDIR\Uninst.exe"
  Delete "$INSTDIR\library.zip"
  Delete "$INSTDIR\msvcr71.dll"
  Delete "$INSTDIR\Papywizard.exe"
  Delete "$INSTDIR\Papywizard-3D.exe"
  Delete "$INSTDIR\Papywizard-Simul.exe"
  Delete "$INSTDIR\w9xpopen.exe"
  Delete "$INSTDIR\Papywizard.exe.log"
  Delete "$INSTDIR\papywizard.ico"
  Delete "$SMPROGRAMS\Papywizard\Uninstall.lnk"
  Delete "$SMPROGRAMS\Papywizard\Website.lnk"
  Delete "$SMPROGRAMS\Papywizard\Papywizard.lnk"
  Delete "$SMPROGRAMS\Papywizard\Papywizard-3D.lnk"
  Delete "$SMPROGRAMS\Papywizard\Papywizard-Simul.lnk"
  RMDir  "$SMPROGRAMS\Papywizard"
  Delete "$DESKTOP\Papywizard.lnk"

  ; Sources
  Delete "$INSTDIR\papywizard\common\*.*"
  Delete "$INSTDIR\papywizard\view\*.*"
  Delete "$INSTDIR\share\locale\en\LC_MESSAGES\papywizard.mo"
  Delete "$INSTDIR\share\locale\fr\LC_MESSAGES\papywizard.mo"
  Delete "$INSTDIR\share\locale\pl\LC_MESSAGES\papywizard.mo"
  Delete "$INSTDIR\share\locale\de\LC_MESSAGES\papywizard.mo"
  RMDir  "$INSTDIR\papywizard\common"
  RMDir  "$INSTDIR\papywizard\view"
  RMDir  "$INSTDIR\papywizard"
  RMDir  "$INSTDIR\share\locale\en\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\en"
  RMDir  "$INSTDIR\share\locale\fr\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\fr"
  RMDir  "$INSTDIR\share\locale\pl\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\pl"
  RMDir  "$INSTDIR\share\locale\de\LC_MESSAGES"
  RMDir  "$INSTDIR\share\locale\de"
  RMDir  "$INSTDIR\share\locale"
  RMDir  "$INSTDIR\share"
  RMDir  "$INSTDIR"

  DeleteRegKey ${PRODUCT_UNINST_ROOT_KEY} "${PRODUCT_UNINST_KEY}"
  DeleteRegKey HKLM "${PRODUCT_DIR_REGKEY}"
  SetAutoClose true
SectionEnd
