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
pub const MAE_BUILD: u64 = 10;
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
     "'Copyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop\\nPortions © Purslane Tech Pte. Ltd. · GNU AGPL-3.0 · source: remote.maesuaisystem.com/source\\n$license',"),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart', "translate('Slogan_tip'),", "'remote.maesuaisystem.com',"),
    # "Powered by RustDesk" label under the logo (links to rustdesk.com): always hidden
    ('flutter/lib/common.dart', 'if (bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {',
     'if (true || bind.mainGetBuildinOption(key: "hide-powered-by-me") == \'Y\') {'),
    ('flutter/lib/mobile/pages/connection_page.dart', 'https://rustdesk.com/download', f'{SITE}/#download'),
]

# รายงานทราฟฟิกของแต่ละ session (r8): เครื่องที่ถูกรีโมทนับ byte ที่ส่ง/รับของการเชื่อมต่อนั้น แล้วส่งยอดสะสม
# ไป {api}/api/audit/conn (action "traffic") ทุก 5 วินาที + ยอดสุดท้ายใน record "close"
# -> API เก็บต่อ session + ยอดรวม -> MAE Monitor วาดกราฟเรียลไทม์/ย้อนหลังได้ แม้ session ต่อตรง (direct)
TRAFFIC_EDITS = [
    ('src/server/connection.rs',
     """pub struct Connection {
    inner: ConnInner,
    display_idx: usize,
    stream: super::Stream,
    server: super::ServerPtrWeak,
""",
     """/// MAE: the peer stream with byte counters for the traffic report (see `post_traffic`). The methods
/// below shadow the `Stream` methods of the same name; everything else reaches the stream via Deref.
struct CountedStream {
    inner: super::Stream,
    tx: u64,
    rx: u64,
}

impl std::ops::Deref for CountedStream {
    type Target = super::Stream;
    fn deref(&self) -> &super::Stream {
        &self.inner
    }
}

impl std::ops::DerefMut for CountedStream {
    fn deref_mut(&mut self) -> &mut super::Stream {
        &mut self.inner
    }
}

impl CountedStream {
    #[inline]
    async fn send(&mut self, msg: &impl hbb_common::protobuf::Message) -> ResultType<()> {
        self.tx += hbb_common::protobuf::Message::compute_size(msg) as u64;
        self.inner.send(msg).await
    }

    #[inline]
    async fn send_raw(&mut self, bytes: Vec<u8>) -> ResultType<()> {
        self.tx += bytes.len() as u64;
        self.inner.send_raw(bytes).await
    }

    #[inline]
    async fn send_bytes(&mut self, bytes: hbb_common::bytes::Bytes) -> ResultType<()> {
        self.tx += bytes.len() as u64;
        self.inner.send_bytes(bytes).await
    }

    #[inline]
    async fn next(&mut self) -> Option<Result<hbb_common::bytes::BytesMut, std::io::Error>> {
        let res = self.inner.next().await;
        if let Some(Ok(bytes)) = &res {
            self.rx += bytes.len() as u64;
        }
        res
    }
}

pub struct Connection {
    inner: ConnInner,
    display_idx: usize,
    stream: CountedStream,
    server: super::ServerPtrWeak,
    // MAE: totals in the last traffic report, when it was sent, and whether it is still on its way
    traffic_reported: (u64, u64),
    traffic_last: Instant,
    traffic_busy: Arc<AtomicBool>,
"""),
    ('src/server/connection.rs',
     """            display_idx: 0,
            stream,
            server,
""",
     """            display_idx: 0,
            stream: CountedStream { inner: stream, tx: 0, rx: 0 },
            server,
            traffic_reported: (0, 0),
            traffic_last: Instant::now(),
            traffic_busy: Arc::new(AtomicBool::new(false)),
"""),
    ('src/server/connection.rs',
     "match fs::handle_read_jobs(&mut conn.read_jobs, &mut conn.stream).await {",
     "match fs::handle_read_jobs_counted(&mut conn.read_jobs, &mut conn.stream.inner, &mut conn.stream.tx).await {"),
    ('src/server/connection.rs',
     """                    conn.file_remove_log_control.on_timer().drain(..).map(|x| conn.send_to_cm(x)).count();
""",
     """                    conn.file_remove_log_control.on_timer().drain(..).map(|x| conn.send_to_cm(x)).count();
                    conn.post_traffic();
"""),
    ('src/server/connection.rs',
     """        conn.post_conn_audit(json!({
            "action": "close",
        }));""",
     """        conn.post_conn_audit(json!({
            "action": "close",
            "tx": conn.stream.tx,
            "rx": conn.stream.rx,
        }));"""),
    ('src/server/connection.rs',
     """            self.stream.set_raw();
            let mut hbbs_rx = crate::hbbs_http::sync::signal_receiver();
""",
     """            self.stream.set_raw();
            let mut hbbs_rx = crate::hbbs_http::sync::signal_receiver();
            let mut traffic_timer = crate::rustdesk_interval(time::interval(Duration::from_secs(1)));
"""),
    ('src/server/connection.rs',
     """                    _ = self.timer.tick() => {
                        if last_recv_time.elapsed() >= H1 {""",
     """                    _ = traffic_timer.tick() => self.post_traffic(),
                    _ = self.timer.tick() => {
                        if last_recv_time.elapsed() >= H1 {"""),
    ('src/server/connection.rs',
     """    fn get_files_for_audit(job_type: fs::JobType, mut files: Vec<FileEntry>) -> Vec<(String, i64)> {""",
     """    /// MAE: this connection's running byte totals, at most every 5 s and only when they changed, so the
    /// monitor shows live traffic for direct sessions too. One attempt and no queue: the next report
    /// carries the totals anyway, and the "close" record (posted with retries) carries the final ones.
    fn post_traffic(&mut self) {
        let now = (self.stream.tx, self.stream.rx);
        if !self.authorized
            || self.server_audit_conn.is_empty()
            || now == self.traffic_reported
            || self.traffic_last.elapsed() < Duration::from_secs(5)
            || self.traffic_busy.swap(true, Ordering::AcqRel)
        {
            return;
        }
        self.traffic_reported = now;
        self.traffic_last = Instant::now();
        let url = self.server_audit_conn.clone();
        let body = json!({
            "action": "traffic",
            "id": Config::get_id(),
            "uuid": crate::encode64(hbb_common::get_uuid()),
            "conn_id": self.inner.id,
            "session_id": self.lr.session_id,
            "tx": now.0,
            "rx": now.1,
        })
        .to_string();
        let busy = self.traffic_busy.clone();
        tokio::spawn(async move {
            allow_err!(crate::post_request(url, body, "").await);
            busy.store(false, Ordering::Release);
        });
    }

    fn get_files_for_audit(job_type: fs::JobType, mut files: Vec<FileEntry>) -> Vec<(String, i64)> {"""),
    ('libs/base/src/fs.rs',
     """pub async fn handle_read_jobs(
    jobs: &mut Vec<TransferJob>,
    stream: &mut hbb_common::Stream,
) -> ResultType<String> {
    init_jobs(jobs, stream).await?;
""",
     """pub async fn handle_read_jobs(
    jobs: &mut Vec<TransferJob>,
    stream: &mut hbb_common::Stream,
) -> ResultType<String> {
    let mut sent = 0;
    handle_read_jobs_counted(jobs, stream, &mut sent).await
}

/// MAE: `handle_read_jobs` that also adds the file bytes it sends to `sent` (the traffic report).
pub async fn handle_read_jobs_counted(
    jobs: &mut Vec<TransferJob>,
    stream: &mut hbb_common::Stream,
    sent: &mut u64,
) -> ResultType<String> {
    init_jobs(jobs, stream).await?;
"""),
    ('libs/base/src/fs.rs',
     """            Ok(Some(block)) => {
                stream.send(&new_block(block)).await?;
""",
     """            Ok(Some(block)) => {
                *sent += block.data.len() as u64;
                stream.send(&new_block(block)).await?;
"""),
]

