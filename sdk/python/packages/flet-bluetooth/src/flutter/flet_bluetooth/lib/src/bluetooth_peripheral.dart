import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:universal_ble/universal_ble.dart';

import 'utils/bluetooth.dart';
import 'utils/bluetooth_peripheral.dart';

class BluetoothPeripheralService extends FletService {
  BluetoothPeripheralService({required super.control});

  static BluetoothPeripheralService? _activeInstance;

  final Map<String, Uint8List> _characteristicValues = {};
  final Map<String, Uint8List> _descriptorValues = {};
  final Set<String> _writableCharacteristics = {};
  final Set<String> _writableDescriptors = {};

  String? _lastServicesFingerprint;
  bool _ownsHandlers = false;
  bool _syncingServices = false;

  StreamSubscription<BlePeripheralAdvertisingStateChanged>?
      _advertisingStateSubscription;
  StreamSubscription<BlePeripheralCharacteristicSubscriptionChanged>?
      _subscriptionSubscription;
  StreamSubscription<BlePeripheralConnectionStateChanged>?
      _connectionSubscription;
  StreamSubscription<BlePeripheralServiceAdded>? _serviceAddedSubscription;
  StreamSubscription<BlePeripheralMtuChanged>? _mtuSubscription;

  @override
  void init() {
    super.init();
    debugPrint(
        "BluetoothPeripheral(${control.id}).init: ${control.properties}");

    if (_activeInstance != null && _activeInstance != this) {
      throw StateError(
        "Only one BluetoothPeripheral service can be active at a time. "
        "universal_ble read/write request handlers are process-global.",
      );
    }
    _activeInstance = this;
    _ownsHandlers = true;

    control.addInvokeMethodListener(_invokeMethod);
    _installHandlers();
    registerEvents();
    unawaited(_syncServices());
  }

  @override
  void update() {
    debugPrint(
        "BluetoothPeripheral(${control.id}).update: ${control.properties}");
    registerEvents();
    unawaited(_syncServices());
  }

  void _installHandlers() {
    UniversalBlePeripheral.setReadRequestHandlers(_onReadRequest);
    UniversalBlePeripheral.setWriteRequestHandlers(_onWriteRequest);
    UniversalBlePeripheral.setDescriptorReadRequestHandlers(
      _onDescriptorReadRequest,
    );
    UniversalBlePeripheral.setDescriptorWriteRequestHandlers(
      _onDescriptorWriteRequest,
    );
  }

  void _clearHandlers() {
    UniversalBlePeripheral.setReadRequestHandlers(null);
    UniversalBlePeripheral.setWriteRequestHandlers(null);
    UniversalBlePeripheral.setDescriptorReadRequestHandlers(null);
    UniversalBlePeripheral.setDescriptorWriteRequestHandlers(null);
  }

  void registerEvents() {
    _advertisingStateSubscription?.cancel();
    _advertisingStateSubscription = null;
    _subscriptionSubscription?.cancel();
    _subscriptionSubscription = null;
    _connectionSubscription?.cancel();
    _connectionSubscription = null;
    _serviceAddedSubscription?.cancel();
    _serviceAddedSubscription = null;
    _mtuSubscription?.cancel();
    _mtuSubscription = null;

    if (control.hasEventHandler("advertising_state_change") ||
        control.hasEventHandler("error")) {
      _advertisingStateSubscription =
          UniversalBlePeripheral.advertisingStateStream.listen((event) {
        control.triggerEvent("advertising_state_change", {
          "state": event.state.name,
          "error": event.error,
        });
        if (event.error != null && control.hasEventHandler("error")) {
          control.triggerEvent("error", event.error);
        }
      });
    }

    if (control.hasEventHandler("subscription_change")) {
      _subscriptionSubscription = UniversalBlePeripheral
          .characteristicSubscriptionStream
          .listen((event) {
        control.triggerEvent("subscription_change", {
          "device_id": event.deviceId,
          "characteristic_uuid": event.characteristicId,
          "is_subscribed": event.isSubscribed,
          "name": event.name,
        });
      });
    }

    if (control.hasEventHandler("connection_change")) {
      _connectionSubscription =
          UniversalBlePeripheral.connectionStateStream.listen((event) {
        control.triggerEvent("connection_change", {
          "device_id": event.deviceId,
          "connected": event.connected,
        });
      });
    }

    if (control.hasEventHandler("service_added")) {
      _serviceAddedSubscription =
          UniversalBlePeripheral.serviceAddedStream.listen((event) {
        control.triggerEvent("service_added", {
          "service_uuid": event.serviceId,
          "error": event.error,
        });
      });
    }

    if (control.hasEventHandler("mtu_change")) {
      _mtuSubscription =
          UniversalBlePeripheral.mtuChangedStream.listen((event) {
        control.triggerEvent("mtu_change", {
          "device_id": event.deviceId,
          "mtu": event.mtu,
        });
      });
    }
  }

