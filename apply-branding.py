#!/usr/bin/env python3
"""ใส่แบรนด์ MAE Remote ลงซอร์ส RustDesk (ทดสอบกับแท็ก 1.5.0)

ใช้: python3 apply-branding.py <rustdesk-source-dir>
ทุกจุดต้องเจอข้อความเดิม "พอดี 1 ครั้ง" ไม่งั้นหยุดทันที (upstream เปลี่ยนแล้ว ต้องตรวจเอง)
"""
import pathlib
import sys

from PIL import Image, ImageDraw

BRAND = (0x4C, 0x3B, 0xFF)
WHITE = (255, 255, 255)
APP_NAME = 'MAERemote'          # ห้ามมีช่องว่าง: ใช้เป็นชื่อ Windows service (`sc create {app_name}` ไม่ใส่ quote)
DISPLAY = 'MAE Remote Desktop'
SHORT = 'MAE Remote'  # ชื่อสั้นที่แสดงบนหน้าต่าง/แถบงาน
HOST = 'rd.maesuaisystem.com'
PUB_KEY = 'jSmZ2nHQNrvAjH8dTHgA6yS1q4fOaLLLdjDMo8cobcQ='
SITE = 'https://remote.maesuaisystem.com'
COPYRIGHT = 'Copyright © 2026 MAE Remote Desktop'

LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64">'
    '<rect width="64" height="64" rx="16" fill="#4C3BFF"/>'
    '<rect x="10" y="12" width="36" height="26" rx="5" fill="none" stroke="#fff" stroke-width="4.5"/>'
    '<path d="M21 46h14" stroke="#fff" stroke-width="4.5" stroke-linecap="round"/>'
    '<path d="M32 26v24.5l6.2-6 4.9 10.3 4.6-2.1-4.8-10.1h8.6z" fill="#fff" stroke="#4C3BFF" '
    'stroke-width="3" stroke-linejoin="round"/></svg>\n'
)

