---
class_name: "flet_bluetooth.Bluetooth"
examples: "extensions/bluetooth"
title: "Bluetooth"
---

import {ClassMembers, ClassSummary, CodeExample} from '@site/src/components/crocodocs';

<ClassSummary name={frontMatter.class_name} />

A service for Bluetooth Low Energy (BLE) **central / client** operations: adapter
state, permissions, scanning, connecting, and GATT read / write / notify.

Add an instance to [`Page.services`][flet.Page.services] before calling methods.
See the [Bluetooth overview](index.md) for install instructions, platform support,
and permission setup.

## Example

<CodeExample path={frontMatter.examples + '/scanner/main.py'} language="python" />

<ClassMembers name={frontMatter.class_name} />
