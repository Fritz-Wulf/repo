# Architecture

Fritz.Wulf separates four concerns: shared runtime, device profiles, architecture/ABI-specific packages, and firmware integration. The runtime may live under `/usb/fritzwulf` when the device profile verifies USB availability and boot ordering.

Package installation and runtime updates never imply a firmware flash. Firmware builds, firmware flashing, theme updates, and package updates are distinct operations with independent rollback paths.