# (ไฟล์, ข้อความเดิม, ข้อความใหม่)
EDITS = [
    ('libs/hbb_common/src/config.rs',
     'RwLock::new("com.carriez".to_owned())', 'RwLock::new("com.maesuaisystem".to_owned())'),
    ('libs/hbb_common/src/config.rs',
     'pub static ref APP_NAME: RwLock<String> = RwLock::new("RustDesk".to_owned());',
     f'pub static ref APP_NAME: RwLock<String> = RwLock::new("{APP_NAME}".to_owned());'),
    ('libs/hbb_common/src/config.rs',
     'pub const RENDEZVOUS_SERVERS: &[&str] = &["rs-ny.rustdesk.com"];',
     f'pub const RENDEZVOUS_SERVERS: &[&str] = &["{HOST}"];'),
    ('libs/hbb_common/src/config.rs',
     'pub const RS_PUB_KEY: &str = "OeVuKk5nlHiXp+APNn0Y3pC1Iwpwn44JGqrQCsWqmBw=";',
     f'pub const RS_PUB_KEY: &str = "{PUB_KEY}";'),
    # คุณภาพภาพเริ่มต้น = Good image quality ("best") แทน Balanced; ผู้ใช้ยังเปลี่ยนเองได้
    ('libs/hbb_common/src/config.rs',
     'self.get_string(key, "balanced", vec!["best", "low", "custom"])',
     'self.get_string(key, "best", vec!["balanced", "low", "custom"])'),
    # ไม่มีเซิร์ฟเวอร์บัญชีของ RustDesk: ชี้ไปพอร์ต API ของเราเอง (ยังไม่มีบริการ ล็อกอินจะล้มแบบปลอดภัย)
    ('src/common.rs',
     '    "https://admin.rustdesk.com".to_owned()\n}',
     f'    "{SITE}".to_owned()\n}}'),
    ('Cargo.toml', 'description = "RustDesk Remote Desktop"', f'description = "{DISPLAY}"'),
    ('Cargo.toml', 'LegalCopyright = "Copyright © 2026 Purslane Tech Pte. Ltd. All rights reserved."',
     f'LegalCopyright = "{COPYRIGHT}"'),
    ('Cargo.toml', 'ProductName = "RustDesk"', f'ProductName = "{DISPLAY}"'),
    ('Cargo.toml', 'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{DISPLAY}"'),
    # ตัวแพ็ก portable (.exe ที่ผู้ใช้ดาวน์โหลด) มี Cargo.toml แยกของตัวเอง
    ('libs/portable/Cargo.toml', 'description = "RustDesk Remote Desktop"', f'description = "{DISPLAY}"'),
    ('libs/portable/Cargo.toml', 'LegalCopyright = "Copyright © 2026 Purslane Tech Pte. Ltd. All rights reserved."',
     f'LegalCopyright = "{COPYRIGHT}"'),
    ('libs/portable/Cargo.toml', 'ProductName = "RustDesk"', f'ProductName = "{DISPLAY}"'),
    ('libs/portable/Cargo.toml', 'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{APP_NAME}.exe"'),
    ('libs/portable/Cargo.toml', 'FileDescription = "RustDesk Remote Desktop"', f'FileDescription = "{DISPLAY}"'),
    ('flutter/windows/runner/Runner.rc', 'VALUE "CompanyName", "Purslane Tech Pte. Ltd." "\\0"',
     f'VALUE "CompanyName", "{DISPLAY}" "\\0"'),
    ('flutter/windows/runner/Runner.rc', 'VALUE "FileDescription", "RustDesk Remote Desktop" "\\0"',
     f'VALUE "FileDescription", "{DISPLAY}" "\\0"'),
    ('flutter/windows/runner/Runner.rc',
     'VALUE "LegalCopyright", "Copyright © 2026 Purslane Tech Pte. Ltd. All rights reserved." "\\0"',
     f'VALUE "LegalCopyright", "{COPYRIGHT}" "\\0"'),
    ('flutter/windows/runner/Runner.rc', 'VALUE "ProductName", "RustDesk" "\\0"',
     f'VALUE "ProductName", "{DISPLAY}" "\\0"'),
    ('flutter/lib/common.dart', 'static const Color accent = Color(0xFF0071FF);',
     'static const Color accent = Color(0xFF4C3BFF);'),
    ('flutter/lib/common.dart', 'static const Color accent50 = Color(0x770071FF);',
     'static const Color accent50 = Color(0x774C3BFF);'),
    ('flutter/lib/common.dart', 'static const Color accent80 = Color(0xAA0071FF);',
     'static const Color accent80 = Color(0xAA4C3BFF);'),
    ('flutter/lib/common.dart', 'static const Color idColor = Color(0xFF00B6F0);',
     'static const Color idColor = Color(0xFF4C3BFF);'),
    ('flutter/lib/common.dart', 'static const Color button = Color(0xFF2C8CFF);',
     'static const Color button = Color(0xFF4C3BFF);'),
    ('flutter/lib/desktop/pages/desktop_home_page.dart', 'https://rustdesk.com/download', f'{SITE}/#download'),
    ('flutter/lib/desktop/widgets/tabbar_widget.dart', '"RustDesk",\n                              style: TextStyle(fontSize: 13),',
     '"MAE Remote Desktop",\n                              style: TextStyle(fontSize: 13),'),
    # ระบบแจ้งอัปเดตของ MAE: โปรแกรมอ่าน https://remote.maesuaisystem.com/version.json ตอนเปิด
    # ถ้า build ในไฟล์ > MAE_BUILD จะขึ้นการ์ด "มี MAE Remote เวอร์ชันใหม่" + ปุ่มดาวน์โหลด (เปิดหน้าเว็บ)
    # เพิ่ม MAE_BUILD ทุกครั้งที่ปล่อยรุ่นใหม่ แล้วแก้ site/version.json ให้ตรง
    ('src/common.rs',
     '''pub fn check_software_update() {
    if is_custom_client() {
        return;
    }''',
     '''pub fn check_software_update() {
    if is_custom_client() {
        mae_check_update();
        return;
    }'''),
    ('src/common.rs',
     '''// No need to check `danger_accept_invalid_cert` for now.
// Because the url is always `https://api.rustdesk.com/version/latest`.''',
     '''// MAE Remote update notice. Bump MAE_BUILD for every release and keep
// https://remote.maesuaisystem.com/version.json ({"build": N, "version": "1.5.0-N"}) in step.
pub const MAE_BUILD: u64 = 7;
const MAE_VERSION_URL: &str = "https://remote.maesuaisystem.com/version.json";

fn mae_check_update() {
    std::thread::spawn(move || allow_err!(mae_do_check_update()));
}

#[tokio::main(flavor = "current_thread")]
async fn mae_do_check_update() -> hbb_common::ResultType<()> {
    let client = crate::hbbs_http::create_http_client_async_with_url_strict(MAE_VERSION_URL).await?;
    let bytes = client.get(MAE_VERSION_URL).send().await?.bytes().await?;
    let latest: Value = serde_json::from_slice(&bytes)?;
    let build = latest["build"].as_u64().unwrap_or(0);
    let version = latest["version"].as_str().unwrap_or_default();
    if build > MAE_BUILD && !version.is_empty() {
        #[cfg(feature = "flutter")]
        {
            let url = format!("https://remote.maesuaisystem.com/?update={version}");
            let mut m = HashMap::new();
            m.insert("name", "check_software_update_finish");
            m.insert("url", url.as_str());
            if let Ok(data) = serde_json::to_string(&m) {
                let _ = crate::flutter::push_global_event(crate::flutter::APP_TYPE_MAIN, data);
            }
        }
    }
    Ok(())
}

// No need to check `danger_accept_invalid_cert` for now.
// Because the url is always `https://api.rustdesk.com/version/latest`.'''),
    # ตัวอัปเดตอัตโนมัติของต้นทางจะไปโหลดตัวติดตั้งจาก GitHub ของต้นทาง: ปิดถาวรสำหรับ MAE
    ('src/updater.rs',
     '''fn check_update(manually: bool) -> ResultType<()> {
''',
     '''fn check_update(manually: bool) -> ResultType<()> {
    if crate::is_custom_client() {
        return Ok(());
    }
'''),
    ('flutter/lib/common.dart',
     '''    if (!bind.isCustomClient()) {
      platformFFI.registerEventHandler(
          kCheckSoftwareUpdateFinish, kCheckSoftwareUpdateFinish,''',
     '''    if (true) {
      platformFFI.registerEventHandler(
          kCheckSoftwareUpdateFinish, kCheckSoftwareUpdateFinish,'''),
    ('flutter/lib/desktop/pages/desktop_home_page.dart',
     '''  Widget buildHelpCards(String updateUrl) {
    if (!bind.isCustomClient() &&''',
     '''  Widget buildHelpCards(String updateUrl) {
    if (bind.isCustomClient() && updateUrl.isNotEmpty && !isCardClosed) {
      final ver = Uri.tryParse(updateUrl)?.queryParameters['update'] ?? '';
      return buildInstallCard(
          "Status",
          "${translate("new-version-of-{MAE Remote}-tip")} ($ver).",
          "Download", () async {
        await launchUrl(Uri.parse(updateUrl));
      }, closeButton: true);
    }
    if (!bind.isCustomClient() &&'''),
    # ข้อมูลไฟล์ (Properties → Details) ของ exe หลักและ DLL ไม่ให้ขึ้นชื่อเดิม
    ('flutter/windows/runner/Runner.rc', 'VALUE "InternalName", "rustdesk" "\\0"', f'VALUE "InternalName", "{APP_NAME}" "\\0"'),
    ('flutter/windows/runner/Runner.rc', 'VALUE "OriginalFilename", "rustdesk.exe" "\\0"', f'VALUE "OriginalFilename", "{APP_NAME}.exe" "\\0"'),
    ('Cargo.toml', 'OriginalFilename = "rustdesk.exe"', f'OriginalFilename = "{APP_NAME}.exe"'),
    # ชื่อที่ผู้ใช้เห็น (แถบงาน, ชื่อหน้าต่าง, ข้อความในโปรแกรม, tooltip ถาด) = "MAE Remote" มีเว้นวรรค
    # APP_NAME ยังเป็น MAERemote (ใช้เป็นชื่อ service/โฟลเดอร์) ; การค้นหาหน้าต่างใช้ชื่อเดียวกับชื่อหน้าต่างเสมอ
    ('src/flutter.rs',
     '    let name = crate::platform::wide_string(&crate::get_app_name());\n    if length > name.len() as i32 {',
     f'    let name = crate::platform::wide_string("{SHORT}");\n    if length > name.len() as i32 {{'),
    ('src/core_main.rs',
     '            &crate::platform::FLUTTER_RUNNER_WIN32_WINDOW_CLASS,\n            &crate::get_app_name(),',
     f'            &crate::platform::FLUTTER_RUNNER_WIN32_WINDOW_CLASS,\n            "{SHORT}",'),
    ('flutter/lib/common.dart',
     'String getWindowName({WindowType? overrideType}) {\n  final name = bind.mainGetAppNameSync();',
     f"String getWindowName({{WindowType? overrideType}}) {{\n  const name = '{SHORT}';"),
    ('flutter/lib/main.dart',
     "              : bind.mainGetAppNameSync(),\n          theme: MyTheme.lightTheme,",
     f"              : '{SHORT}',\n          theme: MyTheme.lightTheme,"),
    ('src/lang.rs',
     '                let app_name = crate::get_app_name();\n                if !app_name.contains("RustDesk") {',
     f'                let app_name = "{SHORT}".to_owned();\n                if !app_name.contains("RustDesk") {{'),
    ('src/tray.rs',
     '                "{} {}",\n                crate::get_app_name(),\n                translate("Service is running".to_owned()),',
     f'                "{{}} {{}}",\n                "{SHORT}",\n                translate("Service is running".to_owned()),'),
    ('src/tray.rs',
     '                "{} - {}\\n{}",\n                crate::get_app_name(),\n                translate("Ready".to_owned()),',
     f'                "{{}} - {{}}\\n{{}}",\n                "{SHORT}",\n                translate("Ready".to_owned()),'),
    # หน้าต่างหลักแสดงชื่อโปรแกรมข้างโลโก้บนแถบหัว (ค่าเดิม showTitle = false แสดงแค่ไอคอน)
    ('flutter/lib/desktop/pages/desktop_tab_page.dart',
     '            body: DesktopTab(\n              controller: tabController,\n',
     '            body: DesktopTab(\n              controller: tabController,\n              showTitle: true,\n'),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart', "launchUrlString('https://rustdesk.com');", f"launchUrlString('{SITE}');"),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart', 'decoration: const BoxDecoration(color: Color(0xFF2c8cff)),',
     'decoration: const BoxDecoration(color: Color(0xFF4C3BFF)),'),
    # AGPL: ต้องคงข้อความลิขสิทธิ์ของต้นฉบับไว้ในหน้า About (ไม่ใช้ชื่อแบรนด์ RustDesk)
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "'Copyright © ${DateTime.now().toString().substring(0, 4)} Purslane Tech Pte. Ltd.\\n$license',",
     "'Copyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop\\nPortions © Purslane Tech Pte. Ltd. · GNU AGPL-3.0 · github.com/maxspeedcom/mae-remote-desktop\\n$license',"),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart', "translate('Slogan_tip'),", "'remote.maesuaisystem.com',"),
    # "Powered by RustDesk" label under the logo (links to rustdesk.com): always hidden
    ('flutter/lib/common.dart', 'if (bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {',
     'if (true || bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {'),
    ('flutter/lib/mobile/pages/connection_page.dart', 'https://rustdesk.com/download', f'{SITE}/#download'),
]