# หน้าจอรีโมทพอดีหน้าต่าง (r8, เห็นหน้าจอเต็มโดยไม่ต้องเลื่อนสกอลบาร์): ค่าเริ่มต้น view style
# = adaptive แทน original (1:1 + scroll bar) และย้ายเครื่องที่บันทึกไว้ด้วยค่าเริ่มต้นเดิมครั้งเดียวตอนเปิดโปรแกรม
FIT_EDITS = [
    ('libs/hbb_common/src/config.rs',
     'keys::OPTION_VIEW_STYLE => self.get_string(key, "original", vec!["adaptive"]),',
     'keys::OPTION_VIEW_STYLE => self.get_string(key, "adaptive", vec!["original"]),'),
    ('src/common.rs',
     """fn mae_check_update() {
    std::thread::spawn(move || allow_err!(mae_do_check_update()));
}
""",
     """fn mae_check_update() {
    std::thread::spawn(move || allow_err!(mae_do_check_update()));
    std::thread::spawn(mae_fit_saved_peers);
}

/// MAE build 8: the remote screen fits the window by default ("adaptive", no scroll bars). Computers saved by
/// older builds kept "original" (1:1 with scroll bars) only because it was the old default, so move them once.
/// A choice made after this (toolbar -> Display) is kept.
fn mae_fit_saved_peers() {
    const DONE: &str = "mae-view-fit-migrated";
    if LocalConfig::get_option(DONE) == "Y" {
        return;
    }
    for (id, _, mut cfg) in config::PeerConfig::peers(None) {
        if cfg.view_style == "original" {
            cfg.view_style = "adaptive".to_owned();
            cfg.store(&id);
        }
    }
    LocalConfig::set_option(DONE.to_owned(), "Y".to_owned());
}
"""),
]

