"""Editable SparkFun/Adafruit peripheral board records researched 2026-10-23.

main() returns definitions for the normal population pipeline. Running this file
with --parts writes its parts_source records, then generates only those parts.
The ADXL335 is intentionally analog; it is the one non-I2C addition requested
alongside the classic accelerometers. AliExpress candidates are not included.

Product-page evidence establishes identity and features, not a manufacturing
pinout. Unknown PCB outlines, contacts and holes are explicit. No mounting-plate
or pinout-drawing jobs are scheduled from incomplete geometry.
"""

import argparse
import contextlib
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parent
RESEARCH_DATE = "2026-10-23"
TAXONOMY_SCHEMA = "breakout_function_v1"


def main(**kwargs):
    options = []

    # SparkFun BME280 Atmospheric Sensor, Qwiic
    option = {
        'name_readable': 'SparkFun BME280 Atmospheric Sensor, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_15440',
        'manufacturer_part_number': 'SEN-15440',
        'type_1': 'sensor',
        'type_2': 'environmental',
        'type_3': 'temperature_humidity_pressure',
        'type_4': 'bme280',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-atmospheric-sensor-breakout-bme280-qwiic.html',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A useful combined weather and environmental sensor. The board supports I2C and SPI.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 119,
            'documented_addresses_7bit': [118, 119],
            'address_selection': 'board_configuration',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit SHT45, STEMMA QT
    option = {
        'name_readable': 'Adafruit SHT45, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '5665',
        'manufacturer_part_number': '5665',
        'type_1': 'sensor',
        'type_2': 'environmental',
        'type_3': 'temperature_humidity',
        'type_4': 'sht45',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/5665',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A dedicated temperature/humidity option with better specified accuracy for those measurements.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 68,
            'documented_addresses_7bit': [68],
            'address_selection': 'not_recorded',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 25.5,
            'height': 17.7,
            'depth': 4.8,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # SparkFun BMI270 6DoF IMU, Qwiic
    option = {
        'name_readable': 'SparkFun BMI270 6DoF IMU, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_22397',
        'manufacturer_part_number': 'SEN-22397',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'imu_6_axis',
        'type_4': 'bmi270',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-6dof-imu-breakout-bmi270-qwiic.html',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A modern accelerometer/gyroscope board for motion, orientation experiments and robotics.',
        'dimensions_mm': {
            'width': 25.4,
            'height': 25.4,
            'status': 'manufacturer_nominal',
            'scope': 'nominal_pcb_outline',
            'source_id': 'product',
        },
        'i2c': {
            'default_address_7bit': 104,
            'documented_addresses_7bit': [104, 105],
            'address_selection': 'solder_jumper',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # SparkFun VEML6030 Ambient Light Sensor, Qwiic
    option = {
        'name_readable': 'SparkFun VEML6030 Ambient Light Sensor, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_15436',
        'manufacturer_part_number': 'SEN-15436',
        'type_1': 'sensor',
        'type_2': 'optical',
        'type_3': 'ambient_light',
        'type_4': 'veml6030',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-ambient-light-sensor-veml6030-qwiic.html',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A simple, inexpensive light measurement board.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 72,
            'documented_addresses_7bit': [72],
            'address_selection': 'configurable_alternate_not_recorded',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit VL53L1X, STEMMA QT
    option = {
        'name_readable': 'Adafruit VL53L1X, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '3967',
        'manufacturer_part_number': '3967',
        'type_1': 'sensor',
        'type_2': 'distance',
        'type_3': 'time_of_flight',
        'type_4': 'vl53l1x',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/3967',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'General distance sensing, with a vendor-specified range up to roughly four metres under suitable conditions.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 41,
            'documented_addresses_7bit': [41],
            'address_selection': 'software_with_xshut_for_multiple_devices',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 25.5,
            'height': 17.5,
            'depth': 4.6,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit INA219, STEMMA QT
    option = {
        'name_readable': 'Adafruit INA219, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '904',
        'manufacturer_part_number': '904',
        'type_1': 'sensor',
        'type_2': 'electrical',
        'type_3': 'current_voltage',
        'type_4': 'ina219',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/904',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Current and bus-voltage measurement for battery, solar and power-use experiments.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [64, 65, 68, 69],
            'address_selection': 'solder_jumpers',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'Product revisions may fit INA219A or INA219B in SOT-23 or SOIC packages; do not assert a single fitted grade.',
            'The current board has a pre-soldered terminal block; board nominal shunt is 0.1 ohm.',
        ],
        'product_dimensions_mm': {
            'width': 25.6,
            'height': 20.4,
            'depth': 4.7,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit ADS1115, STEMMA QT
    option = {
        'name_readable': 'Adafruit ADS1115, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '1085',
        'manufacturer_part_number': '1085',
        'type_1': 'interface',
        'type_2': 'adc',
        'type_3': 'general_purpose',
        'type_4': 'ads1115',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/1085',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Four single-ended or two differential analog inputs, 16-bit conversion and programmable gain.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [72, 73, 74, 75],
            'address_selection': 'address_pin',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 25.4,
            'height': 17.8,
            'depth': 4.6,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit MCP4725, STEMMA QT
    option = {
        'name_readable': 'Adafruit MCP4725, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '935',
        'manufacturer_part_number': '935',
        'type_1': 'interface',
        'type_2': 'dac',
        'type_3': 'voltage_output',
        'type_4': 'mcp4725',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/935',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A straightforward 12-bit analog output with EEPROM-backed startup configuration.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [98, 99],
            'address_selection': 'addr_a0_pin_or_solder_jumper',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit MCP23017 GPIO Expander, STEMMA QT
    option = {
        'name_readable': 'Adafruit MCP23017 GPIO Expander, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '5346',
        'manufacturer_part_number': '5346',
        'type_1': 'interface',
        'type_2': 'gpio_expander',
        'type_3': '16_bit',
        'type_4': 'mcp23017',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/5346',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds 16 digital inputs/outputs, with interrupts and selectable addresses.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 43,
            'height': 18,
            'depth': 5,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit TCA9548A I2C Multiplexer
    option = {
        'name_readable': 'Adafruit TCA9548A I2C Multiplexer',
        'manufacturer': 'adafruit',
        'part_number': '2717',
        'manufacturer_part_number': '2717',
        'type_1': 'interface',
        'type_2': 'i2c',
        'type_3': 'multiplexer',
        'type_4': 'tca9548a',
        'board_variant': 'header_breakout',
        'webpage': 'https://www.adafruit.com/product/2717',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Enables separate bus branches for devices that share an address. This is an active multiplexer, distinct from a passive connector hub.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 112,
            'documented_addresses_7bit': [112, 113, 114, 115, 116, 117, 118, 119],
            'address_selection': 'address_pins',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 30.6,
            'height': 17.6,
            'depth': 2.7,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit PCA9685 PWM/Servo Driver
    option = {
        'name_readable': 'Adafruit PCA9685 PWM/Servo Driver',
        'manufacturer': 'adafruit',
        'part_number': '815',
        'manufacturer_part_number': '815',
        'type_1': 'output',
        'type_2': 'pwm',
        'type_3': '16_channel',
        'type_4': 'pca9685',
        'board_variant': '16_channel_servo_driver',
        'webpage': 'https://www.adafruit.com/product/815',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds 16 channels of 12-bit PWM for servo signals and LED control. Separate load power is part of the board definition.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'Servo/load supply and logic supply are separate; PWM outputs do not directly supply motor power.',
            'Product dimensions conflict in inch/mm conversion; PCB dimensions remain unverified pending CAD.',
        ],
    }
    options.append(option)

    # Adafruit DS3231 RTC, STEMMA QT
    option = {
        'name_readable': 'Adafruit DS3231 RTC, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '5188',
        'manufacturer_part_number': '5188',
        'type_1': 'timing',
        'type_2': 'rtc',
        'type_3': 'temperature_compensated',
        'type_4': 'ds3231',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/5188',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Accurate timekeeping with battery backup; use the current QT carrier rather than silently substituting the older 3013 board.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 25.4,
            'height': 17.8,
            'depth': 7.8,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit MPR121 Touch Breakout, STEMMA QT
    option = {
        'name_readable': 'Adafruit MPR121 Touch Breakout, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '1982',
        'manufacturer_part_number': '1982',
        'type_1': 'input',
        'type_2': 'touch',
        'type_3': 'capacitive',
        'type_4': 'mpr121',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/1982',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Twelve touch inputs for interfaces, switches and interactive objects. Select the header breakout, not the separate Gator carrier.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 90,
            'documented_addresses_7bit': [90, 91, 92, 93],
            'address_selection': 'addr_pin',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit 1.3-inch 128x64 SSD1306 OLED, STEMMA QT
    option = {
        'name_readable': 'Adafruit 1.3-inch 128x64 SSD1306 OLED, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '938',
        'manufacturer_part_number': '938',
        'type_1': 'output',
        'type_2': 'display',
        'type_3': 'oled',
        'type_4': 'ssd1306',
        'board_variant': '128x64_1_3_inch_stemma_qt',
        'webpage': 'https://www.adafruit.com/product/938',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A useful text/graphics display for standalone projects. Record 128x64 resolution and the specific carrier; the current board defaults to I2C and can be reconfigured for SPI.',
        'dimensions_mm': {
            'width': 35.6,
            'height': 33,
            'status': 'manufacturer_nominal',
            'scope': 'nominal_pcb_outline',
            'source_id': 'product',
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [60, 61],
            'address_selection': 'solder_jumpers',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'Current carrier defaults to I2C; conversion to SPI requires solder-jumper changes.',
            'Manufacturer states mounting-hole spacing 30.5 x 28 mm and 2.5 mm diameter; hole coordinates have not been imported.',
        ],
    }
    options.append(option)

    # Adafruit SCD-40 CO2 Sensor, STEMMA QT
    option = {
        'name_readable': 'Adafruit SCD-40 CO2 Sensor, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '5187',
        'manufacturer_part_number': '5187',
        'type_1': 'sensor',
        'type_2': 'environmental',
        'type_3': 'carbon_dioxide',
        'type_4': 'scd40',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/5187',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Direct photoacoustic CO2 measurement, plus temperature and humidity. This complements the gas-response BME688 rather than representing the same measurement.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 98,
            'documented_addresses_7bit': [98],
            'address_selection': 'not_recorded',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 25.5,
            'height': 22.8,
            'depth': 7.7,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # SparkFun Qwiic Scale, NAU7802
    option = {
        'name_readable': 'SparkFun Qwiic Scale, NAU7802',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_15242',
        'manufacturer_part_number': 'SEN-15242',
        'type_1': 'interface',
        'type_2': 'adc',
        'type_3': 'load_cell',
        'type_4': 'nau7802',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-qwiic-scale-nau7802.html',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A 24-bit load-cell amplifier/converter for weighing and force projects. The external load cell remains a separate component.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 42,
            'documented_addresses_7bit': [42],
            'address_selection': 'fixed_hardware',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'NAU7802 has a hardware-fixed 0x2A address; multiple boards need separated bus branches.',
            'Uses an external load cell, not included in this board record.',
        ],
    }
    options.append(option)

    # SparkFun BME688 Environmental Sensor, Qwiic
    option = {
        'name_readable': 'SparkFun BME688 Environmental Sensor, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_19096',
        'manufacturer_part_number': 'SEN-19096',
        'type_1': 'sensor',
        'type_2': 'environmental',
        'type_3': 'gas_temperature_humidity_pressure',
        'type_4': 'bme688',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-environmental-sensor-bme688-qwiic.html',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds gas response/scanning alongside the weather measurements. Gas-derived classifications need their own software and calibration context.',
        'dimensions_mm': {
            'width': 25.4,
            'height': 25.4,
            'status': 'manufacturer_nominal',
            'scope': 'nominal_pcb_outline',
            'source_id': 'product',
        },
        'i2c': {
            'default_address_7bit': 118,
            'documented_addresses_7bit': [118, 119],
            'address_selection': 'board_configuration',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # SparkFun BNO086 VR IMU, Qwiic
    option = {
        'name_readable': 'SparkFun BNO086 VR IMU, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_22857',
        'manufacturer_part_number': 'SEN-22857',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'orientation_fusion',
        'type_4': 'bno086',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-vr-imu-breakout-bno086-qwiic.html',
        'interfaces': ['i2c', 'spi', 'uart'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds onboard sensor fusion and orientation outputs beyond a raw six-axis IMU. Supports I2C, SPI and UART; host compatibility still needs checking before enabling a lab profile.',
        'dimensions_mm': {
            'width': 25.4,
            'height': 30.48,
            'status': 'manufacturer_nominal',
            'scope': 'nominal_pcb_outline',
            'source_id': 'product',
        },
        'i2c': {
            'default_address_7bit': 75,
            'documented_addresses_7bit': [74, 75],
            'address_selection': 'address_select_jumper',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'UART is also supported. I2C is the default board interface.',
            'Review host driver/clock-stretching compatibility before enabling a firmware profile.',
        ],
    }
    options.append(option)

    # SparkFun TMP117 Precision Temperature Sensor, Qwiic
    option = {
        'name_readable': 'SparkFun TMP117 Precision Temperature Sensor, Qwiic',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_15805',
        'manufacturer_part_number': 'SEN-15805',
        'type_1': 'sensor',
        'type_2': 'environmental',
        'type_3': 'temperature',
        'type_4': 'tmp117',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-high-precision-temperature-sensor-tmp117-qwiic.html',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A dedicated precision-temperature reference option with programmable alerts.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 72,
            'documented_addresses_7bit': [72, 73, 74, 75],
            'address_selection': 'board_configuration',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # SparkFun Qwiic Twist RGB Rotary Encoder
    option = {
        'name_readable': 'SparkFun Qwiic Twist RGB Rotary Encoder',
        'manufacturer': 'sparkfun',
        'part_number': 'dev_15083',
        'manufacturer_part_number': 'DEV-15083',
        'type_1': 'input',
        'type_2': 'encoder',
        'type_3': 'rotary',
        'type_4': 'qwiic_twist',
        'board_variant': 'qwiic',
        'webpage': 'https://www.sparkfun.com/sparkfun-qwiic-twist-rgb-rotary-encoder-breakout.html',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A dial, push-button and RGB indicator accessible over I2C. Its tall assembly is useful to document separately from flat sensor boards. This leaf names the assembled product rather than inventing an unverified controller IC.',
        'dimensions_mm': {
            'width': 25.4,
            'height': 30.5,
            'status': 'manufacturer_nominal',
            'scope': 'nominal_pcb_outline',
            'source_id': 'product',
        },
        'i2c': {
            'default_address_7bit': 63,
            'documented_addresses_7bit': [62, 63],
            'address_selection': 'solder_jumper_or_software',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'Software-configurable addressing is supported; only 0x3F/0x3E hardware choices are enumerated here.',
            'Product-page statements about multiple encoders and multiplexers are inconsistent; verify the register-map/firmware behavior before multi-device use.',
            'Manufacturer specifies 25 mm assembly height.',
        ],
    }
    options.append(option)

    # Adafruit VL53L0X Distance Sensor
    option = {
        'name_readable': 'Adafruit VL53L0X Distance Sensor',
        'manufacturer': 'adafruit',
        'part_number': '3317',
        'manufacturer_part_number': '3317',
        'type_1': 'sensor',
        'type_2': 'distance',
        'type_3': 'time_of_flight',
        'type_4': 'vl53l0x',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/3317',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds a familiar earlier ToF family and a reference for comparison with generic carriers. Keep its performance and mechanical evidence separate from the VL53L1X.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 21,
            'height': 18,
            'depth': 2.8,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit I2C FRAM, 256 Kbit / 32 KByte
    option = {
        'name_readable': 'Adafruit I2C FRAM, 256 Kbit / 32 KByte',
        'manufacturer': 'adafruit',
        'part_number': '1895',
        'manufacturer_part_number': '1895',
        'type_1': 'memory',
        'type_2': 'fram',
        'type_3': '256_kbit',
        'type_4': '',
        'board_variant': 'header_breakout',
        'webpage': 'https://www.adafruit.com/product/1895',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Adds persistent logging/configuration storage. Leave the exact fitted memory IC as unverified until checked against the board schematic/BOM; do not derive it solely from capacity.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
        'product_dimensions_mm': {
            'width': 15.5,
            'height': 20,
            'depth': 2,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit ADXL345, STEMMA QT
    option = {
        'name_readable': 'Adafruit ADXL345, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '1231',
        'manufacturer_part_number': '1231',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'adxl345',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/1231',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A classic three-axis digital accelerometer, selectable +/-2/4/8/16 g, with I2C and SPI. The current carrier has regulation and level shifting; its 2022 QT revision changed the shape and pinout.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': 83,
            'documented_addresses_7bit': [83],
            'address_selection': 'alternate_not_recorded',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit LIS3DH, current QT carrier
    option = {
        'name_readable': 'Adafruit LIS3DH, current QT carrier',
        'manufacturer': 'adafruit',
        'part_number': '2809',
        'manufacturer_part_number': '2809',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'lis3dh',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/2809',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A widely used low-power three-axis option with selectable +/-2/4/8/16 g, I2C/SPI, interrupts and motion/tap features. The 2020 QT revision changed carrier geometry and pinout.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # Adafruit MMA8451
    option = {
        'name_readable': 'Adafruit MMA8451',
        'manufacturer': 'adafruit',
        'part_number': '2019',
        'manufacturer_part_number': '2019',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'mma8451',
        'board_variant': 'header_breakout',
        'webpage': 'https://www.adafruit.com/product/2019',
        'interfaces': ['i2c'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A traditional header-based I2C board with 14-bit conversion and selectable +/-2/4/8 g. The carrier includes a regulator and level shifting. Record its repeated-start requirement and selectable 0x1C/0x1D addresses.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [28, 29],
            'address_selection': 'address_selection_pin',
            'address_evidence_status': 'partial_product_page_evidence',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': ['The device requires repeated-start I2C transactions.'],
        'product_dimensions_mm': {
            'width': 21,
            'height': 18,
            'depth': 2,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)

    # Adafruit ADXL343, STEMMA QT
    option = {
        'name_readable': 'Adafruit ADXL343, STEMMA QT',
        'manufacturer': 'adafruit',
        'part_number': '4097',
        'manufacturer_part_number': '4097',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'adxl343',
        'board_variant': 'stemma_qt',
        'webpage': 'https://www.adafruit.com/product/4097',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'A related ADXL345-style three-axis I2C/SPI option, with selectable +/-2/4/8/16 g and motion interrupts. Keep it as a distinct chip family even where libraries support both.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [],
    }
    options.append(option)

    # SparkFun ADXL345, traditional carrier
    option = {
        'name_readable': 'SparkFun ADXL345, traditional carrier',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_09836',
        'manufacturer_part_number': 'SEN-09836',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'adxl345',
        'board_variant': 'header_breakout',
        'webpage': 'https://www.sparkfun.com/sparkfun-triple-axis-accelerometer-breakout-adxl345.html',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': "The familiar non-Qwiic header carrier, with I2C/SPI and two standoff holes. The product specifies a 2.0-3.6 V supply; do not inherit the Adafruit carrier's regulator/level-shifting claims. Vendor SKU is SEN-09836.",
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': [
            'Manufacturer lists 2.0-3.6 V supply; do not copy voltage tolerance from an Adafruit carrier.',
        ],
    }
    options.append(option)

    # SparkFun LIS3DH, traditional carrier
    option = {
        'name_readable': 'SparkFun LIS3DH, traditional carrier',
        'manufacturer': 'sparkfun',
        'part_number': 'sen_13963',
        'manufacturer_part_number': 'SEN-13963',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'lis3dh',
        'board_variant': 'header_breakout',
        'webpage': 'https://www.sparkfun.com/sparkfun-triple-axis-accelerometer-breakout-lis3dh.html',
        'interfaces': ['i2c', 'spi'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': "A simple non-Qwiic I2C/SPI header carrier. The product specifies a 1.7-3.6 V supply and describes it as a 3.3 V board. Keep separate from SparkFun's Qwiic, Micro and pre-headered carrier variants. Vendor SKU is SEN-13963.",
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': {
            'default_address_7bit': None,
            'documented_addresses_7bit': [],
            'address_selection': 'unverified',
            'address_evidence_status': 'unverified',
            'maximum_clock_hz': None,
            'clock_stretching': 'unverified',
        },
        'notes': ['Manufacturer lists 1.7-3.6 V supply and describes the carrier as a 3.3 V device.'],
    }
    options.append(option)

    # Adafruit ADXL335
    option = {
        'name_readable': 'Adafruit ADXL335',
        'manufacturer': 'adafruit',
        'part_number': '163',
        'manufacturer_part_number': '163',
        'type_1': 'sensor',
        'type_2': 'motion',
        'type_3': 'accelerometer',
        'type_4': 'adxl335',
        'board_variant': 'analog_xyz_header_breakout',
        'webpage': 'https://www.adafruit.com/product/163',
        'interfaces': ['analog'],
        'interface_scope': 'documented_board_interfaces_only',
        'description': 'Three analog XYZ outputs, +/-3 g. Add only as an explicit analog extension; it is not an I2C device. The carrier includes a 3.3 V regulator and header pads.',
        'dimensions_mm': {
            'width': None,
            'height': None,
            'status': 'unverified',
            'scope': 'pcb_outline_not_established',
            'source_id': None,
        },
        'i2c': None,
        'notes': ['Analog-only exception: three XYZ voltage outputs and no I2C interface.'],
        'product_dimensions_mm': {
            'width': 19,
            'height': 19,
            'depth': 3.14,
            'scope': 'manufacturer_product_dimensions_not_verified_pcb_outline',
            'source_id': 'product',
        },
    }
    options.append(option)


    for option in options:
        _complete_record(option)
    validate(options)
    return options


def _dimension_token(value):
    return format(value, "g").replace(".", "_")


def _complete_record(option):
    """Supply common metadata without shifting any fixed taxonomy positions."""
    option["schema_version"] = 1
    option["item_kind"] = "breakout"
    option["catalogue"] = "i2c_breakouts"
    option["catalogue_status"] = "product_page_reference"
    option["taxonomy_schema"] = TAXONOMY_SCHEMA
    option["research_date"] = RESEARCH_DATE
    option["definition_authority"] = Path(__file__).name
    for index in range(1, 16):
        option[f"taxonomy_{index}"] = ""
    option["taxonomy_1"] = "electronic"
    option["taxonomy_2"] = "breakout"
    for index in range(1, 5):
        option[f"taxonomy_{index + 2}"] = option[f"type_{index}"]
    option["taxonomy_7"] = option["board_variant"]
    dimensions = option["dimensions_mm"]
    if dimensions["width"] is not None and dimensions["height"] is not None:
        option["taxonomy_8"] = (
            _dimension_token(dimensions["width"]) + "_mm_width_"
            + _dimension_token(dimensions["height"]) + "_mm_height"
        )
    option["taxonomy_14"] = option["manufacturer"]
    option["taxonomy_15"] = option["part_number"]
    option["breakout_description"] = option["board_variant"]
    option["breakout_pcb_width"] = dimensions["width"]
    option["breakout_pcb_height"] = dimensions["height"]
    option[f"webpage_{option['manufacturer']}"] = option["webpage"]
    option[f"part_number_{option['manufacturer']}"] = option["manufacturer_part_number"]
    option["sources"] = [{
        "id": "product",
        "url": option["webpage"],
        "retrieved": RESEARCH_DATE,
        "kind": "manufacturer_product_page",
        "scope": "identity, stated interfaces/features and recorded nominal dimensions",
    }]
    option["pins"] = {}
    option["pinout_status"] = "unverified"
    option["mounting_holes"] = []
    option["mounting_hole_details"] = []
    option["mounting_hole_status"] = "unverified"
    option["geometry_ready"] = False
    option["oobb_details"] = []
    option["data_gaps"] = [
        "Physical connector/pad map and coordinates not imported.",
        "Located mounting holes and complete assembly/connector clearances not imported.",
        "Pull-up values/rails and full electrical limits require schematic review.",
    ]
    if dimensions["width"] is None:
        option["data_gaps"].append("Carrier PCB outline dimensions not verified.")
    else:
        option["data_gaps"].append("Manufacturer nominal outline is not a traced CAD perimeter.")
    if "i2c" in option["interfaces"]:
        option["i2c"]["source_id"] = "product"
        if option["i2c"]["default_address_7bit"] is None:
            option["data_gaps"].append("Default I2C address not established in this import.")


def get_identifier(option):
    return "_".join(option[f"taxonomy_{index}"] for index in range(1, 16)
                    if option[f"taxonomy_{index}"])


def validate(options):
    """Reject broken identity, taxonomy, evidence and interface declarations."""
    identifiers = set()
    for option in options:
        for index in range(1, 16):
            value = option[f"taxonomy_{index}"]
            if not isinstance(value, str) or (value and not re.fullmatch(r"[a-z0-9_]+", value)):
                raise ValueError(f"Invalid taxonomy_{index}: {value!r}")
        if option["manufacturer"] not in ("sparkfun", "adafruit"):
            raise ValueError("Only the researched manufacturer boards belong in this catalogue")
        if (option["taxonomy_14"], option["taxonomy_15"]) != (option["manufacturer"], option["part_number"]):
            raise ValueError("Manufacturer/part number must occupy taxonomy slots 14/15")
        identifier = get_identifier(option)
        if identifier in identifiers:
            raise ValueError("Duplicate board: " + identifier)
        identifiers.add(identifier)
        if option["sources"][0]["url"] != option["webpage"]:
            raise ValueError("Missing product evidence: " + identifier)
        dimensions = option["dimensions_mm"]
        if (dimensions["width"] is None) != (dimensions["height"] is None):
            raise ValueError("Outline dimensions must be supplied together")
        for axis in ("width", "height"):
            value = dimensions[axis]
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0):
                raise ValueError("Invalid outline dimension")
        if "i2c" in option["interfaces"]:
            i2c = option["i2c"]
            addresses = i2c["documented_addresses_7bit"]
            default = i2c["default_address_7bit"]
            if any(type(address) is not int or not 0x08 <= address <= 0x77 for address in addresses):
                raise ValueError("I2C addresses must be unshifted, non-reserved seven-bit values")
            if default is not None and default not in addresses:
                raise ValueError("Default I2C address missing from documented addresses")
        elif option["i2c"] is not None:
            raise ValueError("Non-I2C board must not advertise an I2C address")
        if option["oobb_details"] or option["geometry_ready"]:
            raise ValueError("Product-page records must not schedule unverified manufacturing geometry")


def populate(*, generate_parts=False, destination=None):
    """Run the established source writer, optionally followed by the parts loader."""
    from oomp_populate_helper import build_oomp_id, write_extras

    destination = ROOT if destination is None else Path(destination).resolve()
    destination.mkdir(parents=True, exist_ok=True)
    options = main()
    from working_oomp_populate_mounting import apply_mounting
    apply_mounting(options)
    identifiers = [build_oomp_id(option) for option in options]
    with contextlib.chdir(destination):
        write_extras(options)
        if generate_parts:
            import working_oomp
            working_oomp.main(part_ids=identifiers)
    return identifiers


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--parts", action="store_true", help="Also generate these boards in parts/")
    args = parser.parse_args()
    identifiers = populate(generate_parts=args.parts)
    print(f"Created {len(identifiers)} parts_source records" + (" and parts records" if args.parts else ""))
