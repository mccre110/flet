---
examples: "extensions/bluetooth"
title: "Bluetooth"
---

import TabItem from '@theme/TabItem';
import Tabs from '@theme/Tabs';
import {CodeExample} from '@site/src/components/crocodocs';

# Bluetooth

Bluetooth Low Energy (BLE) services for your [Flet](https://flet.dev) apps via the
`flet-bluetooth` extension.

Powered by Flutter's [`universal_ble`](https://pub.dev/packages/universal_ble)
package (BSD-3-Clause). Classic Bluetooth is not supported — BLE only.

## Services

| Service | Role | Docs |
|---------|------|------|
| [`Bluetooth`](bluetooth.md) | Central / client (scan, connect, GATT) | [Bluetooth](bluetooth.md) |
| [`BluetoothPeripheral`](bluetoothperipheral.md) | Peripheral / server (advertise, GATT server) | [BluetoothPeripheral](bluetoothperipheral.md) |

:::warning[Single peripheral instance]
Only one [`BluetoothPeripheral`](bluetoothperipheral.md) instance may be active at a
time, because `universal_ble` read/write request handlers are process-global.
:::

## Platform Support

### Bluetooth (central)

| Platform  | Windows | macOS | Linux | iOS | Android | Web |
|-----------|---------|-------|-------|-----|---------|-----|
| Supported | ✅       | ✅     | ✅     | ✅   | ✅       | ⚠️  |

Web Bluetooth is available where the browser supports it and typically requires a
user gesture (user activation) to start a scan or request a device.

### BluetoothPeripheral

| Platform  | Windows | macOS | Linux | iOS | Android | Web |
|-----------|---------|-------|-------|-----|---------|-----|
| Supported | ✅       | ✅     | ⚠️     | ✅   | ✅       | ❌   |

Linux peripheral support depends on upstream `universal_ble` completeness and may
be limited. Web does not support BLE peripheral / GATT server mode.

## Usage

Add `flet-bluetooth` to your project dependencies:

<Tabs groupId="uv--pip">
<TabItem value="uv" label="uv">
```bash
uv add flet-bluetooth
```

</TabItem>
<TabItem value="pip" label="pip">
```bash
pip install flet-bluetooth  # (1)!
```

1. After this, you will have to manually add this package to your `requirements.txt` or `pyproject.toml`.
</TabItem>
</Tabs>

Register a service on [`Page.services`][flet.Page.services] before calling methods:

```python
import flet as ft
import flet_bluetooth as fbt

def main(page: ft.Page):
    bt = fbt.Bluetooth()
    page.services.append(bt)
    # await bt.request_permissions()
    # await bt.start_scan()

ft.run(main)
```

## Requirements

Declare Bluetooth permissions when packaging your app. Prefer the predefined
`bluetooth`
[permission bundle](../../publish/index.md#predefined-cross-platform-permission-bundles).

### Cross-platform

<Tabs groupId="flet-build--pyproject-toml">
<TabItem value="flet-build" label="flet build">
```bash
flet build <target_platform> --permissions bluetooth
```
</TabItem>
<TabItem value="pyproject-toml" label="pyproject.toml">
```toml
[tool.flet]
permissions = ["bluetooth"]
```
</TabItem>
</Tabs>

The `bluetooth` bundle expands to platform-specific entries, including:

- **Android:** `BLUETOOTH_CONNECT`, `BLUETOOTH_SCAN` (with
  `neverForLocation`), `BLUETOOTH_ADVERTISE`, legacy `BLUETOOTH` /
  `BLUETOOTH_ADMIN` (max SDK 30), and location permissions capped to older API
  levels where required for scanning.
- **iOS / macOS:** `NSBluetoothAlwaysUsageDescription` and
  `NSBluetoothPeripheralUsageDescription` Info.plist keys.
- **macOS:** `com.apple.security.device.bluetooth` entitlement.

:::note[Android scan location]
`BLUETOOTH_SCAN` is declared with `usesPermissionFlags="neverForLocation"` in the
bundle, so scanning does not imply location access on modern Android.
:::

### Android (manual)

If you prefer to set permissions yourself:

<Tabs groupId="flet-build--pyproject-toml">
<TabItem value="flet-build" label="flet build">
```bash
flet build apk \
  --android-permissions android.permission.BLUETOOTH_CONNECT=true \
  --android-permissions android.permission.BLUETOOTH_SCAN=true \
  --android-permissions android.permission.BLUETOOTH_ADVERTISE=true
```
</TabItem>
<TabItem value="pyproject-toml" label="pyproject.toml">
```toml
[tool.flet.android.permission]
"android.permission.BLUETOOTH_CONNECT" = true
"android.permission.BLUETOOTH_SCAN" = { usesPermissionFlags = "neverForLocation" }
"android.permission.BLUETOOTH_ADVERTISE" = true
```
</TabItem>
</Tabs>

See also: [setting Android permissions](../../publish/android.md#permissions).

### iOS

<Tabs groupId="flet-build--pyproject-toml">
<TabItem value="flet-build" label="flet build">
```bash
flet build ipa \
  --info-plist NSBluetoothAlwaysUsageDescription="This app uses Bluetooth to connect to nearby devices." \
  --info-plist NSBluetoothPeripheralUsageDescription="This app uses Bluetooth to advertise services to nearby devices."
```
</TabItem>
<TabItem value="pyproject-toml" label="pyproject.toml">
```toml
[tool.flet.ios.info]
NSBluetoothAlwaysUsageDescription = "This app uses Bluetooth to connect to nearby devices."
NSBluetoothPeripheralUsageDescription = "This app uses Bluetooth to advertise services to nearby devices."
```
</TabItem>
</Tabs>

See also: [setting iOS Info.plist entries](../../publish/ios.md#infoplist).

### macOS

<Tabs groupId="flet-build--pyproject-toml">
<TabItem value="flet-build" label="flet build">
```bash
flet build macos \
  --info-plist NSBluetoothAlwaysUsageDescription="This app uses Bluetooth to connect to nearby devices." \
  --info-plist NSBluetoothPeripheralUsageDescription="This app uses Bluetooth to advertise services to nearby devices." \
  --macos-entitlements com.apple.security.device.bluetooth=true
```
</TabItem>
<TabItem value="pyproject-toml" label="pyproject.toml">
```toml
[tool.flet.macos.info]
NSBluetoothAlwaysUsageDescription = "This app uses Bluetooth to connect to nearby devices."
NSBluetoothPeripheralUsageDescription = "This app uses Bluetooth to advertise services to nearby devices."

[tool.flet.macos.entitlement]
"com.apple.security.device.bluetooth" = true
```
</TabItem>
</Tabs>

See also:

- [macOS permissions](../../publish/macos.md#permissions)
- [macOS entitlements](../../publish/macos.md#entitlements)

## Examples

<CodeExample path={frontMatter.examples + '/scanner/main.py'} language="python" />

<CodeExample path={frontMatter.examples + '/peripheral/main.py'} language="python" />