# r9: ติดตั้งแล้วเปลี่ยนชื่อตัวโปรแกรมเป็น <APP_NAME>.exe แบบเดียวกับ update_me (กันพลาดถ้าชุดติดตั้งยังชื่อ rustdesk.exe)
INSTALL_EDITS = [
    ('src/platform/windows.rs',
     'md \\"{path}\\"\n{copy_exe}\nreg add {subkey} /f\nreg add {subkey} /f /v DisplayIcon',
     'md \\"{path}\\"\n{copy_exe}\n{rename_exe}\nreg add {subkey} /f\nreg add {subkey} /f /v DisplayIcon'),
    ('src/platform/windows.rs',
     '        copy_exe = copy_exe_cmd(&src_exe, &exe, &path)?,\n        import_config = get_import_config(&exe),',
     '        copy_exe = copy_exe_cmd(&src_exe, &exe, &path)?,\n        rename_exe = rename_exe_cmd(&src_exe, &path)?,\n        import_config = get_import_config(&exe),'),
]

# r9: ชื่อไฟล์ในโฟลเดอร์ติดตั้ง/Task Manager และข้อความที่ผู้ใช้เห็นเป็นชื่อ MAE Remote — core DLL = maeremote_core.dll,
# broker = RuntimeBroker_maeremote.exe, ไม่มีไดรเวอร์เครื่องพิมพ์ (ชื่อ "RustDesk v4 Printer Driver" อยู่ในไดรเวอร์ที่เซ็นแล้ว แก้ไม่ได้)
# จึงซ่อนตัวเลือกติดตั้งเครื่องพิมพ์, แท็บ Printer และ "Enable remote printer"; gen-workflow.py ไม่ใส่ไดรเวอร์ในชุดติดตั้ง
NAME_EDITS = [
    ('flutter/windows/CMakeLists.txt',
     'COMPONENT Runtime RENAME librustdesk.dll)',
     'COMPONENT Runtime RENAME maeremote_core.dll)'),
    ('flutter/windows/runner/main.cpp',
     'HINSTANCE hInstance = LoadLibraryA("librustdesk.dll");',
     'HINSTANCE hInstance = LoadLibraryA("maeremote_core.dll");'),
    ('flutter/windows/runner/main.cpp',
     'std::cout << "Failed to load librustdesk.dll." << std::endl;',
     'std::cout << "Failed to load maeremote_core.dll." << std::endl;'),
    ('flutter/lib/models/native_model.dart',
     "? DynamicLibrary.open('librustdesk.dll')",
     "? DynamicLibrary.open('maeremote_core.dll')"),
    ('src/privacy_mode/win_topmost_window.rs',
     'pub const WIN_TOPMOST_INJECTED_PROCESS_EXE: &\'static str = "RuntimeBroker_rustdesk.exe";',
     'pub const WIN_TOPMOST_INJECTED_PROCESS_EXE: &\'static str = "RuntimeBroker_maeremote.exe";'),
    ('flutter/lib/desktop/pages/install_page.dart',
     "              Option(printer, label: 'Install {$appName} Printer'),\n",
     ''),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "    if (isWindows &&\n        !bind.isDisableSettings() &&\n        bind.mainGetBuildinOption(key: kOptionHideRemotePrinterSetting) != 'Y')\n      SettingsTabKey.printer,\n",
     ''),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "            if (isWindows)\n              _OptionCheckBox(\n                  context, 'Enable remote printer', kOptionEnableRemotePrinter,\n                  enabled: enabled, fakeValue: fakeValue),\n",
     ''),
    ('src/auth_2fa.rs',
     'const ISSUER: &str = "RustDesk";',
     'const ISSUER: &str = "MAE Remote";'),
    ('flutter/lib/common/widgets/toolbar.dart',
     "    'https://github.com/rustdesk/rustdesk/issues/14586';",
     "    'https://remote.maesuaisystem.com/';"),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "                          Text(\n                            'Copyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop\\nPortions © Purslane Tech Pte. Ltd. · GNU AGPL-3.0 · source: remote.maesuaisystem.com/source\\n$license',\n                            style: const TextStyle(color: Colors.white),\n                          ),",
     "                          Text(\n                            'Copyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop${license.isEmpty ? '' : '\\n$license'}',\n                            style: const TextStyle(color: Colors.white),\n                          ),\n                          // The licence notices (AGPL-3.0 section 5d) sit behind this link instead of in the box.\n                          InkWell(\n                            onTap: () => showDialog(\n                              context: context,\n                              builder: (ctx) => AlertDialog(\n                                title: const Text('Licence'),\n                                content: const SelectableText(\n                                    'MAE Remote Desktop includes open-source software.\\n\\n'\n                                    'Portions © Purslane Tech Pte. Ltd., licensed under the GNU Affero General '\n                                    'Public License version 3 (AGPL-3.0). You may copy, modify and share this '\n                                    'program under that licence. It comes WITHOUT ANY WARRANTY.\\n\\n'\n                                    'Licence text and complete source code:\\n'\n                                    'remote.maesuaisystem.com/source'),\n                                actions: [\n                                  TextButton(\n                                    onPressed: () => launchUrlString(\n                                        'https://remote.maesuaisystem.com/source/'),\n                                    child: const Text('Source code'),\n                                  ),\n                                  TextButton(\n                                    onPressed: () => Navigator.of(ctx).pop(),\n                                    child: Text(translate('OK')),\n                                  ),\n                                ],\n                              ),\n                            ),\n                            child: const Text(\n                              'Licence',\n                              style: TextStyle(\n                                  color: Colors.white,\n                                  fontSize: 12,\n                                  decoration: TextDecoration.underline),\n                            ).marginOnly(top: 4),\n                          ),"),
    ('src/lang/en.rs',
     '("doc_mac_permission", "https://rustdesk.com/docs/en/client/mac/#enable-permissions"),',
     '("doc_mac_permission", "https://remote.maesuaisystem.com/"),'),
    ('src/lang/en.rs',
     '("doc_fix_wayland", "https://rustdesk.com/docs/en/client/linux/#x11-required"),',
     '("doc_fix_wayland", "https://remote.maesuaisystem.com/"),'),
    ('src/ui_session_interface.rs',
     'join(format!("rustdesk_printer_{id}"))',
     'join(format!("maeremote_printer_{id}"))'),
    ('src/ui_session_interface.rs',
     'usage:<br><br> rustdesk --port-forward',
     'usage:<br><br> MAERemote --port-forward'),
    ('src/rendezvous_mediator.rs',
     'Run `rustdesk --deploy --token <api_token>`',
     'Run `MAERemote --deploy --token <api_token>`'),
    ('flutter/windows/runner/main.cpp',
     'std::wstring app_name = L"RustDesk";',
     'std::wstring app_name = L"MAE Remote";'),
    ('src/privacy_mode/win_topmost_window.rs',
     'PRIVACY_WINDOW_CLASS: &\'static str = "RustDeskPrivacyWindowClass";',
     'PRIVACY_WINDOW_CLASS: &\'static str = "MAERemotePrivacyWindowClass";'),
    ('src/privacy_mode/win_topmost_window.rs',
     'PRIVACY_WINDOW_NAME: &\'static str = "RustDeskPrivacyWindow";',
     'PRIVACY_WINDOW_NAME: &\'static str = "MAERemotePrivacyWindow";'),
    ('libs/virtual_display/dylib/src/win10/IddController.c',
     'Please try: Reinstall RustDesk with the cert option.',
     'Please try: Reinstall MAE Remote with the cert option.'),
    ('libs/virtual_display/dylib/src/win10/IddController.c',
     'const char* g_msgHeader = "RustDeskIdd: ";',
     'const char* g_msgHeader = "MAERemoteIdd: ";'),
    ('.github/workflows/third-party-RustDeskTempTopMostWindow.yml',
     '      - name: Build the project\n        run: |\n          cd RustDeskTempTopMostWindow && git checkout ecd8d6a139eee76845ea66423fb739af450fda90\n',
     "      - name: Build the project\n        run: |\n          cd RustDeskTempTopMostWindow && git checkout ecd8d6a139eee76845ea66423fb739af450fda90\n          # MAE: the privacy window's title/class (Task Manager can show the title); src/privacy_mode/win_topmost_window.rs matches\n          (Get-Content -Raw WindowInjection/dllmain.cpp).Replace('RustDeskPrivacyWindow', 'MAERemotePrivacyWindow') | Set-Content -NoNewline -Encoding utf8 WindowInjection/dllmain.cpp\n          if (Select-String -Quiet -Pattern 'RustDeskPrivacyWindow' WindowInjection/dllmain.cpp) { throw 'privacy window rename failed' }\n"),
    ('src/flutter_ffi.rs',
     '    } else if key == "transfer-job-id" {',
     '    } else if key == "mae-version" {\n        // MAE: the release shown to users, e.g. 1.5.0-9 (VERSION stays the upstream one for peer compatibility)\n        return format!("{}-{}", crate::VERSION, crate::common::MAE_BUILD);\n    } else if key == "transfer-job-id" {'),
    ('src/platform/windows.rs',
     '        version = crate::VERSION.replace("-", "."),',
     '        version = format!("{}-{}", crate::VERSION, crate::common::MAE_BUILD),'),
    ('src/platform/windows.rs',
     '    let version = crate::VERSION.replace("-", ".");',
     '    let version = format!("{}-{}", crate::VERSION, crate::common::MAE_BUILD);'),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "child: Text('${translate('Version')}: $version')",
     "child: Text('${translate('Version')}: ${bind.mainGetCommonSync(key: 'mae-version')}')"),
    ('flutter/lib/desktop/pages/desktop_setting_page.dart',
     "'Copyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop${license.isEmpty ? '' : '\\n$license'}',",
     "'MAE Remote Desktop ${bind.mainGetCommonSync(key: 'mae-version')}\\nCopyright © ${DateTime.now().toString().substring(0, 4)} MAE Remote Desktop${license.isEmpty ? '' : '\\n$license'}',"),
    ('flutter/lib/desktop/pages/connection_page.dart',
     'const url = "https://rustdesk.com/pricing";',
     'const url = "https://remote.maesuaisystem.com/";'),
    ('flutter/lib/desktop/pages/desktop_home_page.dart',
     "? 'https://github.com/rustdesk/rustdesk/releases/tag/${bind.mainGetNewVersion()}'",
     "? 'https://remote.maesuaisystem.com/'"),
]

