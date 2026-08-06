# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](http://keepachangelog.com/en/1.0.0/)
and this project adheres to [Semantic Versioning](http://semver.org/spec/v2.0.0.html).

## 0.1.0

### Added

- Initial release of `flet-bluetooth` with BLE central and peripheral services powered by
  [`universal_ble`](https://pub.dev/packages/universal_ble) (BSD-3-Clause).
- [`Bluetooth`](https://flet.dev/docs/services/bluetooth/bluetooth) service for central /
  client operations: adapter availability, permissions, scanning, connect/disconnect,
  GATT discover / read / write / subscribe, pairing, MTU, and RSSI.
- [`BluetoothPeripheral`](https://flet.dev/docs/services/bluetooth/bluetoothperipheral)
  service for peripheral / server operations: declarative GATT service tree, advertising,
  characteristic value updates, and observational read/write/subscription events.
- Shared types, enums, and events for scan filters, discovered devices/services, GATT
  trees, and peripheral capabilities.
- Docs, scanner and peripheral examples, and integration smoke tests.
