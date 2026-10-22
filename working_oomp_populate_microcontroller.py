import copy
import itertools

from requests import options

from oomp_populate_helper import build_oomp_id, write_extras


def main(**kwargs):

    options = []

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "feather",
            "breakout_description": "22_86_mm_width_50_8_mm_height_28_pin",
            "manufacturer": "adafruit",
            "part_number": "4884",
            "breakout_pcb_width": 22.86,
            "breakout_pcb_height": 50.8,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "pico",
            "type_4": "wifi_bluetooth",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_w",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "pico",
            "type_4": "wifi_bluetooth",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_wh",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "pico",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "pico",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_h",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "pro_micro",
            "breakout_description": "17_78_mm_width_33_02_mm_height_24_pin",
            "manufacturer": "sparkfun_dev",
            "part_number": "18288",
            "breakout_pcb_width": 17.78,
            "breakout_pcb_height": 33.02,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "qt_py",
            "breakout_description": "18_mm_width_21_mm_height_14_pin",
            "manufacturer": "adafruit",
            "part_number": "4900",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "xiao",
            "breakout_description": "17_8_mm_width_21_mm_height_14_pin",
            "manufacturer": "seeed_studio",
            "part_number": "102010428",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "zero",
            "breakout_description": "18_mm_width_23_5_mm_height_20_pin",
            "manufacturer": "waveshare",
            "part_number": "rp2040_zero",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2040",
            "type_3": "zero",
            "breakout_description": "18_mm_width_23_5_mm_height_20_pin",
            "manufacturer": "waveshare",
            "part_number": "rp2040_zero_m",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "feather",
            "breakout_description": "22_86_mm_width_50_8_mm_height_28_pin",
            "manufacturer": "hstx_adafruit",
            "part_number": "6000",
            "breakout_pcb_width": 22.86,
            "breakout_pcb_height": 50.8,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "pico",
            "type_4": "wifi_bluetooth",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_2_w",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "pico",
            "type_4": "wifi_bluetooth",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_2_w_with_headers",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "pico",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_2",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "pico",
            "breakout_description": "21_mm_width_51_mm_height_40_pin",
            "manufacturer": "raspberry_pi",
            "part_number": "pico_2_with_headers",
            "breakout_pcb_width": 21,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "xiao",
            "breakout_description": "17_8_mm_width_21_mm_height_14_pin",
            "manufacturer": "seeed_studio",
            "part_number": "102010550",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "rp2350a",
            "type_3": "zero",
            "breakout_description": "18_mm_width_23_5_mm_height_20_pin",
            "manufacturer": "waveshare",
            "part_number": "rp2350_zero",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32",
            "type_3": "devkit_v1_30_pin",
            "breakout_description": "28_33_mm_width_51_45_mm_height_30_pins",
            "manufacturer": "doit",
            "part_number": "esp32_devkit_v1_30_pin",
            "breakout_pcb_width": 28.33,
            "breakout_pcb_height": 51.45,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32e",
            "type_3": "devkitc_v4_38_pin",
            "breakout_description": "27_9_mm_width_54_4_mm_height_38_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_devkitc_32e",
            "breakout_pcb_width": 27.9,
            "breakout_pcb_height": 54.4,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32",
            "type_3": "nodemcu_32s_38_pin",
            "breakout_description": "26_mm_width_54_mm_height_38_pins",
            "manufacturer": "generic",
            "part_number": "nodemcu_32s",
            "breakout_pcb_width": 26,
            "breakout_pcb_height": 54,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3_wroom_1_n8r8",
            "type_3": "devkitc_1_44_pin",
            "breakout_description": "25_4_mm_width_62_74_mm_height_44_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_s3_devkitc_1_n8r8",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 62.74,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3_mini_1",
            "type_3": "devkitm_1_20_pin",
            "breakout_description": "30_mm_width_50_9_mm_height_20_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_c3_devkitm_1",
            "breakout_pcb_width": 30,
            "breakout_pcb_height": 50.9,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3_wroom_02",
            "type_3": "devkitc_02_30_pin",
            "breakout_description": "38_9_mm_width_25_4_mm_height_30_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_c3_devkitc_02",
            "breakout_pcb_width": 38.9,
            "breakout_pcb_height": 25.4,

        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c6_wroom_1_n8",
            "type_3": "devkitc_1_30_pin",
            "breakout_description": "25_4_mm_width_58_15_mm_height_30_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_c6_devkitc_1_n8",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 58.15,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c6_mini_1_n4",
            "type_3": "devkitm_1_30_pin",
            "breakout_description": "25_4_mm_width_53_65_mm_height_30_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_c6_devkitm_1_n4",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 53.65,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s2_wroom",
            "type_3": "devkitc_1_44_pin",
            "breakout_description": "25_4_mm_width_62_74_mm_height_44_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_s2_devkitc_1",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 62.74,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3_fn4",
            "type_3": "supermini_16_pin",
            "breakout_description": "18_mm_width_22_5_mm_height_16_pins",
            "manufacturer": "generic",
            "part_number": "esp32_c3_supermini",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 22.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3",
            "type_3": "supermini_18_pin",
            "breakout_description": "18_mm_width_23_5_mm_height_18_pins",
            "manufacturer": "tenstar",
            "part_number": "esp32_s3_supermini",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c6",
            "type_3": "supermini_20_pin",
            "breakout_description": "18_mm_width_23_5_mm_height_20_pins",
            "manufacturer": "tenstar",
            "part_number": "esp32_c6_supermini",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_h2",
            "type_3": "supermini_18_pin",
            "breakout_description": "18_mm_width_23_5_mm_height_18_pins",
            "manufacturer": "tenstar",
            "part_number": "esp32_h2_supermini",
            "breakout_pcb_width": 18,
            "breakout_pcb_height": 23.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3",
            "type_3": "xiao_esp32c3",
            "breakout_description": "17_8_mm_width_21_mm_height_14_pins",
            "manufacturer": "seeed_studio",
            "part_number": "xiao_esp32c3",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3",
            "type_3": "xiao_esp32s3",
            "breakout_description": "17_8_mm_width_21_mm_height_14_pins",
            "manufacturer": "seeed_studio",
            "part_number": "xiao_esp32s3",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c6",
            "type_3": "xiao_esp32c6",
            "breakout_description": "17_8_mm_width_21_mm_height_14_pins",
            "manufacturer": "seeed_studio",
            "part_number": "xiao_esp32c6",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3_fn4",
            "type_3": "qt_py_esp32_c3",
            "breakout_description": "17_8_mm_width_22_mm_height_14_pins",
            "manufacturer": "adafruit",
            "part_number": "5405",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 22,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3",
            "type_3": "qt_py_esp32_s3",
            "breakout_description": "17_8_mm_width_21_7_mm_height_14_pins",
            "manufacturer": "adafruit",
            "part_number": "qt_py_esp32_s3",
            "breakout_pcb_width": 17.8,
            "breakout_pcb_height": 21.7,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s2",
            "type_3": "lolin_s2_mini",
            "breakout_description": "25_4_mm_width_34_3_mm_height_32_pins",
            "manufacturer": "wemos",
            "part_number": "lolin_s2_mini",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 34.3,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3fh4",
            "type_3": "lolin_c3_mini",
            "breakout_description": "25_4_mm_width_34_3_mm_height",
            "manufacturer": "wemos",
            "part_number": "lolin_c3_mini",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 34.3,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3",
            "type_3": "lolin_s3_mini",
            "breakout_description": "25_4_mm_width_34_3_mm_height",
            "manufacturer": "wemos",
            "part_number": "lolin_s3_mini",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 34.3,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32",
            "type_3": "lolin_d32",
            "breakout_description": "25_4_mm_width_57_mm_height_20_pins",
            "manufacturer": "wemos",
            "part_number": "lolin_d32",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 57,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wrover",
            "type_3": "lolin_d32_pro",
            "breakout_description": "25_4_mm_width_65_mm_height_32_pins",
            "manufacturer": "wemos",
            "part_number": "lolin_d32_pro",
            "breakout_pcb_width": 25.4,
            "breakout_pcb_height": 65,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s",
            "type_3": "esp32_cam_16_pin",
            "breakout_description": "27_mm_width_40_5_mm_height_16_pins",
            "manufacturer": "ai_thinker",
            "part_number": "esp32_cam",
            "breakout_pcb_width": 27,
            "breakout_pcb_height": 40.5,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_pico_d4",
            "type_3": "pico_kit_20_pin",
            "breakout_description": "20_3_mm_width_52_mm_height_20_pins",
            "manufacturer": "espressif",
            "part_number": "esp32_pico_kit_v4",
            "breakout_pcb_width": 20.3,
            "breakout_pcb_height": 52,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32",
            "type_3": "huzzah32_feather",
            "breakout_description": "22_7_mm_width_51_mm_height_28_pins",
            "manufacturer": "adafruit",
            "part_number": "3405",
            "breakout_pcb_width": 22.7,
            "breakout_pcb_height": 51,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_s3",
            "type_3": "feather_esp32_s3",
            "breakout_description": "22_7_mm_width_52_3_mm_height_28_pins",
            "manufacturer": "adafruit",
            "part_number": "5477",
            "breakout_pcb_width": 22.7,
            "breakout_pcb_height": 52.3,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_wroom_32",
            "type_3": "d1_r32",
            "breakout_description": "53_34_mm_width_68_58_mm_height",
            "manufacturer": "generic",
            "part_number": "esp32_d1_r32",
            "breakout_pcb_width": 53.34,
            "breakout_pcb_height": 68.58,
        }
        options.append(option)

    if True:
        option = {
            "type_1": "microcontroller",
            "type_2": "esp32_c3",
            "type_3": "m5stamp_c3u",
            "breakout_description": "20_mm_width_34_mm_height",
            "manufacturer": "m5stack",
            "part_number": "stamp_c3u",
            "breakout_pcb_width": 20,
            "breakout_pcb_height": 34,
        }
        options.append(option)

    return options


# Call main automatically
if __name__ == "__main__":
    main()
