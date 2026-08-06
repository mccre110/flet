import 'dart:typed_data';

import 'package:flet/flet.dart';
import 'package:universal_ble/universal_ble.dart';

import 'bluetooth.dart';

const int gattSuccess = 0x00;
const int gattWriteNotPermitted = 0x03;
const int gattInvalidOffset = 0x07;
const int gattInvalidAttributeLength = 0x0d;
const int maxGattAttributeLength = 512;

ManufacturerData? parsePeripheralManufacturerData(dynamic value) {
  if (value == null) return null;
  final map = Map<String, dynamic>.from(value as Map);
  return ManufacturerData(
    parseInt(map["company_identifier"], 0)!,
    parseBytes(map["data"]),
  );
}

List<CharacteristicProperty> parseCharacteristicProperties(dynamic value) {
  if (value is! List) return const [];
  return value
      .whereType<String>()
      .map((name) => parseEnum(CharacteristicProperty.values, name))
      .whereType<CharacteristicProperty>()
      .toList();
}

List<PeripheralAttributePermission> parsePeripheralPermissions(dynamic value) {
  if (value is! List) return const [];
  return value
      .whereType<String>()
      .map((name) => parseEnum(PeripheralAttributePermission.values, name))
      .whereType<PeripheralAttributePermission>()
      .toList();
}

BlePeripheralDescriptor? parseBlePeripheralDescriptor(dynamic value) {
  if (value == null) return null;
  final map = Map<String, dynamic>.from(value as Map);
  final uuid = map["uuid"] as String?;
  if (uuid == null) return null;
  final permissions = parsePeripheralPermissions(map["permissions"]);
  return BlePeripheralDescriptor(
    uuid: uuid,
    value: convertToUint8List(map["value"]),
    permissions: permissions.isEmpty ? null : permissions,
  );
}

BlePeripheralCharacteristic? parseBlePeripheralCharacteristic(dynamic value) {
  if (value == null) return null;
  final map = Map<String, dynamic>.from(value as Map);
  final uuid = map["uuid"] as String?;
  if (uuid == null) return null;
  final descriptors = (map["descriptors"] as List? ?? const [])
      .map(parseBlePeripheralDescriptor)
      .whereType<BlePeripheralDescriptor>()
      .toList();
  return BlePeripheralCharacteristic(
    uuid: uuid,
    properties: parseCharacteristicProperties(map["properties"]),
    permissions: parsePeripheralPermissions(map["permissions"]),
    value: convertToUint8List(map["value"]),
    descriptors: descriptors,
  );
}

BlePeripheralService? parseBlePeripheralService(dynamic value) {
  if (value == null) return null;
  final map = Map<String, dynamic>.from(value as Map);
  final uuid = map["uuid"] as String?;
  if (uuid == null) return null;
  final characteristics = (map["characteristics"] as List? ?? const [])
      .map(parseBlePeripheralCharacteristic)
      .whereType<BlePeripheralCharacteristic>()
      .toList();
  return BlePeripheralService(
    uuid: uuid,
    primary: parseBool(map["primary"], true)!,
    characteristics: characteristics,
  );
}

List<BlePeripheralService> parseBlePeripheralServices(dynamic value) {
  if (value is! List) return const [];
  return value
      .map(parseBlePeripheralService)
      .whereType<BlePeripheralService>()
      .toList();
}

Map<String, dynamic> peripheralCapabilitiesToMap(BlePeripheralCapabilities c) {
  return {
    "supports_peripheral_mode": c.supportsPeripheralMode,
    "supports_manufacturer_data_in_advertisement":
        c.supportsManufacturerDataInAdvertisement,
    "supports_manufacturer_data_in_scan_response":
        c.supportsManufacturerDataInScanResponse,
    "supports_service_data_in_advertisement":
        c.supportsServiceDataInAdvertisement,
    "supports_service_data_in_scan_response":
        c.supportsServiceDataInScanResponse,
    "supports_targeted_characteristic_update":
        c.supportsTargetedCharacteristicUpdate,
    "supports_advertising_timeout": c.supportsAdvertisingTimeout,
  };
}

String descriptorCacheKey(String characteristicId, String descriptorId) {
  return "${BleUuidParser.string(characteristicId)}:${BleUuidParser.string(descriptorId)}";
}

Uint8List sliceBleValue(Uint8List? value, int offset) {
  if (value == null || value.isEmpty || offset >= value.length) {
    return Uint8List(0);
  }
  if (offset <= 0) return value;
  return Uint8List.fromList(value.sublist(offset));
}

Uint8List applyBleWrite(Uint8List? existing, int offset, Uint8List incoming) {
  if (offset <= 0) {
    return Uint8List.fromList(incoming);
  }
  final current = existing ?? Uint8List(0);
  final end = offset + incoming.length;
  final length = end > current.length ? end : current.length;
  final result = Uint8List(length);
  result.setRange(0, current.length, current);
  result.setRange(offset, end, incoming);
  return result;
}