# ลิงก์ที่มีหลายจุดในไฟล์เดียว: แทนทุกจุด (ต้องเจออย่างน้อย 1)
EDITS_ALL = [
    ('flutter/lib/desktop/pages/desktop_setting_page.dart', 'https://rustdesk.com/privacy.html', f'{SITE}/privacy.html'),
    ('flutter/lib/desktop/pages/install_page.dart', 'https://rustdesk.com/privacy.html', f'{SITE}/privacy.html'),
    ('flutter/lib/mobile/pages/settings_page.dart', 'https://rustdesk.com/privacy.html', f'{SITE}/privacy.html'),
]


def edit(root, rel, old, new, all_=False):
    p = root / rel
    text = p.read_text(encoding='utf-8')
    n = text.count(old)
    if (n != 1 and not all_) or n == 0:
        sys.exit(f'STOP: {rel}: expected {"1" if not all_ else ">=1"} match, found {n}: {old[:70]!r}')
    p.write_text(text.replace(old, new), encoding='utf-8')
    print(f'  ok {rel} ({n}x)')


def render_icon(size):
    s = 16  # วาดที่ 1024px แล้วย่อ ให้ขอบเนียน
    img = Image.new('RGBA', (64 * s, 64 * s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, 64 * s - 1, 64 * s - 1), radius=16 * s, fill=BRAND)
    h = 2.25  # ครึ่งหนึ่งของ stroke 4.5 (stroke ของ SVG อยู่กึ่งกลางเส้น)
    d.rounded_rectangle(((10 - h) * s, (12 - h) * s, (46 + h) * s, (38 + h) * s),
                        radius=(5 + h) * s, outline=WHITE, width=int(4.5 * s))
    d.rounded_rectangle(((21 - h) * s, (46 - h) * s, (35 + h) * s, (46 + h) * s), radius=h * s, fill=WHITE)
    pts = [(32, 26), (32, 50.5), (38.2, 44.5), (43.1, 54.8), (47.7, 52.7), (42.9, 42.6), (51.5, 42.6)]
    pts = [(x * s, y * s) for x, y in pts]
    d.polygon(pts, fill=WHITE)
    d.line(pts + [pts[0], pts[1]], fill=BRAND, width=3 * s, joint='curve')
    return img.resize((size, size), Image.LANCZOS)


