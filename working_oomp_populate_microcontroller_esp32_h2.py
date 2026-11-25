"""ESP32_H2 board definitions. Edit these verbose dictionaries directly."""


def main(**kwargs):
    options = []

    # Tenstar ESP32-H2 SuperMini (pinout unverified)
    option = {
        'type_1': "microcontroller",
        'type_2': "esp32_h2",
        'type_3': "supermini_18_pin",
        'breakout_description': "18_mm_width_23_5_mm_height_18_pins",
        'manufacturer': "tenstar",
        'part_number': "esp32_h2_supermini",
        'breakout_pcb_width': 18,
        'breakout_pcb_height': 23.5,
        'schema_version': 1,
        'item_kind': "breakout",
        'name_readable': "Tenstar ESP32-H2 SuperMini (pinout unverified)",
        'taxonomy_1': "electronic",
        'taxonomy_2': "breakout",
        'taxonomy_3': "microcontroller",
        'taxonomy_4': "esp32_h2",
        'taxonomy_5': "supermini_18_pin",
        'taxonomy_6': "18_mm_width_23_5_mm_height_18_pins",
        'taxonomy_7': "",
        'taxonomy_8': "",
        'taxonomy_9': "",
        'taxonomy_10': "",
        'taxonomy_11': "",
        'taxonomy_12': "",
        'taxonomy_13': "",
        'taxonomy_14': "tenstar",
        'taxonomy_15': "esp32_h2_supermini",
        'form_factor': "supermini_18_pin",
        'chip': {
            'family': "esp32_h2",
            'part_number': "esp32_h2",
            'identity_scope': "catalogue_chip_or_module_label",
            'oomp_id': None,
            'silicon_revision': None,
        },
        'dimensions_mm': {
            'width': 18,
            'height': 23.5,
            'pcb_thickness': None,
            'assembled_height': None,
            'scope': "nominal_catalogue_outline_not_measured",
            'source_id': "original_catalogue",
            'status': "unverified",
        },
        'coordinate_system': {
            'units': "mm",
            'origin': "centre_of_pcb_outline",
            'view': "top_with_usb_at_positive_y",
            'x_positive': "right",
            'y_positive': "towards_usb",
        },
        'assembly': {
            'headers': "unspecified",
            'header_pitch_mm': None,
        },
        'electrical': {
            'logic_voltage_v': 3.3,
            'gpio_5v_tolerant': False,
            'usb_connector': None,
            'source_id': "chip_datasheet",
        },
        'memory': {
            'external_flash_bytes': None,
            'psram_bytes': None,
        },
        'mounting_holes': [],
        'mounting_hole_details': [],
        'mounting_hole_candidates': [],
        'mounting_hole_status': "not_verified",
        'pins': {},
        'connectors': {},
        'onboard_gpio_connections': [],
        'sources': [
            {
                'id': "original_catalogue",
                'url': None,
                'title': "Original populate entries in this repository",
                'local_file': None,
                'scope': "Nominal dimensions and identity; not manufacturer verification",
                'accessed': "2026-10-22",
            },
            {
                'id': "chip_datasheet",
                'url': "https://www.espressif.com/sites/default/files/documentation/esp32-h2_datasheet_en.pdf",
                'title': "chip_datasheet",
                'accessed': "2026-10-22",
                'scope': "GPIO capabilities, electrical limits and strapping; not carrier geometry",
            },
            {
                'id': "board_guide",
                'url': "https://docs.zephyrproject.org/latest/boards/others/esp32h2_supermini/doc/index.html",
                'title': "board_guide",
                'accessed': "2026-10-22",
                'scope': "Primary Zephyr target documentation; does not establish Tenstar header geometry",
            },
        ],
        'notes': [],
        'data_gaps': [
            "Assembled component keepouts and USB insertion/cable envelopes have not been captured.",
            "No revision-specific primary Tenstar header drawing was established. Header GPIO assignments, pad centres and hole locations remain unknown; related SuperMini variants are not substituted.",
        ],
        'pinout_scope': "Expansion connectors and explicitly listed test pads; USB socket contacts excluded.",
        'chip_resources': {
            'cpu_core_count': 1,
            'clock_max_mhz': 96,
            'pwm_channels': 6,
            'hardware_i2c_controllers': 2,
            'general_purpose_spi_controllers': 1,
            'hardware_uart_controllers': 2,
            'pio_state_machines': 0,
            'scope': "silicon resources; board routing and firmware may reduce availability",
            'source_id': "chip_datasheet",
        },
        'lab_support': {
            'status': "catalogue_reference_only",
            'automatic_firmware_enable': False,
            'requires_reviewed_board_profile': True,
            'gpio_matrix_routing': True,
        },
        'pinout_status': "not_established",
        'svg_details': {
            'svg_name': "microcontroller",
            'stylesheet': "microcontroller",
            'width': 18,
            'height': 23.5,
        },
        'gpio_summary': {
            'exposed': [],
            'general_io_candidates': [],
            'analog_candidates': [],
            'automatic_firmware_enable': False,
        },
        'default_interfaces': {
            'uart': {
                'protocol': "uart",
                'status': "unverified",
                'basis': "unknown",
                'framework': None,
                'variant': None,
                'variant_scope': "unverified_carrier",
                'api': None,
                'peripheral': None,
                'source_ids': [],
                'tx_gpio': None,
                'rx_gpio': None,
                'pin_keys': {
                    'tx': [],
                    'rx': [],
                },
                'signal_status': {
                    'tx': "unverified",
                    'rx': "unverified",
                },
                'notes': [
                    "Revision-specific carrier pinout is unverified. Do not substitute a similarly named board or generic SoC default.",
                ],
            },
            'i2c': {
                'protocol': "i2c",
                'status': "unverified",
                'basis': "unknown",
                'framework': None,
                'variant': None,
                'variant_scope': "unverified_carrier",
                'api': None,
                'peripheral': None,
                'source_ids': [],
                'sda_gpio': None,
                'scl_gpio': None,
                'pin_keys': {
                    'sda': [],
                    'scl': [],
                },
                'signal_status': {
                    'sda': "unverified",
                    'scl': "unverified",
                },
                'notes': [
                    "Revision-specific carrier pinout is unverified. Do not substitute a similarly named board or generic SoC default.",
                ],
            },
            'spi': {
                'protocol': "spi",
                'status': "unverified",
                'basis': "unknown",
                'framework': None,
                'variant': None,
                'variant_scope': "unverified_carrier",
                'api': None,
                'peripheral': None,
                'source_ids': [],
                'sck_gpio': None,
                'mosi_gpio': None,
                'miso_gpio': None,
                'ss_gpio': None,
                'pin_keys': {
                    'sck': [],
                    'mosi': [],
                    'miso': [],
                    'ss': [],
                },
                'signal_status': {
                    'sck': "unverified",
                    'mosi': "unverified",
                    'miso': "unverified",
                    'ss': "unverified",
                },
                'notes': [
                    "Revision-specific carrier pinout is unverified. Do not substitute a similarly named board or generic SoC default.",
                ],
            },
        },
        'interface_defaults_version': 1,
    }
    options.append(option)

    return options


def get_chips(**kwargs):
    options = []

    return options
