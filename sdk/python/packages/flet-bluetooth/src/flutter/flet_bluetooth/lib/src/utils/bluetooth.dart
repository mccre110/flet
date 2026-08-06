import 'dart:typed_data';

import 'package:flet/flet.dart';
import 'package:universal_ble/universal_ble.dart';

Uint8List parseBytes(dynamic value, [Uint8List? defaultValue]) {
  if (value == null) {
    return defaultValue ?? Uint8List(0);
  }
  if (value is Uint8List) {
    return value;
  }
  if (value is ByteBuffer) {
    return value.asUint8List();
  }
  if (value is List) {
    return Uint8List.fromList(value.cast<int>());
  }
  return defaultValue ?? Uint8List(0);
}

ManufacturerDataFilter? parseManufacturerDataFilter(dynamic value) {
  if (value == null || value is! Map) return null;
  final company = value["company_identifier"] ?? value["company_id"];
  if (company is! num) return null;
  return ManufacturerDataFilter(
    companyIdentifier: company.toInt(),
    payloadPrefix: value["payload_prefix"] != null
        ? parseBytes(value["payload_prefix"])
        : null,
    payloadMask:
        value["payload_mask"] != null ? parseBytes(value["payload_mask"]) : null,
  );
}

ExclusionFilter? parseExclusionFilter(dynamic value) {
  if (value == null || value is! Map) return null;
  return ExclusionFilter(
    services: (value["services"] as List?)?.cast<String>() ?? const [],
    manufacturerDataFilter: (value["manufacturer_data_filter"] as List?)
            ?.map(parseManufacturerDataFilter)
            .whereType<ManufacturerDataFilter>()
            .toList() ??
        const [],
    namePrefix: value["name_prefix"] as String?,
  );
}

ScanFilter? parseScanFilter(dynamic value, [ScanFilter? defaultValue]) {
  if (value == null) return defaultValue;
  if (value is! Map) return defaultValue;
  return ScanFilter(
    withServices: (value["with_services"] as List?)?.cast<String>() ?? const [],
    withNamePrefix:
        (value["with_name_prefix"] as List?)?.cast<String>() ?? const [],
    withManufacturerData: (value["with_manufacturer_data"] as List?)
            ?.map(parseManufacturerDataFilter)
            .whereType<ManufacturerDataFilter>()
            .toList() ??
        const [],
    exclusionFilters: (value["exclusion_filters"] as List?)
            ?.map(parseExclusionFilter)
            .whereType<ExclusionFilter>()
            .toList() ??
        const [],
  );
}

AndroidOptions? parseAndroidOptions(dynamic value) {
  if (value == null || value is! Map) return null;
  return AndroidOptions(
    requestLocationPermission: value["request_location_permission"] as bool?,
    scanMode: parseEnum(AndroidScanMode.values, value["scan_mode"] as String?),
    reportDelayMillis: value["report_delay_millis"] is num
        ? (value["report_delay_millis"] as num).toInt()
        : null,
    callbackType: (value["callback_type"] as List?)
        ?.map((e) => parseEnum(AndroidScanCallbackType.values, e as String?))
        .whereType<AndroidScanCallbackType>()
        .toList(),
    matchMode: parseEnum(
        AndroidScanMatchMode.values, value["match_mode"] as String?),
    numOfMatches: parseEnum(
        AndroidScanNumOfMatches.values, value["num_of_matches"] as String?),
    legacy: value["legacy"] as bool?,
  );
}

WebOptions? parseWebOptions(dynamic value) {
  if (value == null || value is! Map) return null;
  return WebOptions(
    optionalServices:
        (value["optional_services"] as List?)?.cast<String>() ?? const [],
    optionalManufacturerData: (value["optional_manufacturer_data"] as List?)
            ?.map((e) => (e as num).toInt())
            .toList() ??
        const [],
  );
}

PlatformConfig? parsePlatformConfig({
  dynamic androidOptions,
  dynamic webOptions,
}) {
  final android = parseAndroidOptions(androidOptions);
  final web = parseWebOptions(webOptions);
  if (android == null && web == null) return null;
  return PlatformConfig(android: android, web: web);
}

BleCommand? parsePairingCommand(dynamic args) {
  if (args is! Map) return null;
  final service = args["service_uuid"] as String?;
  final characteristic = args["characteristic_uuid"] as String?;
  if (service == null || characteristic == null) return null;
  return BleCommand(service: service, characteristic: characteristic);
}

Map<String, dynamic> manufacturerDataToMap(ManufacturerData data) => {
      "company_id": data.companyId,
      "payload": data.payload,
    };

Map<String, dynamic> bleDeviceToMap(BleDevice device) => {
      "device_id": device.deviceId,
      "name": device.name,
      "rssi": device.rssi,
      "is_system_device": device.isSystemDevice,
      "paired": device.paired,
      "service_uuids": device.services,
      "manufacturer_data_list":
          device.manufacturerDataList.map(manufacturerDataToMap).toList(),
      "service_data": device.serviceData.map((k, v) => MapEntry(k, v)),
      "timestamp": device.timestamp,
    };

Map<String, dynamic> bleDescriptorToMap(BleDescriptor descriptor) => {
      "uuid": descriptor.uuid,
    };

Map<String, dynamic> bleCharacteristicToMap(BleCharacteristic characteristic) =>
    {
      "uuid": characteristic.uuid,
      "properties": characteristic.properties.map((e) => e.name).toList(),
      "descriptors":
          characteristic.descriptors.map(bleDescriptorToMap).toList(),
    };

Map<String, dynamic> bleServiceToMap(BleService service) => {
      "uuid": service.uuid,
      "characteristics":
          service.characteristics.map(bleCharacteristicToMap).toList(),
    };

Map<String, dynamic> okResult([dynamic value]) {
  if (value == null) {
    return {"ok": true};
  }
  return {"ok": true, "value": value};
}

Map<String, dynamic> errorResult(Object error) {
  if (error is UniversalBleException) {
    return {
      "ok": false,
      "code": error.code.name,
      "message": error.message,
      if (error.details != null) "details": error.details.toString(),
    };
  }
  return {
    "ok": false,
    "code": UniversalBleErrorCode.unknownError.name,
    "message": error.toString(),
  };
}
