# waggle.protocol

This package provides functionality for packing and unpacking the various
protocols used by the Waggle platform.

## Core Data Types

The Waggle platform implements a variety of data types, each used for a specific
layer of the message pipeline. The typical data flow looks like:

1. Plugin publishes **sensorgrams**.
2. Node bundles **sensorgrams** and plugin info into **datagram**.
3. Node bundles **datagrams** with sender and receiver info into **waggle message**.

The result waggle message, depicted visually, would be organized like:

```
+-------------------------+
| waggle message          |
| sender-info: node123    |
| receiver-info: beehive  |
| datagrams:              |
| +---------------------+ |
| | datagram 1          | |
| | plugin-info: sysmon | |
| | sensorgrams:        | |
| | +---------------+   | |
| | | measurement 1 |   | |
| | | measurement 2 |   | |
| | | ...           |   | |
| | | measurement n |   | |
| | +---------------+   | |
| +---------------------+ |
| ...more datagrams...    |
+-------------------------+
```

### Sensorgram

### Datagram

### Waggle Message

## Protocol API

The protocol API provides a few code