def write_ico(path, big):
    """ICO มาตรฐาน Windows: 16-128 เป็น BMP 32 บิต + AND mask, 256 เป็น PNG, planes=1
    (Pillow เขียนทุกขนาดเป็น PNG และ planes=0 ทำให้ Explorer ไม่แสดงไอคอนของ .exe)"""
    import io
    import struct
    images = []
    for s in (16, 20, 24, 32, 40, 48, 64, 128, 256):
        im = big.resize((s, s), Image.LANCZOS).convert('RGBA')
        if s == 256:
            buf = io.BytesIO()
            im.save(buf, 'PNG')
            images.append((s, buf.getvalue()))
            continue
        px = im.load()
        xor = bytearray()
        mask_row = ((s + 31) // 32) * 4
        and_mask = bytearray()
        for y in range(s - 1, -1, -1):
            row_bits = bytearray(mask_row)
            for x in range(s):
                r, g, b, a = px[x, y]
                xor += bytes((b, g, r, a))
                if a == 0:
                    row_bits[x // 8] |= 0x80 >> (x % 8)
            and_mask += row_bits
        header = struct.pack('<IiiHHIIiiII', 40, s, s * 2, 1, 32, 0, len(xor) + len(and_mask), 0, 0, 0, 0)
        images.append((s, header + bytes(xor) + bytes(and_mask)))
    out = struct.pack('<HHH', 0, 1, len(images))
    offset = 6 + 16 * len(images)
    for s, blob in images:
        dim = 0 if s == 256 else s
        out += struct.pack('<BBBBHHII', dim, dim, 0, 0, 1, 32, len(blob), offset)
        offset += len(blob)
    path.write_bytes(out + b''.join(blob for _, blob in images))


def write_icons(root):
    big = render_icon(1024)
    for rel, size in [('res/icon.png', 512), ('res/32x32.png', 32), ('res/64x64.png', 64),
                      ('res/128x128.png', 128), ('res/128x128@2x.png', 256), ('res/mac-icon.png', 1024),
                      ('flutter/assets/icon.png', 256), ('flutter/assets/logo.png', 256),
                      ('flutter/assets/logo_light.png', 256), ('flutter/assets/logo_dark.png', 256)]:
        big.resize((size, size), Image.LANCZOS).save(root / rel)
        print(f'  png {rel} {size}px')
    for rel in ['res/icon.ico', 'res/tray-icon.ico', 'flutter/windows/runner/resources/app_icon.ico']:
        write_ico(root / rel, big)
        print(f'  ico {rel}')
    for rel in ['res/logo.svg', 'res/scalable.svg', 'flutter/assets/icon.svg']:
        (root / rel).write_text(LOGO_SVG, encoding='utf-8')
        print(f'  svg {rel}')


def main():
    root = pathlib.Path(sys.argv[1]).resolve()
    print('text edits:')
    for rel, old, new in EDITS:
        edit(root, rel, old, new)
    for rel, old, new in EDITS_ALL:
        edit(root, rel, old, new, all_=True)
    print('icons:')
    write_icons(root)
    print('done')


if __name__ == '__main__':
    main()
