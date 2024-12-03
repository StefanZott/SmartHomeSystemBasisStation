| Supported Targets | ESP32 | ESP32-C2 | ESP32-C3 | ESP32-C6 | ESP32-H2 | ESP32-S2 | ESP32-S3 |
| ----------------- | ----- | -------- | -------- | -------- | -------- | -------- | -------- |

# _Sample project_

(See the README.md file in the upper level 'examples' directory for more information about examples.)

This is the simplest buildable example. The example is used by command `idf.py create-project`
that copies the project to user specified path and set it's name. For more information follow the [docs page](https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html#start-a-new-project)



## How to use example
We encourage the users to use the example as a template for the new projects.
A recommended way is to follow the instructions on a [docs page](https://docs.espressif.com/projects/esp-idf/en/latest/api-guides/build-system.html#start-a-new-project).

## Example folder contents

The project **sample_project** contains one source file in C language [main.c](main/main.c). The file is located in folder [main](main).

ESP-IDF projects are built using CMake. The project build configuration is contained in `CMakeLists.txt`
files that provide set of directives and instructions describing the project's source files and targets
(executable, library, or both). 

Below is short explanation of remaining files in the project folder.

```
├── CMakeLists.txt
├── main
│   ├── CMakeLists.txt
│   └── main.c
└── README.md                  This is the file you are currently reading
```
Additionally, the sample project contains Makefile and component.mk files, used for the legacy Make based build system. 
They are not used or needed when building with CMake and idf.py.

# Hardware

## Stückliste
| Stück | Name | Preis | Link |
| :---: | :---: | :---: | :--- |
| 1 | ESP32-S3-WROOM-2 | [6,21 €](https://www.mouser.de/ProductDetail/Espressif-Systems/ESP32-S3-WROOM-2-N32R8V?qs=sGAEpiMZZMu3sxpa5v1qrkR%2F6t0IkXq8%2Fwfpzku%252BThM%3D) | [Datasheet](https://www.mouser.de/datasheet/2/891/esp32_s3_wroom_2_datasheet_en-2902185.pdf)   [Footprint](https://github.com/espressif/kicad-libraries/blob/main/footprints/Espressif.pretty/ESP32-S3-WROOM-1.kicad_mod) [Symbol](https://github.com/espressif/kicad-libraries/tree/main/symbols) [3D-Models](https://www.snapeda.com/parts/ESP32-S3-WROOM-2-N32R8V/Espressif%20Systems/view-part/?ref=search&t=esp32-s3-wroom-2)
| 1 | TSR 1-2433E | [3,31 €](https://www.reichelt.com/dk/en/shop/product/dc_dc_converter_tsr_1e_1_a_6-36_3_3_vdc_sil-3-288646?PROVID=2788&gad_source=1&gclid=Cj0KCQjwu-63BhC9ARIsAMMTLXQah1hD_9dkKNU3fR1BPLRpt7zMLCJ1lF65J9EvhKjII7mxAZm5eI4aAiu6EALw_wcB) | [Datasheet](https://cdn-reichelt.de/documents/datenblatt/C700/TSR1-2433E_DB_EN.pdf) [Footprint Symbol](https://www.snapeda.com/parts/TSR%201-2433E/Traco%20Power/view-part/?welcome=home&ref=search&t=tsr1-2433) [3D-Models](https://www.snapeda.com/parts/TSR%201-2433E/Traco%20Power/view-part/?welcome=home&ref=search&t=tsr1-2433)
| 1 | MBB02070Z0000ZRP00 (Widerstand) | [0,40 €](https://www.mouser.de/ProductDetail/Vishay-Beyschlag/MBB02070Z0000ZRP00?qs=sGAEpiMZZMtlubZbdhIBIACtXsCE%2Fl4kMnYGM9CYwD0%3D) | [Datasheet](https://www.vishay.com/docs/28766/mbxsma.pdf) Footprint Symbol 3d-Model (KiCad8 Lib)
| 1 | 1543-650 - Push Switch | [1,13 €](https://www.mouser.de/ProductDetail/Bourns/1543-650-149?qs=2f2kQrcl%2FoiIszYh%252BBIYwA%3D%3D) | [Datasheet](https://www.mouser.de/datasheet/2/54/1543-55078.pdf) [Footprint Symbol](https://www.snapeda.com/parts/1543-650-149/Bourns/view-part/?ref=search&t=1543-650-149) 
| 2 | 890334023023 (WE - Kondensator) | [0,40 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/890334023023?qs=sGAEpiMZZMsh%252B1woXyUXjw135FJCisgx62221Dnepso%3D) | [Datasheet](https://www.we-online.com/components/products/datasheet/890334023023.pdf) [Footprint Symbol 3D-Model](https://www.snapeda.com/parts/890334023023/W%C3%BCrth%20Elektronik/view-part/?ref=search&t=890334023023)
| 1 | 870235673001 (WE - Kondensator) | [0,87 €](https://www.we-online.com/components/products/datasheet/870235673001.pdf) | [Datasheet](https://www.we-online.com/components/products/datasheet/870235673001.pdf) [Footprint Symbol](https://www.snapeda.com/parts/870235673001/W%C3%BCrth%20Elektronik/view-part/?ref=search&t=870235673001)
| 4 | EP4WSS220RJ (TE Connectivity - Widerstand) | [0,61 €](https://www.mouser.de/ProductDetail/TE-Connectivity-Neohm/EP4WSS220RJ?qs=HoCaDK9Nz5ea25zidrpq7Q%3D%3D) | [Datasheet](https://www.mouser.de/datasheet/2/418/9/ENG_CD_2176613_BA1-3367918.pdf) Foorprint Symbol 3D-Model (KiCad8 Lib)
| 1 | 151051BS04000 (WE-BLUE-LED) | [0,24 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/151051BS04000?qs=LlUlMxKIyB3OjuZOlqaOjg%3D%3D) | [Datasheet](https://www.mouser.de/datasheet/2/418/9/ENG_CD_2176613_BA1-3367918.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/151051BS04000/W%C3%BCrth%20Elektronik/view-part/?welcome=home&ref=search&t=151051BS04000)
| 1 | 151031YS05900 (WE-YELLOW-LED) | [0,17 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/151031YS05900?qs=LlUlMxKIyB2uWWsOjTR3Fw%3D%3D) | [Datasheet](https://www.we-online.com/components/products/datasheet/151031YS05900.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/151031YS05900/Wurth%20Electronics/view-part/?ref=search&t=151031YS05900)
| 1 | 151031YS05900 (WE-RED-LED) | [0,17 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/151033RS03000?qs=LlUlMxKIyB1%252BAw6bWFN43w%3D%3D) | [Datasheet](https://www.we-online.com/components/products/datasheet/151033RS03000.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/151033RS03000/W%C3%BCrth%20Elektronik/view-part/?ref=search&t=151033RS03000)
| 1 | 151031YS05900 (WE-GREEN-LED) | [0,16 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/151031VS06000?qs=LlUlMxKIyB01ggED1iKswA%3D%3D) | [Datasheet](https://www.we-online.com/components/products/datasheet/151031VS06000.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/151031VS06000/Wurth%20Electronics/view-part/?ref=search&t=151031VS06000)
| 1 | 61201021621 (WE 10 PIN MALE BOX) | [0,45 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/61201021621?qs=W%252B2sBeLta1a0dwX5pxbfXw%3D%3D&mgh=1&vip=1&utm_id=20968985688&gad_source=1&gclid=CjwKCAjwx4O4BhAnEiwA42SbVD3qD7Ghb3sIcNxPBit9jrGpqggUyeh4tj6mStcjgxjb2YuEWH3NOxoCIQsQAvD_BwE) | [Datasheet](https://www.we-online.com/components/products/datasheet/61201021621.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/61201021621/W%C3%BCrth%20Elektronik/view-part/?ref=search&t=61201021621)
| 1 | 61200621621 (WE 6 PIN MALE BOX) | [0,45 €](https://www.mouser.de/ProductDetail/Wurth-Elektronik/61200621621?qs=PhR8RmCirEbjX8n1RKw4Jw%3D%3D) | [Datasheet](https://www.we-online.com/components/products/datasheet/61200621621.pdf) [Foorprint Symbol 3D-Model](https://www.snapeda.com/parts/61200621621/Wurth%20Electronics/view-part/?ref=search&t=61200621621)