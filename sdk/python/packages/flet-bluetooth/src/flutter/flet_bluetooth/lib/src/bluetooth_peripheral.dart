import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';

import 'package:flet/flet.dart';
import 'package:flutter/foundation.dart';
import 'package:universal_ble/universal_ble.dart';

import 'utils/bluetooth.dart';
import 'utils/bluetooth_peripheral.dart';

class _UnknownBluetoothPeripheralMethod implements Exception {
  final String name;
  const _UnknownBluetoothPeripheralMethod(this.name);

  @override
  String toString() => "Unknown BluetoothPeripheral method: $name";
}

class BluetoothPeripheralService extends FletService {
  BluetoothPeripheralService({required super.control});

  static BluetoothPeripheralService? _activeInstance;

  final Map<String, Uint8List> _characteristicValues = {};
  final Map<String, Uint8List> _descriptorValues = {};
  final Set<String> _writableCharacteristics = {};
  final Set<String> _writableDescriptors = {};

  String? _lastServicesFingerprint;
  List<String> _cachedServiceUuids = const [];
  bool _syncingServices = false;
  bool _syncPending = false;

  bool? _wantAdvertisingState;
  bool? _wantSubscription;
  bool? _wantConnection;
  bool? _wantServiceAdded;
  bool? _wantMtu;

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
    final wantAdvertising = control.hasEventHandler("advertising_state_change") ||
        control.hasEventHandler("error");
    final wantSubscription = control.hasEventHandler("subscription_change");
    final wantConnection = control.hasEventHandler("connection_change");
    final wantServiceAdded = control.hasEventHandler("service_added");
    final wantMtu = control.hasEventHandler("mtu_change");

