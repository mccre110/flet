---
class_name: "flet_bluetooth.BluetoothPeripheral"
examples: "extensions/bluetooth"
title: "BluetoothPeripheral"
---

import {ClassMembers, ClassSummary, CodeExample} from '@site/src/components/crocodocs';

<ClassSummary name={frontMatter.class_name} />

A service for Bluetooth Low Energy (BLE) **peripheral / server** operations:
declarative GATT services, advertising, and characteristic updates.

Add an instance to [`Page.services`][flet.Page.services] before calling methods.
See the [Bluetooth overview](index.md) for install instructions, platform support,
and permission setup.

:::warning[Synchronous value cache]
GATT characteristic and descriptor **read requests are synchronous** on the
native side (`universal_ble`'s `OnPeripheralReadRequest` returns a value
immediately and cannot await Python). Flet control events are one-way, so Python
cannot answer reads.

The Flutter side therefore owns a **value cache** keyed by characteristic (and
descriptor) UUID. Read handlers answer instantly from that cache (supporting
`offset` slicing; empty bytes if missing). Write handlers update the cache,
return success (or a GATT status for static rules such as not writable / value
too long), then fire observational events to Python.

Seed the cache by setting [`services`][flet_bluetooth.BluetoothPeripheral.services]
characteristic/descriptor `value` fields, and keep it current with
[`update_characteristic_value()`][flet_bluetooth.BluetoothPeripheral.update_characteristic_value].
:::

:::note[Single instance]
Only one `BluetoothPeripheral` instance may be active at a time because
`universal_ble` read/write request handlers are process-global.

When [`services`][flet_bluetooth.BluetoothPeripheral.services] changes while
advertising, advertising is stopped, services are cleared and re-added, and
advertising is **not** automatically restarted.
:::

## Example

<CodeExample path={frontMatter.examples + '/peripheral/main.py'} language="python" />

<ClassMembers name={frontMatter.class_name} />