# r10 (SignPath): ชุดติดตั้งเป็นโอเพนซอร์สทั้งหมด — ไม่มีไดรเวอร์จอเสมือน Amyuni จึงเสนอ virtual display เฉพาะเมื่อมีไฟล์ไดรเวอร์
OSS_EDITS = [
    ('src/virtual_display_manager.rs',
     '    #[cfg(target_os = "windows")]\n    {\n        is_windows_version_or_greater(10, 0, 19041, 0, 0)\n    }',
     '    #[cfg(target_os = "windows")]\n    {\n        // MAE: the Amyuni driver (closed source) is not shipped; offer virtual displays only when its files are present\n        is_windows_version_or_greater(10, 0, 19041, 0, 0)\n            && std::env::current_exe()\n                .ok()\n                .and_then(|p| p.parent().map(|d| d.join("usbmmidd_v2").exists()))\n                .unwrap_or(false)\n    }'),
    ('src/server/terminal_service.rs',
     '// vim, Claude Code, and other TUI applications hang when ConPTY is created',
     '// vim and other TUI applications hang when ConPTY is created'),
]

# ชื่องานของ workflow ที่ mae-windows.yml เรียกใช้ (ไม่ให้ชื่อต้นทางขึ้นในหน้า Actions)
WORKFLOW_EDITS = [
    ('.github/workflows/flutter-build.yml', 'name: Build the flutter version of the RustDesk\n', 'name: Build (reusable)\n'),
    ('.github/workflows/third-party-RustDeskTempTopMostWindow.yml', 'name: build RustDeskTempTopMostWindow\n',
     'name: Build window helper (reusable)\n'),
]

# ลิงก์ที่มีหลายจุดในไฟล์เดียว: แทนทุกจุด (ต้องเจออย่างน้อย 1)
EDITS_ALL = [
    ('libs/portable/src/main.rs', 'RuntimeBroker_rustdesk.exe', 'RuntimeBroker_maeremote.exe'),
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
    for rel, old, new in EDITS + TRAFFIC_EDITS + FIT_EDITS + INSTALL_EDITS + NAME_EDITS + OSS_EDITS + WORKFLOW_EDITS:
        edit(root, rel, old, new)
    for rel, old, new in EDITS_ALL:
        edit(root, rel, old, new, all_=True)
    print('icons:')
    write_icons(root)
    print('done')


if __name__ == '__main__':
    main()
