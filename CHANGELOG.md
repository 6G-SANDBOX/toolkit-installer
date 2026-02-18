# Changelog

## [v1.5.0] - 2026-02-16

### Added

- Support for OpenNebula 7.0.x.
- Smart auto-fill for template_id and image_id variables from marketplace appliances.
- VM ID-based functions to prevent naming conflicts with multiple instances.
- Unique naming for instantiated services.
- Function index and section headers to OpenNebula CLI wrapper.
- Component selection prompt readability improvements.

### Changed

- site_routemanager is now optional.
- Enhanced user input handling for list values in site YAML.

### Fixed

- Handle empty VM/service list in onemarketapp_instantiate.
- Multi-instance support with ID-based lookups in installer.
- Unpack 4 return values from onemarketapp_instantiate.

## [v1.0.0] - 2025-09-11

### Added

- Initial stable release of the toolkit installer.

## [v0.5.1] - 2025-04-10

### Fixed

- Script installer select correct toolkit installer version.
- Point to new 6G-Library release.

## [v0.5.0] - 2025-03-31

### Added

- Toolkit also works as updater as well.
- Validate if the Official OpenNebula Marketplace is installed. [#11](https://github.com/6G-SANDBOX/toolkit-installer/issues/11)
- Ask DNS. [#15](https://github.com/6G-SANDBOX/toolkit-installer/issues/15)
- Ask route-manager-api. [#17](https://github.com/6G-SANDBOX/toolkit-installer/issues/17)
- Possibility to select the host to deploy the TNLCM vm on. [#20](https://github.com/6G-SANDBOX/toolkit-installer/issues/20)
- Versioning appliances for install and upgrade.

### Changed

- Update _extract_appliance_name to handle multiple appliance url. [#18](https://github.com/6G-SANDBOX/toolkit-installer/issues/18)
- Migrate OneKE 1.29 to 1.31. [#19](https://github.com/6G-SANDBOX/toolkit-installer/issues/19)

## [v0.4.0] - 2025-02-22

### Added

- First toolkit version.

[v1.5.0]: https://github.com/6G-SANDBOX/toolkit-installer/compare/v1.0.0...v1.5.0
[v1.0.0]: https://github.com/6G-SANDBOX/toolkit-installer/compare/v0.5.1...v1.0.0
[v0.5.1]: https://github.com/6G-SANDBOX/toolkit-installer/compare/v0.5.0...v0.5.1
[v0.5.0]: https://github.com/6G-SANDBOX/toolkit-installer/compare/v0.4.0...v0.5.0
[v0.4.0]: https://github.com/6G-SANDBOX/toolkit-installer/releases/tag/v0.4.0