  PeripheralReadRequestResult? _onReadRequest(
    String deviceId,
    String characteristicId,
    int offset,
    Uint8List? value,
  ) {
    final key = BleUuidParser.string(characteristicId);
    final cached = _characteristicValues[key];
    final sliced = sliceBleValue(cached, offset);
    if (control.hasEventHandler("characteristic_read")) {
      control.triggerEvent("characteristic_read", {
        "device_id": deviceId,
        "characteristic_uuid": key,
        "offset": offset,
        "value": sliced,
      });
    }
    return PeripheralReadRequestResult(
      value: sliced,
      offset: offset,
      status: gattSuccess,
    );
  }

  PeripheralWriteRequestResult? _onWriteRequest(
    String deviceId,
    String characteristicId,
    int offset,
    Uint8List? value,
  ) {
    final key = BleUuidParser.string(characteristicId);
    final incoming = value ?? Uint8List(0);

    if (!_writableCharacteristics.contains(key)) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattWriteNotPermitted,
      );
    }
    if (offset < 0) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattInvalidOffset,
      );
    }
    final existing = _characteristicValues[key];
    final next = applyBleWrite(existing, offset, incoming);
    if (next.length > maxGattAttributeLength) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattInvalidAttributeLength,
      );
    }

    _characteristicValues[key] = next;
    if (control.hasEventHandler("characteristic_write")) {
      control.triggerEvent("characteristic_write", {
        "device_id": deviceId,
        "characteristic_uuid": key,
        "offset": offset,
        "value": incoming,
      });
    }
    return PeripheralWriteRequestResult(
      value: incoming,
      offset: offset,
      status: gattSuccess,
    );
  }

  PeripheralReadRequestResult? _onDescriptorReadRequest(
    String deviceId,
    String characteristicId,
    String descriptorId,
    int offset,
    Uint8List? value,
  ) {
    final charKey = BleUuidParser.string(characteristicId);
    final descKey = BleUuidParser.string(descriptorId);
    final cacheKey = descriptorCacheKey(charKey, descKey);
    final sliced = sliceBleValue(_descriptorValues[cacheKey], offset);
    if (control.hasEventHandler("descriptor_read")) {
      control.triggerEvent("descriptor_read", {
        "device_id": deviceId,
        "characteristic_uuid": charKey,
        "descriptor_uuid": descKey,
        "offset": offset,
        "value": sliced,
      });
    }
    return PeripheralReadRequestResult(
      value: sliced,
      offset: offset,
      status: gattSuccess,
    );
  }

  PeripheralWriteRequestResult? _onDescriptorWriteRequest(
    String deviceId,
    String characteristicId,
    String descriptorId,
    int offset,
    Uint8List? value,
  ) {
    final charKey = BleUuidParser.string(characteristicId);
    final descKey = BleUuidParser.string(descriptorId);
    final cacheKey = descriptorCacheKey(charKey, descKey);
    final incoming = value ?? Uint8List(0);

    if (!_writableDescriptors.contains(cacheKey)) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattWriteNotPermitted,
      );
    }
    if (offset < 0) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattInvalidOffset,
      );
    }
    final next =
        applyBleWrite(_descriptorValues[cacheKey], offset, incoming);
    if (next.length > maxGattAttributeLength) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattInvalidAttributeLength,
      );
    }

    _descriptorValues[cacheKey] = next;
    if (control.hasEventHandler("descriptor_write")) {
      control.triggerEvent("descriptor_write", {
        "device_id": deviceId,
        "characteristic_uuid": charKey,
        "descriptor_uuid": descKey,
        "offset": offset,
        "value": incoming,
      });
    }
    return PeripheralWriteRequestResult(
      value: incoming,
      offset: offset,
      status: gattSuccess,
    );
  }

  String _servicesFingerprint(List<BlePeripheralService> services) {
    return jsonEncode(services.map((s) => s.toJson()).toList());
  }

  Future<void> _syncServices() async {
    if (_syncingServices) return;
    final services = parseBlePeripheralServices(control.get("services"));
    final fingerprint = _servicesFingerprint(services);
    if (fingerprint == _lastServicesFingerprint) {
      return;
    }

    _syncingServices = true;
    try {
      final advertisingState =
          await UniversalBlePeripheral.getAdvertisingState();
      final wasAdvertising =
          advertisingState == PeripheralAdvertisingState.advertising ||
              advertisingState == PeripheralAdvertisingState.starting;
      if (wasAdvertising) {
        await UniversalBlePeripheral.stopAdvertising();
      }

      await UniversalBlePeripheral.clearServices();
      for (final service in services) {
        await UniversalBlePeripheral.addService(service);
      }

      _seedCacheFromServices(services, replace: true);
      _lastServicesFingerprint = fingerprint;
      // If we stopped advertising due to a services change, do not auto-restart.
    } catch (e, st) {
      debugPrint("BluetoothPeripheral._syncServices error: $e\n$st");
      if (control.hasEventHandler("error")) {
        control.triggerEvent("error", e.toString());
      }
    } finally {
      _syncingServices = false;
    }
  }

  void _seedCacheFromServices(
    List<BlePeripheralService> services, {
    bool replace = false,
  }) {
    if (replace) {
      _characteristicValues.clear();
      _descriptorValues.clear();
      _writableCharacteristics.clear();
      _writableDescriptors.clear();
    }

    for (final service in services) {
      for (final characteristic in service.characteristics) {
        final charId = BleUuidParser.string(characteristic.uuid);
        if (characteristic.value != null) {
          _characteristicValues[charId] =
              Uint8List.fromList(characteristic.value!);
        } else if (replace) {
          _characteristicValues.putIfAbsent(charId, () => Uint8List(0));
        }

        final writable = characteristic.permissions
                .contains(PeripheralAttributePermission.writeable) ||
            characteristic.properties.contains(CharacteristicProperty.write) ||
            characteristic.properties
                .contains(CharacteristicProperty.writeWithoutResponse);
        if (writable) {
          _writableCharacteristics.add(charId);
        } else if (replace) {
          _writableCharacteristics.remove(charId);
        }

        for (final descriptor in characteristic.descriptors) {
          final descId = BleUuidParser.string(descriptor.uuid);
          final key = descriptorCacheKey(charId, descId);
          if (descriptor.value != null) {
            _descriptorValues[key] = Uint8List.fromList(descriptor.value!);
          } else if (replace) {
            _descriptorValues.putIfAbsent(key, () => Uint8List(0));
          }

          final descWritable = descriptor.permissions
                  ?.contains(PeripheralAttributePermission.writeable) ??
              false;
          if (descWritable) {
            _writableDescriptors.add(key);
          } else if (replace) {
            _writableDescriptors.remove(key);
          }
        }
      }
    }
  }

  List<String> _serviceUuidsFromProp() {
    return parseBlePeripheralServices(control.get("services"))
        .map((s) => s.uuid)
        .toList();
  }

  Future<dynamic> _invokeMethod(String name, dynamic args) async {
    debugPrint("BluetoothPeripheral.$name($args)");
    try {
      switch (name) {
        case "get_capabilities":
          final caps = await UniversalBlePeripheral.getCapabilities();
          return okResult(peripheralCapabilitiesToMap(caps));
        case "get_availability_state":
          final state = await UniversalBlePeripheral.getAvailabilityState();
          return okResult(state.name);
        case "get_advertising_state":
          final state = await UniversalBlePeripheral.getAdvertisingState();
          return okResult(state.name);
        case "start_advertising":
          {
            final serviceUuids =
                (args["service_uuids"] as List?)?.cast<String>() ??
                    _serviceUuidsFromProp();
            await UniversalBlePeripheral.startAdvertising(
              services: serviceUuids,
              localName: args["local_name"] as String?,
              timeout: parseDuration(args["timeout"]),
              manufacturerData:
                  parsePeripheralManufacturerData(args["manufacturer_data"]),
            );
            return okResult();
          }
        case "stop_advertising":
          await UniversalBlePeripheral.stopAdvertising();
          return okResult();
        case "update_characteristic_value":
          {
            final characteristicId =
                args["characteristic_uuid"] as String? ?? "";
            final key = BleUuidParser.string(characteristicId);
            final value = parseBytes(args["value"]);
            _characteristicValues[key] = value;
            await UniversalBlePeripheral.updateCharacteristicValue(
              characteristicId: key,
              value: value,
              deviceId: args["device_id"] as String?,
            );
            return okResult();
          }
        case "get_subscribed_clients":
          {
            final characteristicId =
                args["characteristic_uuid"] as String? ?? "";
            final clients = await UniversalBlePeripheral.getSubscribedClients(
              characteristicId,
            );
            return okResult(clients);
          }
        case "get_maximum_notify_length":
          {
            final deviceId = args["device_id"] as String? ?? "";
            final length =
                await UniversalBlePeripheral.getMaximumNotifyLength(deviceId);
            return okResult(length);
          }
        default:
          throw Exception("Unknown BluetoothPeripheral method: $name");
      }
    } catch (error, stackTrace) {
      debugPrint("BluetoothPeripheral.$name error: $error\n$stackTrace");
      return errorResult(error);
    }
  }

  @override
  void dispose() {
    debugPrint("BluetoothPeripheral(${control.id}).dispose()");
    control.removeInvokeMethodListener(_invokeMethod);

    _advertisingStateSubscription?.cancel();
    _subscriptionSubscription?.cancel();
    _connectionSubscription?.cancel();
    _serviceAddedSubscription?.cancel();
    _mtuSubscription?.cancel();

    if (_ownsHandlers && _activeInstance == this) {
      unawaited(UniversalBlePeripheral.stopAdvertising());
      unawaited(UniversalBlePeripheral.clearServices());
      _clearHandlers();
      _activeInstance = null;
      _ownsHandlers = false;
    }

    _characteristicValues.clear();
    _descriptorValues.clear();
    _writableCharacteristics.clear();
    _writableDescriptors.clear();
    super.dispose();
  }
}
