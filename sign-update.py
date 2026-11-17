#!/usr/bin/env python3
"""Signed update metadata for MAE Remote automatic updates (the client checks it in src/update_metadata.rs and
src/updater/artifact.rs: mae_verified_update_artifact).

usage: sign-update.py <installer.exe> <version, e.g. 1.5.3-11> <release tag, e.g. mae-1.5.3-r11> <out dir>

Writes <out dir>/mae-update.json and mae-update.json.sig, then verifies both exactly the way the client does, with the
public key taken from the client source (rustdesk/src/update_metadata.rs), so a key mismatch stops the release.
The signing key is /root/.mae-remote/update-signing.key (base64 Ed25519 seed, root only, never on the web server).
"""
import base64
import ctypes
import datetime
import hashlib
import json
import os
import re
import sys

KEY_FILE = '/root/.mae-remote/update-signing.key'
KEY_ID = 'mae-2026-11-ed25519'
CONTEXT = b'MAE Remote update metadata v1\n'
APP = PACKAGE_ID = 'maeremote'
RELEASES = 'https://github.com/maxspeedcom/mae-remote-desktop/releases/download'
_HERE = os.path.dirname(os.path.abspath(__file__))
CLIENT_SRC = next((p for p in (os.path.join(_HERE, 'rustdesk', 'src', 'update_metadata.rs'),
                                os.path.join(_HERE, 'src', 'update_metadata.rs')) if os.path.exists(p)),
                  os.path.join(_HERE, 'rustdesk', 'src', 'update_metadata.rs'))

na = ctypes.CDLL('libsodium.so.23')
if na.sodium_init() < 0:
    sys.exit('libsodium init failed')


def client_public_key():
    src = open(CLIENT_SRC, encoding='utf-8').read()
    m = re.search(r'key_id: "([^"]+)",\s*algorithm: SIGNATURE_ALGORITHM,\s*public_key: \[([\d,\s]+)\]', src)
    if not m:
        sys.exit('STOP: trusted update key not found in ' + CLIENT_SRC)
    key = bytes(int(x) for x in m.group(2).replace('\n', ' ').split(',') if x.strip())
    if m.group(1) != KEY_ID or len(key) != 32:
        sys.exit('STOP: client trusts key id %r, signer uses %r' % (m.group(1), KEY_ID))
    return key


def sign(body):
    seed = base64.b64decode(open(KEY_FILE).read().strip())
    pk = (ctypes.c_ubyte * 32)()
    sk = (ctypes.c_ubyte * 64)()
    assert na.crypto_sign_seed_keypair(pk, sk, (ctypes.c_ubyte * 32).from_buffer_copy(seed)) == 0
    msg = CONTEXT + body
    sig = (ctypes.c_ubyte * 64)()
    assert na.crypto_sign_detached(sig, None, msg, ctypes.c_ulonglong(len(msg)), sk) == 0
    ctypes.memset(sk, 0, 64)
    return bytes(sig), bytes(pk)


def verify(meta_path, sig_path, exe, version, release, pub):
    """The client's checks (update_metadata.rs verify_update_metadata_with_options + artifact rules)."""
    body = open(meta_path, 'rb').read()
    s = json.loads(open(sig_path, 'rb').read())
    assert s['schema_version'] == 1 and s['algorithm'] == 'ed25519' and s['key_id'] == KEY_ID, 'signature header'
    raw = base64.b64decode(s['signature'])
    assert len(raw) == 64 and base64.b64encode(raw).decode() == s['signature'], 'signature encoding'
    msg = CONTEXT + body
    ok = na.crypto_sign_verify_detached(raw, msg, ctypes.c_ulonglong(len(msg)), pub) == 0
    assert ok, 'signature does not verify with the key the client trusts'
    m = json.loads(body)
    assert m['schema_version'] == 1 and m['signature_key_id'] == s['key_id'], 'metadata header'
    assert m['app'] == APP and m['package_id'] == PACKAGE_ID, 'app / package id'
    assert m['version'] == version and m['release_id'] == release, 'version / release id'
    hits = [a for a in m['artifacts'] if (a['platform'], a['arch'], a['format']) == ('windows', 'x86_64', 'exe')]
    assert len(hits) == 1, 'exactly one windows/x86_64/exe artifact'
    a = hits[0]
    assert re.fullmatch(r'[A-Za-z0-9._-]+', a['file_name']) and a['file_name'] not in ('.', '..'), 'file name'
    assert a['url'] == '%s/%s/%s' % (RELEASES, release, a['file_name']), 'artifact url'
    data = open(exe, 'rb').read()
    assert a['size'] == len(data) and a['sha256'] == hashlib.sha256(data).hexdigest(), 'size / sha256 of the installer'
    assert a['file_name'] == os.path.basename(exe), 'installer name'
    return a


def main():
    exe, version, release, out = sys.argv[1:5]
    if not re.fullmatch(r'[A-Za-z0-9._-]+', release):
        sys.exit('STOP: bad release tag ' + release)
    pub = client_public_key()
    name = os.path.basename(exe)
    data = open(exe, 'rb').read()
    meta = {
        'schema_version': 1, 'app': APP, 'package_id': PACKAGE_ID, 'version': version, 'release_id': release,
        'published_at': datetime.datetime.now(datetime.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ'),
        'signature_key_id': KEY_ID,
        'artifacts': [{'platform': 'windows', 'arch': 'x86_64', 'format': 'exe',
                       'url': '%s/%s/%s' % (RELEASES, release, name), 'file_name': name,
                       'size': len(data), 'sha256': hashlib.sha256(data).hexdigest()}],
    }
    body = (json.dumps(meta, indent=2) + '\n').encode()
    sig, signer_pub = sign(body)
    if signer_pub != pub:
        sys.exit('STOP: the signing key is not the key the client trusts')
    os.makedirs(out, exist_ok=True)
    meta_path, sig_path = os.path.join(out, 'mae-update.json'), os.path.join(out, 'mae-update.json.sig')
    open(meta_path, 'wb').write(body)
    open(sig_path, 'w').write(json.dumps({'schema_version': 1, 'algorithm': 'ed25519', 'key_id': KEY_ID,
                                          'signature': base64.b64encode(sig).decode()}) + '\n')
    a = verify(meta_path, sig_path, exe, version, release, pub)
    print('signed + verified: %s %s (%d bytes, sha256 %s…) release %s' % (name, version, a['size'], a['sha256'][:12], release))


if __name__ == '__main__':
    main()
