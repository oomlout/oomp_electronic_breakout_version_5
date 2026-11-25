# I2C peripheral breakout catalogue

The editable authority is [working_oomp_populate_i2c.py](working_oomp_populate_i2c.py).
It contains 29 explicit board dictionaries: 28 I2C-capable SparkFun/Adafruit
carriers and the analog-only Adafruit ADXL335. AliExpress candidates remain in
the [research proposal](research/i2c_breakouts/proposal_2026_10_23.md), outside
the generated catalogue.

Generate the source records and then their parts records:

```powershell
python working_oomp_populate_i2c.py --parts
```

Without `--parts`, the same command writes only `parts_source/<id>/working.yaml`.
The script resolves its own repository root, so it also works when invoked by
absolute path from another directory. It uses the existing shared
`oomp_populate_helper.write_extras` and `working_oomp` generation path. The latter
accepts an exact `part_ids` selection, so this command reads/writes only these
29 boards and propagates part-generation errors before returning.

The normal `working_oomp_populate.main()` also includes these boards. Their fixed
taxonomy is preserved alongside the microcontroller catalogue:

| Slots | Meaning |
| --- | --- |
| 1–2 | `electronic / breakout` |
| 3–6 | Function, group, role, device family; an unknown family stays empty |
| 7 | Carrier/assembly variant |
| 8 | Nominal PCB dimensions, only when explicitly sourced |
| 9–13 | Reserved, empty |
| 14 | Board manufacturer (`sparkfun` or `adafruit`) |
| 15 | Manufacturer product number, normalized for the identifier |

Original vendor SKUs, product links, research date, features and available
address evidence are kept in each record. I2C addresses are integer **seven-bit**
values. `documented_addresses_7bit` contains only addresses transcribed from
reviewed product pages and need not be exhaustive. A null default is unknown,
not address zero. The ADXL335 has `interfaces: [analog]` and `i2c: null`.

This is a product-reference import. Five records have manufacturer nominal PCB
dimensions; other carrier outlines remain null. Separately stated
`product_dimensions_mm` are not treated as PCB outlines. Physical connector/pad
maps, located mounting holes and full electrical/assembly envelopes are not yet
imported. Every record exposes these gaps and has `geometry_ready: false` and
`oobb_details: []`. Thus ordinary catalogue generation creates usable searchable
records without scheduling unverified mounting plates or pinout drawings.

Validate coverage, taxonomy preservation and repeatable source-to-parts output:

```powershell
python -m unittest discover -s tests -p test_i2c_breakouts.py -v
```

Per-board evidence collection has a separate project agent,
[i2c-part-researcher.toml](.codex/agents/i2c-part-researcher.toml), with a detailed
[workflow](research/i2c_breakouts/AGENT_WORKFLOW.md),
[research schema](research/i2c_breakouts/RESEARCH_SCHEMA.md) and
[handoff prompt](research/i2c_breakouts/HANDOFF.md). It inherits the model selected
when launched. Research is stored in `source_file/<exact_part_id>/working.yaml`
beside archived website HTML/text/links, datasheets and other evidence.

Two primary-agent pilots are complete with documented gaps: Adafruit ADXL345
1231 and SparkFun BME280 SEN-15440. The [queue](research/i2c_breakouts/research_queue.yaml)
has 26 remaining I2C boards. The research preserves the original catalogue
taxonomy and does not itself import geometry into `parts_source` or `parts`.

```powershell
python tools/i2c_part_research.py queue
python tools/i2c_part_research.py validate
python -m unittest discover -s tests -p test_i2c_research.py -v
```