    if (_wantAdvertisingState != wantAdvertising) {
      _advertisingStateSubscription?.cancel();
      _advertisingStateSubscription = null;
      if (wantAdvertising) {
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
      _wantAdvertisingState = wantAdvertising;
    }

    if (_wantSubscription != wantSubscription) {
      _subscriptionSubscription?.cancel();
      _subscriptionSubscription = null;
      if (wantSubscription) {
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
      _wantSubscription = wantSubscription;
    }

    if (_wantConnection != wantConnection) {
      _connectionSubscription?.cancel();
      _connectionSubscription = null;
      if (wantConnection) {
        _connectionSubscription =
            UniversalBlePeripheral.connectionStateStream.listen((event) {
          control.triggerEvent("connection_change", {
            "device_id": event.deviceId,
            "connected": event.connected,
          });
        });
      }
      _wantConnection = wantConnection;
    }

    if (_wantServiceAdded != wantServiceAdded) {
      _serviceAddedSubscription?.cancel();
      _serviceAddedSubscription = null;
      if (wantServiceAdded) {
        _serviceAddedSubscription =
            UniversalBlePeripheral.serviceAddedStream.listen((event) {
          control.triggerEvent("service_added", {
            "service_uuid": event.serviceId,
            "error": event.error,
          });
        });
      }
      _wantServiceAdded = wantServiceAdded;
    }

    if (_wantMtu != wantMtu) {
      _mtuSubscription?.cancel();
      _mtuSubscription = null;
      if (wantMtu) {
        _mtuSubscription =
            UniversalBlePeripheral.mtuChangedStream.listen((event) {
          control.triggerEvent("mtu_change", {
            "device_id": event.deviceId,
            "mtu": event.mtu,
          });
        });
      }
      _wantMtu = wantMtu;
    }
  }

  PeripheralReadRequestResult? _onReadRequest(
    String deviceId,
    String characteristicId,
    int offset,
    Uint8List? value,
  ) {
    final key = BleUuidParser.string(characteristicId);
    final sliced = sliceBleValue(_characteristicValues[key], offset);
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
    return _handleWrite(
      cacheKey: key,
      cache: _characteristicValues,
      writable: _writableCharacteristics,
      offset: offset,
      value: value,
      onAccepted: (incoming) {
        if (control.hasEventHandler("characteristic_write")) {
          control.triggerEvent("characteristic_write", {
            "device_id": deviceId,
            "characteristic_uuid": key,
            "offset": offset,
            "value": incoming,
          });
        }
      },
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
    return _handleWrite(
      cacheKey: cacheKey,
      cache: _descriptorValues,
      writable: _writableDescriptors,
      offset: offset,
      value: value,
      onAccepted: (incoming) {
        if (control.hasEventHandler("descriptor_write")) {
          control.triggerEvent("descriptor_write", {
            "device_id": deviceId,
            "characteristic_uuid": charKey,
            "descriptor_uuid": descKey,
            "offset": offset,
            "value": incoming,
          });
        }
      },
    );
  }

  PeripheralWriteRequestResult _handleWrite({
    required String cacheKey,
    required Map<String, Uint8List> cache,
    required Set<String> writable,
    required int offset,
    required Uint8List? value,
    required void Function(Uint8List incoming) onAccepted,
  }) {
    final incoming = value ?? Uint8List(0);

    if (!writable.contains(cacheKey)) {
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
    final next = applyBleWrite(cache[cacheKey], offset, incoming);
    if (next.length > maxGattAttributeLength) {
      return PeripheralWriteRequestResult(
        value: incoming,
        offset: offset,
        status: gattInvalidAttributeLength,
      );
    }

    cache[cacheKey] = next;
    onAccepted(incoming);
    return PeripheralWriteRequestResult(
      value: incoming,
      offset: offset,
      status: gattSuccess,
    );
  }

  Future<void> _syncServices() async {
    if (_syncingServices) {
      _syncPending = true;
      return;
    }

    // Fingerprint the raw control payload before parsing objects.
    final rawServices = control.get("services");
    final fingerprint = jsonEncode(rawServices);
    if (fingerprint == _lastServicesFingerprint) {
      return;
    }

    _syncingServices = true;
    try {
      do {
        _syncPending = false;
        final services = parseBlePeripheralServices(control.get("services"));
        final currentFingerprint = jsonEncode(control.get("services"));

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

        _seedCacheFromServices(services);
        _cachedServiceUuids = services.map((s) => s.uuid).toList();
        _lastServicesFingerprint = currentFingerprint;
        // If we stopped advertising due to a services change, do not auto-restart.
      } while (_syncPending);
    } catch (e, st) {
      debugPrint("BluetoothPeripheral._syncServices error: $e\n$st");
      if (control.hasEventHandler("error")) {
        control.triggerEvent("error", e.toString());
      }
    } finally {
      _syncingServices = false;
    }
  }

  void _seedCacheFromServices(List<BlePeripheralService> services) {
    _characteristicValues.clear();
    _descriptorValues.clear();
    _writableCharacteristics.clear();
    _writableDescriptors.clear();

    for (final service in services) {
      for (final characteristic in service.characteristics) {
        final charId = BleUuidParser.string(characteristic.uuid);
        _characteristicValues[charId] = characteristic.value != null
            ? Uint8List.fromList(characteristic.value!)
            : Uint8List(0);

        final writable = characteristic.permissions
                .contains(PeripheralAttributePermission.writeable) ||
            characteristic.properties.contains(CharacteristicProperty.write) ||
            characteristic.properties
                .contains(CharacteristicProperty.writeWithoutResponse);
        if (writable) {
          _writableCharacteristics.add(charId);
        }

        for (final descriptor in characteristic.descriptors) {
          final descId = BleUuidParser.string(descriptor.uuid);
          final key = descriptorCacheKey(charId, descId);
          _descriptorValues[key] = descriptor.value != null
              ? Uint8List.fromList(descriptor.value!)
              : Uint8List(0);

          final descWritable = descriptor.permissions
                  ?.contains(PeripheralAttributePermission.writeable) ??
              false;
          if (descWritable) {
            _writableDescriptors.add(key);
          }
        }
      }
    }
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
                    (_cachedServiceUuids.isNotEmpty
                        ? _cachedServiceUuids
                        : parseBlePeripheralServices(control.get("services"))
                            .map((s) => s.uuid)
                            .toList());
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
          throw _UnknownBluetoothPeripheralMethod(name);
      }
    } on _UnknownBluetoothPeripheralMethod {
      rethrow;
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

    if (_activeInstance == this) {
      unawaited(UniversalBlePeripheral.stopAdvertising());
      unawaited(UniversalBlePeripheral.clearServices());
      _clearHandlers();
      _activeInstance = null;
    }

    _characteristicValues.clear();
    _descriptorValues.clear();
    _writableCharacteristics.clear();
    _writableDescriptors.clear();
    super.dispose();
  }
}
