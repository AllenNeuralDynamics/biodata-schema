# biodata-schema v3.0.0 Migration Guide

v3.0.0 removes every field, class, method, and back-compatibility shim that was marked
deprecated in v2.x. All of them used to emit a `DeprecationWarning` (or carried Pydantic's
`deprecated=`) but still validated. They are now gone, and passing them raises a Pydantic
`ValidationError` (`extra_forbidden`), since all schema models forbid extra fields.

There is no automatic upgrade path for stored JSON. Files written under v2.x that use the
removed fields must be rewritten before they will validate against v3.0.0.

## Contents

1. [`coordinate_system` renamed to `global_`/`local_coordinate_system`](#1-coordinate_system-renamed)
2. [`Section` coordinate fields moved to `PlanarSection`](#2-section-coordinate-fields)
3. [Device fields replaced by `shape`](#3-device-size-fields-replaced-by-shape)
4. [`DAQChannel.channel_index`](#4-daqchannelchannel_index)
5. [`BreedingInfo.breeding_group`](#5-breedinginfobreeding_group)
6. [Olfactory stimulus classes](#6-olfactory-stimulus-classes)
7. [`DataDescription.from_*` classmethods](#7-datadescriptionfrom_-classmethods)
8. [`QCMetric.tags` list form](#8-qcmetrictags-list-form)
9. [`CoordinateSystemLibrary` removed](#9-coordinatesystemlibrary-removed)
10. [Removed helper](#10-removed-helper)
11. [Warnings promoted to errors](#11-warnings-promoted-to-errors)
12. [Validators still emitting warnings](#12-validators-still-emitting-warnings)

---

## 1. `coordinate_system` renamed

v2.x split `coordinate_system` into `global_coordinate_system` on top-level and container
models, and `local_coordinate_system` on device and config models. The old field stayed
alongside the new one, and a `model_validator(mode="before")` copied the old value forward
with a `DeprecationWarning`.

The old field and the copy-forward validators are both removed.

### Renamed to `global_coordinate_system`

| Model | Module |
| --- | --- |
| `Acquisition` | `core/acquisition.py` |
| `Procedures` | `core/procedures.py` |
| `Instrument` | `core/instrument.py` |
| `Surgery` | `components/subject_procedures.py` |
| `PlanarSectioning` | `components/specimen_procedures.py` |

### Renamed to `local_coordinate_system`

| Model | Module |
| --- | --- |
| `DevicePosition` (and every subclass, e.g. `Monitor`) | `components/devices.py` |
| `ImagingConfig` | `components/configs.py` |
| `LickSpoutConfig` | `components/configs.py` |
| `AirPuffConfig` | `components/configs.py` |
| `ManipulatorConfig` | `components/configs.py` |
| `ProbeConfig` | `components/configs.py` |

**Before**

```python
Acquisition(..., coordinate_system=CoordinateSystemLibrary.BREGMA_ARI)
ProbeConfig(..., coordinate_system=CoordinateSystemLibrary.BREGMA_ARI)
```

**After**

```python
Acquisition(..., global_coordinate_system=CoordinateSystemLibrary.BREGMA_ARI)
ProbeConfig(..., local_coordinate_system=CoordinateSystemLibrary.BREGMA_ARI)
```

> Not affected: `AtlasCoordinate.coordinate_system` is a different field that holds an
> `Atlas`. Do not rename it.

`Instrument.global_coordinate_system` and the `local_coordinate_system` fields on
`ManipulatorConfig` and `ProbeConfig` are required. If you relied on the old field being
copied forward, set the new field explicitly.

## 2. `Section` coordinate fields

`Section` had six coordinate fields that duplicated `PlanarSection`. They are removed from
`Section`. Use `PlanarSection` for any section with coordinate data.

Removed from `Section` (`components/specimen_procedures.py`):

- `coordinate_system_name`
- `start_coordinate`
- `end_coordinate`
- `thickness`
- `thickness_unit`
- `partial_slice`

The `deprecated_coordinate_fields` validator that warned on these is also removed.

**Before**

```python
Section(output_specimen_id="123456_001", coordinate_system_name="BREGMA_ARI", thickness=0.1)
```

**After**

```python
PlanarSection(
    output_specimen_id="123456_001",
    coordinate_system_name="BREGMA_ARI",
    start_coordinate=Translation(translation=[0.3, 0, 0]),
    thickness=0.1,
)
```

`PlanarSection` requires `coordinate_system_name` and `start_coordinate`.

## 3. Device size fields replaced by `shape`

`Enclosure` and `Arena` (`components/devices.py`) used a `Scale`-based `size`/`size_unit`
pair. Use a geometry object instead.

| Model | Removed | Replacement |
| --- | --- | --- |
| `Enclosure` | `size`, `size_unit` | `shape: Rectangle \| Circle` |
| `Arena` | `size`, `size_unit` | `shape: Circle \| Rectangle` |

`shape` is now required on both models. It was optional with a `None` default in v2.x, but
`size` was required and was the only way to record extent, so every `Enclosure` and `Arena`
must now set `shape`.

**Before**

```python
Arena(..., size=Scale(scale=[30, 30, 20]), size_unit=SizeUnit.CM)
```

**After**

```python
Arena(..., shape=Rectangle(width=30, height=30, size_unit=SizeUnit.CM))
```

> Other `size_unit` fields in the schema (`Monitor`, `Rectangle`, `Wheel`, and so on) were
> never deprecated and are unchanged.

## 4. `DAQChannel.channel_index`

`DAQChannel.channel_index` (`components/devices.py`) and its `deprecated_channel_index`
validator are removed. Use `DAQChannel.port`.

**Before**

```python
DAQChannel(channel_name="ch", channel_type=DaqChannelType.DI, channel_index=1)
```

**After**

```python
DAQChannel(channel_name="ch", channel_type=DaqChannelType.DI, port=1)
```

> Not affected: `OlfactometerChannel.channel_index` and
> `OlfactometerChannelInfo.channel_index` are unrelated fields and were never deprecated.

## 5. `BreedingInfo.breeding_group`

`BreedingInfo.breeding_group` (`components/subjects.py`) is removed, along with the
`warn_breeding_group_deprecated` validator that warned on the value and then cleared it.

v2.x already discarded the value, so nothing is lost. Drop the argument.

## 6. Olfactory stimulus classes

Two classes are removed from `components/stimulus.py`:

| Removed | Replacement |
| --- | --- |
| `OlfactometerChannelConfig` | `OlfactometerChannelInfo` in `components/configs.py` |
| `OlfactoryStimulation` | `StimulusEpoch.stimulus_name` plus `OlfactometerConfig` in `components/configs.py` |

`OlfactoryStimulation.channels` and `OlfactoryStimulation.notes` were separately deprecated
and go away with the class.

## 7. `DataDescription.from_*` classmethods

The three derivation classmethods on `DataDescription` (`core/data_description.py`) are
removed. Use the functions in `aind_data_schema.utils.inheritance` that they already called.

| Removed | Replacement |
| --- | --- |
| `DataDescription.from_raw(...)` | `derive_data_description_from_raw(...)` |
| `DataDescription.from_derived(...)` | `derive_data_description_from_derived(...)` |
| `DataDescription.from_data_description(...)` | `derive_data_description(...)` |

The signatures are the same, so this is an import and a rename:

```python
from aind_data_schema.utils.inheritance import (
    derive_data_description,
    derive_data_description_from_derived,
    derive_data_description_from_raw,
)

derived = derive_data_description_from_raw(dd, "spikesort-ks25", creation_time=dt)
```

## 8. `QCMetric.tags` list form

`QCMetric.tags` became a `dict` in v2.3. The `fix_tag_lists` validator
(`core/quality_control.py`) accepted the v2.2.x list form and converted it to
`{"tag_1": ..., "tag_2": ...}` with a `DeprecationWarning`. That validator is removed, so
list-valued `tags` now fail validation.

**Before (v2.2.x JSON)**

```json
{"tags": ["Probe A", "Drift"]}
```

**After**

```json
{"tags": {"probe": "Probe A", "issue": "Drift"}}
```

Pick whatever keys you want. The old shim used positional `tag_1`, `tag_2` keys, so
`{"tag_1": "Probe A", "tag_2": "Drift"}` gives you the same result as v2.x if you want a
mechanical rewrite.

### Related removal: `fix_default_grouping_list`

`QualityControl.fix_default_grouping_list` turned a v2.2.x string-list `default_grouping`
into `[["modality"], ["tag_1"]]`. It only ran when the first metric had list-valued `tags`,
so removing `fix_tag_lists` left it unreachable and it is removed too. Pass
`default_grouping` in the current form, a list of tuples of strings.

## 9. `CoordinateSystemLibrary` removed

`aind_data_schema.components.coordinates.CoordinateSystemLibrary` is removed. It held a
fixed set of named `CoordinateSystem` constants (`BREGMA_ARI`, `BREGMA_RAS`, `BREGMA_ARID`,
`BREGMA_RASD`, `ARENA_RBT`, `SIPE_CAMERA_RBF`, `SIPE_MONITOR_RTF`, `SIPE_SPEAKER_LTF`,
`MPM_MANIP_RFB`, `PINPOINT_PROBE_RSAB`, `SPIM_RPI`, `SPIM_IJK`, `MRI_LPS`, `IMAGE_XYZ`, and
others).

Coordinate systems belong to a rig or a project, not to the schema. Define the ones your
project uses in your own module and import them where you need them.

`CoordinateSystem`, `Axis`, `Origin`, `AxisName`, and `Direction` are unchanged. Only the
library of pre-built constants is gone.

**Before**

```python
from aind_data_schema.components.coordinates import CoordinateSystemLibrary

Acquisition(..., global_coordinate_system=CoordinateSystemLibrary.BREGMA_ARI)
```

**After**

```python
from aind_data_schema_models.coordinates import AxisName, Direction, Origin
from aind_data_schema_models.units import SizeUnit

from aind_data_schema.components.coordinates import Axis, CoordinateSystem

BREGMA_ARI = CoordinateSystem(
    name="BREGMA_ARI",
    origin=Origin.BREGMA,
    axis_unit=SizeUnit.MM,
    axes=[
        Axis(name=AxisName.AP, direction=Direction.PA),
        Axis(name=AxisName.ML, direction=Direction.LR),
        Axis(name=AxisName.SI, direction=Direction.SI),
    ],
)

Acquisition(..., global_coordinate_system=BREGMA_ARI)
```

To copy an old definition verbatim, look at `components/coordinates.py` at the v2.9.0 tag.
Every example under `examples/` now defines its coordinate system inline and can be used as
a template.

> `AtlasLibrary` is a separate library and still ships with the package.

## 10. Removed helper

`aind_data_schema.base.migrate_deprecated_coordinate_system` is removed. It only existed to
do the copy-forward described in section 1 and has no replacement. `recursive_get_all_names`
in `utils/validators.py` no longer skips the old `coordinate_system` field and is simpler
as a result.

### The `transforms` extra is gone

`pip install biodata-schema[transforms]` is no longer valid. The optional-dependency group
and its `scipy` requirement are both removed. The extra was only there for
`Rotation.to_matrix`, which no longer ships. Drop `[transforms]` from your install command;
plain `pip install biodata-schema` covers everything.

## 11. Warnings promoted to errors

Six things that only warned in v2.x now fail validation. These reject files that used to be
accepted, so they are the most likely source of new `ValidationError`s.

### `Code` requires `commit_hash` or `version`

`Code._ensure_commit_hash_or_version` (`components/identifiers.py`) used to warn that at
least one of these fields would be required in a future release. It is required now.

```python
Code(url="https://github.com/AllenNeuralDynamics/example")  # ValidationError
Code(url="https://github.com/AllenNeuralDynamics/example", version="0.0.1")  # ok
```

### Bare `Injection` procedures are rejected

`Procedures.reject_injections` (`core/procedures.py`) now raises. Wrap every `Injection` in
a `Surgery` or `NonSurgicalInjection`:

```python
Procedures(subject_id="12345", subject_procedures=[Injection(...)])  # ValidationError
Procedures(subject_id="12345", subject_procedures=[Surgery(procedures=[Injection(...)])])  # ok
```

### Duplicate component names on `Instrument`

`Instrument.validate_unique_component_names` (`core/instrument.py`) now raises instead of
logging. Two cases are rejected:

- two entries in `Instrument.components` with the same `name`, and
- two different objects anywhere in the component tree with the same `name`.

Referencing one shared object from more than one place is fine. Objects are compared by
value before a name is reported as a duplicate.

`Software` names are skipped entirely. Software is a descriptor, not an addressable device,
and the same package is often recorded across many devices. Setting
`Software(name="Bonsai", version="2.5")` as the `recording_software` on every camera is
valid, and so is giving a `Software` the same name as a device.

This matters because `Connection.source_device` and `Connection.target_device` look up
components by name.

#### Renamed devices in `multiplane_ophys_instrument`

`examples/multiplane_ophys_instrument.py` failed this check. Three `CameraAssembly` objects
each held a `Camera` with the assembly's exact name, and `Connection.source_device` pointed
at that name, so the reference was ambiguous. The inner cameras were renamed to match the
`"… Camera Lens"` and `"… Camera Filter"` naming already used in that file:

| Old name (assembly and camera) | Assembly keeps | Inner camera becomes |
| --- | --- | --- |
| `Behavior Camera` | `Behavior Camera` | `Behavior Camera Detector` |
| `Eye Camera` | `Eye Camera` | `Eye Camera Detector` |
| `Face Camera` | `Face Camera` | `Face Camera Detector` |

Do the same if you copied names from that example, or if your instrument gives an assembly
and its inner camera the same name: keep the assembly name, since connections point at it,
and rename the inner device.

### Absolute `AssetPath` values

`recursive_check_paths` (`utils/validators.py`) now raises on an absolute `AssetPath`
instead of logging. It runs from `DataCoreModel.write_standard_file`, so writing a file with
absolute asset paths now fails. Paths must be relative to the metadata directory.

A path that does not exist still only logs a warning, because whether a relative path
resolves depends on the working directory.

### `Monitor.contrast_unit` and `brightness_unit` are no longer filled in

`Monitor.add_units_if_needed` (`components/devices.py`) set these units to `percent` when a
value was given without one. It is removed. A separate validator already required the unit
whenever the value is set, and that requirement now takes effect:

```python
Monitor(..., contrast=50)  # ValidationError
Monitor(..., contrast=50, contrast_unit=UnitlessUnit.PERCENT)  # ok
```

### `Metadata` no longer adds the `calibration` tag for you

`Metadata.validate_calibration_object_tags` (`core/metadata.py`) still warns when a
`CalibrationObject` subject has no `"calibration"` tag, but it no longer appends the tag to
`data_description.tags`. Add it yourself:

```python
DataDescription(..., tags=["calibration"])
```

## 12. Validators still emitting warnings

There are no `DeprecationWarning`s left in the package. These are the warnings that remain
after the changes in section 11, and they stay warnings on purpose.

### `UserWarning`, visible through `warnings` and `pytest.warns`

| Location | Validator | Fires when | Why it stays a warning |
| --- | --- | --- | --- |
| `core/metadata.py` | `Metadata.validate_expected_files_by_modality` | A file required by the declared modality is missing | Metadata is built up in pieces, so an error would block partial objects |
| `core/metadata.py` | `Metadata.validate_calibration_object_tags` | `CalibrationObject` subject with no `"calibration"` tag | Advisory only; see section 11 for the dropped auto-fix |
| `core/metadata.py` | `Metadata.validate_training_protocol_references` | `StimulusEpoch.training_protocol_name` has no match in `Procedures` | Only meaningful when both files are present |
| `core/metadata.py` | `Metadata.validate_data_description_name_time_consistency` | Creation time from the name is far from `acquisition_end_time` | "Close to" is a heuristic, not a rule |
| `core/processing.py` | `Processing.__add__` | Merged objects share process names | The merge already fixes it by renaming |
| `base.py` | `_GenericModel.validate_fieldnames` | A field name contains `.` or `$` | Fires on user-supplied `GenericModel` payloads the schema does not control |

### `logger.warning`, log output only

| Location | Validator | Fires when | Why it stays a warning |
| --- | --- | --- | --- |
| `core/metadata.py` | `Metadata.validate_core_fields` | A core field failed its own validation | This is the escape hatch for wrapping partially-invalid cores |
| `core/acquisition.py` | `DataStream.__add__` | Two merged data streams disagree | Part of the merge helper, not a validator |
| `utils/validators.py` | `recursive_check_paths` | An `AssetPath` does not exist on disk | Whether it resolves depends on the working directory |
| `base.py` | `DataCoreModel.write_standard_file` | Serialized file is over the 500 KB `MAX_FILE_SIZE` | Advisory on a write path; failing would throw away your data |

### Note on `DEPTH` axes

v2.x warned when a `CoordinateSystem` used a `DEPTH` axis. That warning is gone and `DEPTH`
axes are now accepted without complaint, for compatibility with existing coordinate systems.
Removing `CoordinateSystemLibrary` (section 9) is the other half of this: the package no
longer ships a `DEPTH`-based system, so projects defining their own will not pick one up by
accident.

## Verifying your upgrade

The full test suite and all bundled examples were updated for these changes and pass under
v3.0.0:

```bash
uv run pytest
```
