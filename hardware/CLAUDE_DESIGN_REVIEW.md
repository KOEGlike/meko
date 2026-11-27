# Meko v3: Hardware Design Review

*Review date: 2026-11-22; updated 2026-11-27 with the owner's later fixes and design decisions (see "Resolved since the review" and "Accepted by design"). Covers the main board (`hardware/pcb`) and the touchpad board (`hardware/pcb_touchpad`) as they stood in the working tree after the owner's two fixes: the WiFi SDMMC pull-ups moved to the correct rail, and C123 (10 µF) added on the BQ25640 BAT pin.*

## How this review was done

- `kicad-cli` (KiCad 10.0.8) exported the netlist, ERC, DRC (with schematic parity) and BOM for both boards. Every IC connection was checked pin-by-pin against the manufacturer datasheet: Microchip SAMA7D65 and MCP16502, TI BQ25640, TPS7A20, TAC5212 and DRV2605L, Micron MT41K256M16TW, u-blox MAYA-W3, ST ECMF02, Sharp LS022B7DH03, Azoteq IQS7211E, and Molex/HRO connectors. Reference designs (SAMA7D65 Curiosity) were used where datasheets left room for interpretation.
- Layout was checked with scripts that parse `meko.kicad_pcb`: DDR lengths with via barrels, trace widths and copper weight on power nets, via statistics, and keep-outs. Results were compared against JLCPCB's 6-layer 0.8 mm (JLC06081H-1080) capabilities.
- Six domain reviewers worked in parallel; a separate reviewer then checked their findings for errors.
- No project files were modified.
- Paths starting with `SCR/` point to the reviewer's temporary working directory (kicad-cli exports, downloaded datasheets, analysis scripts). They are not in the repo; regenerate the exports with `kicad-cli` if needed.

### Severity scale

| Severity | Meaning |
|---|---|
| **CRITICAL** | Board will not work, or damage/safety risk |
| **HIGH** | Very likely malfunction or major feature broken; needs a fix before fab, or rework |
| **MEDIUM** | Works marginally / out of spec / reliability, EMI, SI or DFM risk |
| **LOW** | Best practice, minor optimisation |
| **INFO** | Observation or rationale, no action needed |
| **RESOLVED** | Fixed by the owner after the review and verified against the design files |
| **ACCEPTED** | Deliberately left as-is by the owner, with a documented mitigation and residual risk |

## Executive summary

**No CRITICAL issues were found.** Every custom symbol and footprint that was checked matches its datasheet: the SAMA7D65 343-ball map (all balls), MAYA-W386, BQ25640, MCP16502, ECMF02, DDR3L FBGA-96, and the TAC5212 pin numbering. All DDR3L connections are valid. Every SoC pin-mux assignment is legal and sits on a correctly powered I/O bank. Both FPC cables are pin-1 to pin-1, checked in the 3D assembly. The board can be fabricated at JLC as drawn: through-vias only, 0.3/0.15 mm vias, 0.65 mm BGA fanout without via-in-pad.

Finding count: 1 HIGH, 20 MEDIUM, 52 LOW, 18 INFO, 10 RESOLVED, 2 ACCEPTED (some issues appear under more than one area; see the duplicates table).

### Fix before ordering (highest priority)

Remaining items to fix before fab (PWR-01 and PWR-03 were accepted by design; see below).

1. **AUD-02 (HIGH)**: The TAC5212 footprint is a generic VQFN-24. It lacks the package's four corner VSS pads and its exposed pad is larger than the package's. Use TI's land pattern.
2. **SAMA-06 (MEDIUM)**: BOM-only fix. R10/R11 (SDMMC2_CAL, QSPI0_CAL) should be 20 k because their banks run at 1.8 V.

### Accepted by design (firmware mitigation)

| ID | Was | Decision and required firmware |
|---|---|---|
| PWR-01 | HIGH | TS left floating, no thermistor. At every boot: `WATCHDOG = 00b` (first), `TS_IGNORE = 1`, ICHG ≈ 1.0–1.2 A; recommended: stop charging outside ~0–45 °C using the MAX17260 temperature. No hardware temperature protection. Bring-up checks: boot from USB with a dead battery, and confirm the registers persist with the SoC off. |
| PWR-03 | MEDIUM | L2 kept (2.2 µH, ~2.2 A I_temp / ~2.6 A I_sat). The software ICHG limit above keeps charge current plus system load within rating. The 2 A power-on default only returns after a full charger reset, usually with the device off. |

### Resolved since the review

| ID | Was | Fix (verified 2026-11-27 against the working tree) |
|---|---|---|
| TP-01 | HIGH | Touchpad re-assigned to 6 Rx × 7 Tx with a 3 + 3 Rx split, giving 21 cycles. Needs the RxTxMapping in firmware (see TP-01). |
| AUD-01 | HIGH | Jack-detect nets moved to ADC inputs PC3/AD0 and PC10/AD5. Firmware must set `bias-disable` (see AUD-01). |
| PWR-02 / SAMA-01 | MEDIUM | WKUP0 pulled up with 100 k to `+VBAT_SAMA`; R58 removed. |
| PWR-04 / CON-03 / LAY-04 | MEDIUM | VBUS moved to an In2 pour plus a 1.25 mm B.Cu trace: ≈ 33 mΩ, against ≈ 140 mΩ before. |
| SAMA-03 | MEDIUM | C54 changed to 1 µF: +2V5 is now ≈ 1.3 µF effective, inside the 1–2.7 µF stable range. |
| DDR-01 | MEDIUM | ODT re-meandered to 41.46 mm at 0.1072 mm, inside the 41–43 mm addr/ctl window; no DRC length/skew errors on ODT. |
| PWR-11 | — | C123 10 µF added on the BQ25640 BAT pin (meets the datasheet). |
| LAY-01 | — | WiFi SDMMC pull-ups moved to the correct rail: +3V3/+1V8 short and unconnected items gone. |

### Issues reported in more than one area

| Topic | IDs |
|---|---|
| WKUP0 pulled up from VSYS (**resolved**) | PWR-02, SAMA-01 |
| +1V8 (LDO2) off by default in the MCP16502AB, which breaks power-up sequencing | PWR-05, SAMA-02 |
| VBAT fed by LDO1 (both LOW) | PWR-15, SAMA-07 |
| VBUS trace resistance (**resolved**) | PWR-04, CON-03, LAY-04 |
| SDMMC2 calibration resistor R10 should be 20 k for 1.8 V | SAMA-06, CON-02 |
| MCLK contention between I2SMCC0_MCK and MAYA PCM_MCLK | SAMA-09, CON-09 |
| +3V3 buck load and MAYA bulk decoupling | PWR-07, CON-01 |
| Bulk decoupling near SoC/DDR | SAMA-04, DDR-08 |
| Antenna surroundings | CON-11, CON-16, LAY-05 |
| microSD slots 3.3 V-only (no UHS-I) | CON-07, SAMA-12 |
| No VBUS-present signal to the SoC | SAMA-12, CON-13 |
| BQ25640 D+/D− open, so legacy chargers are limited to 500 mA | PWR-09, CON-12 |
| Codec AVDD LDO (U3) always enabled | PWR-14, AUD-08 |
| Duplicate (co-located) GND via in the BGA | SAMA-11, LAY-07 |
| Stale fab/impedance note on Cmts.User | DDR-07, LAY-11 |
| DDR clearance-rule violations are not real SI problems | DDR-04, LAY-09 |
| Battery-connector/test-point courtyard overlaps | PWR-18, LAY-15 |

## All findings

| Severity | ID | Finding | Area |
|---|---|---|---|
| HIGH | [AUD-02](#high-aud-02-tac5212-footprint-has-no-pads-for-the-four-corner-vss-pins-a1-a4-and-its-ep-is-larger-than-the-packages-exposed-pad-needs-verification-with-ti) | TAC5212 footprint has no pads for the four corner VSS pins (A1-A4), and its EP is larger than the package's exposed pad (Needs verification with TI) | Peripherals |
| MEDIUM | [PWR-05](#medium-pwr-05-1v8-ldo2-is-off-at-power-up-in-the-ab-variant-so-periphery-supplies-come-up-after-vddcore) | +1V8 (LDO2) is OFF at power-up in the AB variant, so periphery supplies come up after VDDCORE | Power |
| MEDIUM | [PWR-06](#medium-pwr-06-3v3-and-3v3avdd-fall-out-of-regulation-at-low-battery) | 3V3 and 3V3_AVDD fall out of regulation at low battery | Power |
| MEDIUM | [PWR-07](#medium-pwr-07-buck1-3v3-1-a-rated-load-budget-is-tight) | Buck1 (+3V3, 1 A rated) load budget is tight | Power |
| MEDIUM | [PWR-08](#medium-pwr-08-battery-connector-jst-gh-2-pin-current-rating-vs-charge-and-discharge-current-no-reverse-polarity-protection) | Battery connector JST-GH 2-pin current rating vs charge and discharge current; no reverse-polarity protection | Power |
| MEDIUM | [SAMA-02](#medium-sama-02-1v8-rail-mcp16502ab-ldo2-is-off-by-default-so-vddiop1-vddqspi0-and-vddsdmmc2-power-up-after-the-core) | +1V8 rail (MCP16502AB LDO2) is OFF by default, so VDDIOP1, VDDQSPI0 and VDDSDMMC2 power up after the core | SAMA7D65 SoC core |
| MEDIUM | [SAMA-04](#medium-sama-04-bulk-decoupling-near-the-soc-is-below-the-datasheet-minimum-and-microchip-guidance-vddin33-vddutmii-vddioddr-vddcore) | Bulk decoupling near the SoC is below the datasheet minimum and Microchip guidance (VDDIN33, VDDUTMII, VDDIODDR, VDDCORE) | SAMA7D65 SoC core |
| MEDIUM | [SAMA-05](#medium-sama-05-24-mhz-crystal-drive-level-rating-is-probably-below-the-sama7d65-oscillators-requirement-needs-verification) | 24 MHz crystal drive-level rating is probably below the SAMA7D65 oscillator's requirement (Needs verification) | SAMA7D65 SoC core |
| MEDIUM | [SAMA-06](#medium-sama-06-sdmmc2cal-and-qspi0cal-use-the-33-v-calibration-resistor-value-on-18-v-banks) | SDMMC2_CAL and QSPI0_CAL use the 3.3 V calibration resistor value on 1.8 V banks | SAMA7D65 SoC core |
| MEDIUM | [CON-01](#medium-con-01-maya-3v3-supply-no-bulk-capacitance-near-the-module-single-small-via-and-the-1-a-buck-is-shared-with-both-sd-cards) | MAYA 3V3 supply: no bulk capacitance near the module, single small via, and the 1 A buck is shared with both SD cards | Connectivity |
| MEDIUM | [CON-02](#medium-con-02-sdmmc2-wifi-18-v-calibration-resistor-r10-16k9-the-data-sheet-requires-20-k-for-18-v) | SDMMC2 (WiFi, 1.8 V) calibration resistor R10 = 16k9; the data sheet requires 20 kΩ for 1.8 V | Connectivity |
| MEDIUM | [CON-04](#medium-con-04-external-microsd-j7-no-esd-protection-vdd-hard-wired-to-the-system-3v3-no-load-switch-or-power-cycling) | External microSD (J7): no ESD protection, VDD hard-wired to the system +3V3 (no load switch or power cycling) | Connectivity |
| MEDIUM | [CON-05](#medium-con-05-usb-c-vbuscc-have-no-populated-esd-protection-esd441-is-not-suitable-for-vbus) | USB-C VBUS/CC have no populated ESD protection; ESD441 is not suitable for VBUS | Connectivity |
| MEDIUM | [AUD-03](#medium-aud-03-micbias-pin-has-no-decoupling-capacitor) | MICBIAS pin has no decoupling capacitor | Peripherals |
| MEDIUM | [AUD-04](#medium-aud-04-no-esd-protection-on-the-user-accessible-jack-pins) | No ESD protection on the user-accessible jack pins | Peripherals |
| MEDIUM | [AUD-05](#medium-aud-05-headset-mic-bias-low-headroom-and-dc-coupled-input-loading) | Headset mic bias: low headroom and DC-coupled input loading | Peripherals |
| MEDIUM | [DISP-01](#medium-disp-01-vcom-com-inversion-mode-is-hard-wired-to-serial-but-this-panel-needs-57-hz-inversion) | VCOM (COM inversion) mode is hard-wired to serial, but this panel needs ≥57 Hz inversion | Peripherals |
| MEDIUM | [TP-02](#medium-tp-02-iqs7211e-decoupling-below-azoteq-requirements) | IQS7211E decoupling below Azoteq requirements | Peripherals |
| MEDIUM | [LAY-03](#medium-lay-03-jlc-standard-pcba-needs-edge-rails-and-fiducials-and-parts-overhang-every-edge) | JLC Standard PCBA needs edge rails and fiducials, and parts overhang every edge | Layout, DRC & manufacturability |
| MEDIUM | [LAY-05](#medium-lay-05-maya-w386-antenna-keep-out-is-correct-but-large-and-metal-parts-sit-inside-u-bloxs-10-mm-zone) | MAYA-W386 antenna: keep-out is correct, but large and metal parts sit inside u-blox's 10 mm zone | Layout, DRC & manufacturability |
| MEDIUM | [LAY-06](#medium-lay-06-four-ics-have-no-lcsc-part-number) | Four ICs have no LCSC part number | Layout, DRC & manufacturability |
| LOW | [PWR-09](#low-pwr-09-charger-defaults-and-otg-need-software-legacy-chargers-are-limited-to-500-ma) | Charger defaults and OTG need software; legacy chargers are limited to 500 mA | Power |
| LOW | [PWR-10](#low-pwr-10-pmid-capacitor-10-f-0402-63-v) | PMID capacitor: 10 µF 0402, 6.3 V | Power |
| LOW | [PWR-11](#low-pwr-11-new-bat-capacitor-c123-meets-the-datasheet-small-dc-bias-caveat-re-check-of-owners-fix) | New BAT capacitor C123: meets the datasheet, small DC-bias caveat (re-check of owner's fix) | Power |
| LOW | [PWR-12](#low-pwr-12-few-thermal-vias-under-u4) | Few thermal vias under U4 | Power |
| LOW | [PWR-13](#low-pwr-13-c126-100-nf-on-nstrt-makes-the-pmic-auto-start-whenever-vsys-ramps-from-0) | C126 (100 nF on nSTRT) makes the PMIC auto-start whenever VSYS ramps from 0 | Power |
| LOW | [PWR-14](#low-pwr-14-u3-tps7a2033-is-always-enabled-from-vsys) | U3 (TPS7A2033) is always enabled from VSYS | Power |
| LOW | [PWR-15](#low-pwr-15-vbat-supplied-by-ldo1-18-v-instead-of-a-backup-element-or-vddin33) | VBAT supplied by LDO1 (1.8 V) instead of a backup element or VDDIN33 | Power |
| LOW | [PWR-16](#low-pwr-16-max17260-u5-connections-verified-against-the-datasheet-csn-should-be-a-kelvin-trace-to-r29) | MAX17260 (U5) connections verified against the datasheet; CSN should be a Kelvin trace to R29 | Power |
| LOW | [SAMA-07](#low-sama-07-vbat-is-fed-from-pmic-ldo1-instead-of-vddin33-or-a-storage-element-sequencing-and-hibernate-depend-on-i2c-setup-needs-verification) | VBAT is fed from PMIC LDO1 instead of VDDIN33 or a storage element: sequencing and hibernate depend on I2C setup (Needs verification) | SAMA7D65 SoC core |
| LOW | [SAMA-08](#low-sama-08-debugsam-ba-uart-header-j1-has-no-gnd-pin) | Debug/SAM-BA UART header J1 has no GND pin | SAMA7D65 SoC core |
| LOW | [SAMA-09](#low-sama-09-possible-mclk-driver-contention-between-soc-i2smcc0mck-and-maya-pcmmclk) | Possible MCLK driver contention between SoC I2SMCC0_MCK and MAYA PCM_MCLK | SAMA7D65 SoC core |
| LOW | [SAMA-10](#low-sama-10-copper-routed-under-the-crystals) | Copper routed under the crystals | SAMA7D65 SoC core |
| LOW | [SAMA-11](#low-sama-11-bga-fanout-dfm-details) | BGA fanout DFM details | SAMA7D65 SoC core |
| LOW | [DDR-02](#low-ddr-02-ddr-diff-pair-skew-rule-compares-dqs-pairs-against-ck-giving-false-23-mm-skew-violations-real-intra-pair-skews-are-tiny) | "DDR diff pair skew" rule compares DQS pairs against CK, giving false 2–3 mm skew violations; real intra-pair skews are tiny | DDR3L memory |
| LOW | [DDR-03](#low-ddr-03-addrctl-spread-is-226-mm-own-rule-2-mm-5-nets-flagged-by-drc) | Addr/ctl spread is 2.26 mm (own rule 2 mm); 5 nets flagged by DRC | DDR3L memory |
| LOW | [DDR-04](#low-ddr-04-ddr-clearance-to-everything-44-and-ddr-diff-pair-clearance-12-violations-not-real-si-problems) | "DDR clearance to everything" (44) and "DDR diff pair clearance" (12) violations — not real SI problems | DDR3L memory |
| LOW | [DDR-05](#low-ddr-05-vref-track-runs-alongside-dq11-and-ddra13) | VREF track runs alongside DQ11 and DDR_A13 | DDR3L memory |
| LOW | [DDR-06](#low-ddr-06-stackup-dielectric-constants-do-not-match-jlcs-published-values-for-the-selected-template-impedance-is-still-inside-10) | Stackup dielectric constants do not match JLC's published values for the selected template; impedance is still inside ±10 % | DDR3L memory |
| LOW | [DDR-07](#low-ddr-07-stale-fabricationimpedance-note-on-cmtsuser-contradicts-the-actual-design) | Stale fabrication/impedance note on Cmts.User contradicts the actual design | DDR3L memory |
| LOW | [DDR-08](#low-ddr-08-bulk-decoupling-on-1v35ddr-is-thinner-than-the-microchip-reference) | Bulk decoupling on +1V35_DDR is thinner than the Microchip reference | DDR3L memory |
| LOW | [DDR-09](#low-ddr-09-u2-footprint-library-not-registered-symbol-is-a-modified-copy-of-the-kicad-library) | U2 footprint library not registered; symbol is a modified copy of the KiCad library | DDR3L memory |
| LOW | [DDR-10](#low-ddr-10-ddra15-not-routed-to-u2m7-no-drop-in-8-gb-option) | DDR_A15 not routed to U2.M7 (no drop-in 8 Gb option) | DDR3L memory |
| LOW | [CON-06](#low-con-06-tf-008-internal-os-card-detect-switch-is-normally-closed-so-bootcd-polarity-is-inverted-from-the-sama7-low-card-present-convention) | TF-008 (internal OS card) detect switch is normally-closed, so BOOT.CD polarity is inverted from the SAMA7 "low = card present" convention | Connectivity |
| LOW | [CON-07](#low-con-07-sd-slots-are-33-v-only-no-uhs-i-sdmmcx1v8sel-not-used) | SD slots are 3.3 V-only (no UHS-I); SDMMCx_1V8SEL not used | Connectivity |
| LOW | [CON-08](#low-con-08-wlen-bten-have-no-external-pull-down-sama7-reset-default-pull-up-fights-the-modules-50-k-pull-down) | WL_EN / BT_EN have no external pull-down; SAMA7 reset-default pull-up fights the module's 50 kΩ pull-down | Connectivity |
| LOW | [CON-09](#low-con-09-pcmmclk-is-wired-to-i2smcc0mck-so-two-outputs-share-one-net) | PCM_MCLK is wired to I2SMCC0_MCK, so two outputs share one net | Connectivity |
| LOW | [CON-10](#low-con-10-wifi-sdio-details-strappull-up-values-skew-no-series-r-option) | WiFi SDIO details: strap/pull-up values, skew, no series-R option | Connectivity |
| LOW | [CON-11](#low-con-11-antenna-feed-has-no-pi-network0-option-a-gnd-track-touches-the-rf-keep-out) | Antenna feed has no pi-network/0 Ω option; a GND track touches the RF keep-out | Connectivity |
| LOW | [CON-12](#low-con-12-bq25640-dd--left-unconnected-so-no-bc12-legacy-charger-detection) | BQ25640 D+/D- left unconnected, so no BC1.2 / legacy charger detection | Connectivity |
| LOW | [CON-13](#low-con-13-no-direct-vbus-present-signal-to-the-sama7-for-the-udc) | No direct VBUS-present signal to the SAMA7 for the UDC | Connectivity |
| LOW | [CON-14](#low-con-14-drc-clearance-violations-on-sdmmcext-sdmmcwl-usb-asibt-netclasses) | DRC clearance violations on SDMMC_EXT / SDMMC_WL / USB / ASI_BT netclasses | Connectivity |
| LOW | [AUD-06](#low-aud-06-codec-supply-decoupling-is-thinner-than-tis-typical-application) | Codec supply decoupling is thinner than TI's typical application | Peripherals |
| LOW | [AUD-07](#low-aud-07-shared-vcom-headphone-return-trace-adds-lr-crosstalk) | Shared VCOM headphone return trace adds L/R crosstalk | Peripherals |
| LOW | [AUD-08](#low-aud-08-codec-avdd-ldo-is-always-on) | Codec AVDD LDO is always on | Peripherals |
| LOW | [AUD-09](#low-aud-09-35-mm-ground-is-vcom-165-v-dc) | 3.5 mm "ground" is VCOM (1.65 V DC) | Peripherals |
| LOW | [I2C-01](#low-i2c-01-10-k-pull-ups-are-too-weak-for-400-khz-on-the-8-node-shared-bus) | 10 kΩ pull-ups are too weak for 400 kHz on the 8-node shared bus | Peripherals |
| LOW | [DISP-02](#low-disp-02-the-70-hz-full-frame-claim-is-not-reachable-at-the-panels-2-mhz-sclk-limit) | The 70 Hz full-frame claim is not reachable at the panel's 2 MHz SCLK limit | Peripherals |
| LOW | [DISP-03](#low-disp-03-3v3-tolerance-vs-the-ls022b7dh03-recommended-range) | +3V3 tolerance vs. the LS022B7DH03 recommended range | Peripherals |
| LOW | [DISP-04](#low-disp-04-scssclk-are-pulled-high-by-the-sama7-reset-pull-ups-during-boot) | SCS/SCLK are pulled high by the SAMA7 reset pull-ups during boot | Peripherals |
| LOW | [BTN-01](#low-btn-01-sidevolume-buttons-no-esd-protection-or-rc-filter-wake-capability-is-limited) | Side/volume buttons: no ESD protection or RC filter; wake capability is limited | Peripherals |
| LOW | [BTN-02](#low-btn-02-power-key-runtime-events-are-hard-to-use-from-linux) | Power-key runtime events are hard to use from Linux | Peripherals |
| LOW | [TP-03](#low-tp-03-iqs7211e-qnr-exposed-corner-gnd-pads-sit-over-the-col7-and-3v3-tracks) | IQS7211E-QNR exposed corner GND pads sit over the COL7 and +3V3 tracks | Peripherals |
| LOW | [MECH-01](#low-mech-01-j9-ffc-slot-is-very-tight-on-one-side-needs-verification) | J9 FFC slot is very tight on one side (Needs verification) | Peripherals |
| LOW | [SI-01](#low-si-01-asi-and-spi-lines-have-no-source-termination) | ASI and SPI lines have no source termination | Peripherals |
| LOW | [LAY-07](#low-lay-07-hole-to-hole-spacing-and-a-duplicate-via) | Hole-to-hole spacing and a duplicate via | Layout, DRC & manufacturability |
| LOW | [LAY-08](#low-lay-08-side-switches-sw1sw5-npth-holes-0099015-mm-from-pad-copper) | Side switches SW1–SW5: NPTH holes 0.099–0.15 mm from pad copper | Layout, DRC & manufacturability |
| LOW | [LAY-09](#low-lay-09-the-91-netclassdru-clearance-violations-are-si-preference-rules-not-dfm-problems) | The 91 netclass/DRU clearance violations are SI-preference rules, not DFM problems | Layout, DRC & manufacturability |
| LOW | [LAY-10](#low-lay-10-libfootprintmismatch-ic1-ic3-u5-u3-copper-identical-changes-are-cosmetic-library-drift) | lib_footprint_mismatch (IC1, IC3, U5, U3): copper identical, changes are cosmetic library drift | Layout, DRC & manufacturability |
| LOW | [LAY-11](#low-lay-11-fab-notes-on-usercomments-now-updated-one-ddr-value-is-still-stale) | Fab notes on User.Comments: now updated, one DDR value is still stale | Layout, DRC & manufacturability |
| LOW | [LAY-12](#low-lay-12-bom-hygiene-stale-fields-trailing-spaces-extended-part-fees) | BOM hygiene: stale fields, trailing spaces, extended-part fees | Layout, DRC & manufacturability |
| LOW | [LAY-13](#low-lay-13-silkscreen-thin-strokes-missing-font-qr-over-vias) | Silkscreen: thin strokes, missing font, QR over vias | Layout, DRC & manufacturability |
| LOW | [LAY-14](#low-lay-14-board-setup-rule-values-looser-or-stricter-than-jlc) | Board-setup rule values looser or stricter than JLC | Layout, DRC & manufacturability |
| INFO | [PWR-17](#info-pwr-17-mcp16502-power-stage-layout) | MCP16502 power-stage layout | Power |
| INFO | [PWR-18](#info-pwr-18-minor) | Minor | Power |
| INFO | [SAMA-12](#info-sama-12-other-observations) | Other observations | SAMA7D65 SoC core |
| INFO | [DDR-11](#info-ddr-11-100-ck-termination-r17-deviates-from-the-microchip-reference-acceptable) | 100 Ω CK termination (R17) — deviates from the Microchip reference; acceptable | DDR3L memory |
| INFO | [DDR-12](#info-ddr-12-reset-pull-up-and-no-cke-pull-down-copied-from-the-microchip-reference-intentional) | RESET# pull-up and no CKE pull-down — copied from the Microchip reference, intentional | DDR3L memory |
| INFO | [DDR-13](#info-ddr-13-commercial-temperature-grade) | Commercial temperature grade | DDR3L memory |
| INFO | [DDR-14](#info-ddr-14-bootstrap-ddr-configuration-must-differ-from-the-curiosity-board) | Bootstrap DDR configuration must differ from the Curiosity board | DDR3L memory |
| INFO | [CON-15](#info-con-15-maya-w3-is-infineon-cyw55513-based-not-nxp-iw612) | MAYA-W3 is Infineon CYW55513-based, not NXP IW612 | Connectivity |
| INFO | [CON-16](#info-con-16-antenna-placement-versus-housing-needs-mechanical-verification) | Antenna placement versus housing (needs mechanical verification) | Connectivity |
| INFO | [CON-17](#info-con-17-housekeeping) | Housekeeping | Connectivity |
| INFO | [HAP-01](#info-hap-01-haptics-implementation) | Haptics implementation | Peripherals |
| INFO | [AUD-10](#info-aud-10-25-mm-balanced-pin-out-convention) | 2.5 mm balanced pin-out convention | Peripherals |
| INFO | [TP-04](#info-tp-04-touchpad-drc-items-scrtouchdrcrpt-real-or-not) | Touchpad DRC items (SCR/touch/drc.rpt): real or not | Peripherals |
| INFO | [LAY-15](#info-lay-15-courtyard-overlaps-involve-only-test-pads) | Courtyard overlaps involve only test pads | Layout, DRC & manufacturability |
| INFO | [LAY-16](#info-lay-16-bga-land-and-solder-mask) | BGA land and solder mask | Layout, DRC & manufacturability |
| INFO | [LAY-17](#info-lay-17-via-in-pad-on-qfn-thermal-pads-order-with-epoxy-fill-and-cap) | Via-in-pad on QFN thermal pads: order with epoxy fill and cap | Layout, DRC & manufacturability |
| INFO | [LAY-18](#info-lay-18-assembly-plan-notes) | Assembly plan notes | Layout, DRC & manufacturability |
| INFO | [LAY-19](#info-lay-19-touchpad-board-scrtouchdrcrpt-no-real-errors) | Touchpad board (SCR/touch/drc.rpt): no real errors | Layout, DRC & manufacturability |
| RESOLVED | [LAY-01](#resolved-lay-01-3v31v8-short-at-r35-and-the-5-1v8-unconnected-items-wifi-sdmmc-pull-ups-fixed-verified) | +3V3/+1V8 short at R35 and the 5 × +1V8 unconnected items (WiFi SDMMC pull-ups): fixed, verified | Layout, DRC & manufacturability |
| RESOLVED | [PWR-02](#resolved-pwr-02-nstrto-wkup0-pulled-to-a-divided-vsys-overdrives-a-vbat-domain-18-v-pin-and-drains-current-when-off) | nSTRTO → WKUP0 pulled to a divided VSYS: overdrives a VBAT-domain (1.8 V) pin and drains current when off | Power |
| RESOLVED | [SAMA-01](#resolved-sama-01-wkup0-vbat-domain-pulled-up-from-vsys-over-voltage-current-injection-into-vbat-and-possible-spurious-pmic-start) | WKUP0 (VBAT domain) pulled up from +VSYS: over-voltage, current injection into VBAT and possible spurious PMIC start | SAMA7D65 SoC core |
| RESOLVED | [AUD-01](#resolved-aud-01-headphone-jack-detect-det35mm-det25mm-never-gives-a-valid-logic-level) | Headphone jack detect (~DET_3.5mm / ~DET_2.5mm) never gives a valid logic level | Peripherals |
| RESOLVED | [TP-01](#resolved-tp-01-touchpad-electrode-assignment-7-rx-x-6-tx-exceeds-the-iqs7211es-21-cycle-limit) | Touchpad electrode assignment (7 Rx x 6 Tx) exceeds the IQS7211E's 21-cycle limit | Peripherals |
| RESOLVED | [PWR-04](#resolved-pwr-04-vbus-route-88-mm-of-08-mm-trace-on-15-m-inner-copper-in2-plus-20-mm-on-bcu) | VBUS route: ~88 mm of 0.8 mm trace on 15 µm inner copper (In2) plus ~20 mm on B.Cu | Power |
| RESOLVED | [CON-03](#resolved-con-03-vbus-path-88-mm-of-08-mm-trace-on-in2-15-m-cu-bq25640-defaults-will-push-about-2-a-through-it) | VBUS path: 88 mm of 0.8 mm trace on In2 (15 µm Cu); BQ25640 defaults will push about 2 A through it | Connectivity |
| RESOLVED | [LAY-04](#resolved-lay-04-vbus-path-is-108-mm-of-08-mm-track-mostly-on-05-oz-inner-copper) | VBUS path is 108 mm of 0.8 mm track, mostly on 0.5 oz inner copper | Layout, DRC & manufacturability |
| RESOLVED | [SAMA-03](#resolved-sama-03-vddout25-output-capacitance-exceeds-the-regulators-stable-range) | VDDOUT25 output capacitance exceeds the regulator's stable range | SAMA7D65 SoC core |
| RESOLVED | [DDR-01](#resolved-ddr-01-odt-net-is-not-length-matched-1813-mm-vs-4143-mm-addrctl-target-and-still-has-the-pre-jlc-0115-mm-width) | ODT net is not length-matched (18.13 mm vs 41–43 mm addr/ctl target) and still has the pre-JLC 0.115 mm width | DDR3L memory |
| ACCEPTED | [PWR-01](#accepted-pwr-01-battery-ts-pin-floating-no-thermistor-anywhere-charging-depends-on-software-and-has-no-temperature-protection) | Battery TS pin floating, no thermistor anywhere; charging depends on software and has no temperature protection | Power |
| ACCEPTED | [PWR-03](#accepted-pwr-03-charger-inductor-l2-dfe252012p-2r2m-undersized-and-at-the-top-of-the-allowed-l-range) | Charger inductor L2 (DFE252012P-2R2M) undersized and at the top of the allowed L range | Power |


---

# Power (charger, fuel gauge, PMIC, LDO)

Reviewed: the regenerated netlist, components_by_sheet, nets and drc (22 Nov 22:02), and meko.kicad_pcb as committed (21:50). This includes the owner's new BAT capacitor C123 and the WiFi 1V8 pull-up fix.

### Summary
- Most of the power architecture is sound. BQ25640 is the NVDC charger and USB-C DRP controller. MCP16502TAB (the same PMIC variant as the SAMA7D65-Curiosity) supplies 3V3, 1V35 DDR3L, 1V15 core and 1V15 CPU from VSYS. The pin numbering of the BQ25640 and MCP16502 symbols, and the BQ25640 footprint, match the datasheets.
- One HIGH issue:
  - **PWR-01:** TS is floating and there is no battery thermistor. There is no temperature protection, and default-mode charging likely depends on software setting TS_IGNORE.
- Main MEDIUM issues (cheap to fix before fab, but none stops the board working):
  - **PWR-02:** nSTRTO→WKUP0 is pulled to a divided VSYS. That puts about 3.5 V on a VBAT-domain pin (out of recommended conditions, inside absolute maximum) and drains about 0.37 mA while the device is off.
  - **PWR-03:** The charger inductor (2.2 µH, Isat about 2.6 A, Itemp 2.2 A) is over its ratings at the 2 A default charge current plus system load.
  - **PWR-04:** VBUS runs about 108 mm, mostly a 0.8 mm trace on thin inner copper, for roughly 140 mΩ. At 3 A that is about 1.3 W of trace loss.
  - The +1V8 rail (LDO2) is off by default in the AB variant, which breaks the recommended SAMA7D6 power-up sequence. Buck1 3V3 has little headroom for load (MAYA calibration peak 850 mA) and for low battery. The JST-GH current rating is below the default 2 A charge current.
- *Reviewer pass:* PWR-02, PWR-03 and PWR-04 were downgraded from HIGH to MEDIUM (PWR-04 now matches CON-03/LAY-04). PWR-16 was rewritten after the MAX17260 datasheet was retrieved: U5's connections are correct. No findings were removed.
- The new C123 (10 µF on BAT) meets the datasheet minimum and is well placed. Only a LOW DC-bias note remains (PWR-11).

### Findings

#### [ACCEPTED] PWR-01 Battery TS pin floating, no thermistor anywhere; charging depends on software and has no temperature protection
> **⚖️ Accepted by design (2026-11-27):** the owner chose to leave TS floating, with no thermistor and no fixed resistor network, and to handle the charger in software.
>
> **Required firmware settings (BQ25640, applied at every boot):**
>
> 1. `WATCHDOG = 00b`: disable the charger watchdog **first**. When it expires, the charger returns to default mode, ICHG is halved, other fields revert, and `TS_IGNORE` is reset (REG0x1B Table 7-25: reset by REG_RESET and WATCHDOG). With it left on, settings are lost whenever Linux is suspended or off for more than 160 s, and charging while off stops working.
> 2. `TS_IGNORE = 1` (REG0x1B bit 7): the charger treats TS as always good, so a floating TS is allowed (§7.3.6.4, p. 30).
> 3. `ICHG` ≈ 1.0–1.2 A: with about 1 A of system load this keeps the L2 current within its ~2.2 A rating (PWR-03), and it also suits the JST-GH battery connector (PWR-08).
> 4. Recommended: read the MAX17260 temperature (its TH pin is tied to BATT, so this is the internal die temperature: an approximation of the cell's temperature) and clear `EN_CHG` outside roughly 0–45 °C.
>
> **Notices / residual risks:**
>
> - **No hardware battery-temperature protection.** Cold charging (below 0 °C causes lithium plating) and hot charging are only guarded while Linux runs and checks the gauge. Accepted for a mostly-indoor device.
> - **Full charger reset** (battery unplugged, or drained below the charger's UVLO) restores the defaults: ICHG = 2 A, `TS_IGNORE = 0`, watchdog on. If the floating TS reads out of range, charging is suspended until Linux boots from USB power and re-applies the settings. If it reads in range, the charger charges at 2 A while the device is off; with no system load that is roughly within L2's rating (~2.15 A peak).
> - **Bring-up check:** confirm the board boots from USB with a flat or disconnected battery, since the system must start from VBUS alone to re-apply the settings. With D+/D− unconnected (CON-12) the input current limit may start low.
> - **Bring-up check:** confirm the charger keeps its registers, powered from the battery, while the SoC is off, so the settings persist across shutdowns.
>
> *Original severity: HIGH. The original finding is kept below for reference.*
**Where:** U4 pin 10 TS = `unconnected-(U4-TS-Pad10)`; U4 pin 7 NC/REGTS unconnected; BT1 is a 2-pin JST GH (no NTC wire); U5 TH (pin 1) tied to +BATT.
**Issue:**
- Nothing measures battery temperature: the charger TS pin floats and the fuel-gauge TH is strapped to BATT.
- The datasheet allows a floating TS only when TS_IGNORE = 1. TS_IGNORE resets to 0 at POR, on REG_RESET and on watchdog expiry. Watchdog expiry happens 40 s after the last host write by default, for example when Linux is suspended or crashed.
- With TS floating and TS_IGNORE = 0, the TS reading is undefined. The datasheet says "Charge suspends when TS pin voltage is out of range", so charging probably stops, or behaves randomly, until software writes TS_IGNORE again.
- This also means a dead device cannot charge while off: the PMIC stays off without a button press, so nothing sets TS_IGNORE.
- When charging does run with TS ignored, a Li-ion cell is charged at up to 2 A (the POR default ICHG) with no cold or hot cutoff. OTG boost also loses its temperature guard.

**Evidence:**
- BQ25640 SLVSIK1 §7.3.6.4: "The TS pin can be left floating if TS_IGNORE is set to 1b."
- Table 7-25 REG0x1B: TS_IGNORE reset 0h, "Reset by: REG_RESET, WATCHDOG".
- Table 5-1 TS: "Charge suspends when TS pin voltage is out of range. Recommend a 103AT-2 10kΩ thermistor."
- §7.6 / 7.3.6: WATCHDOG default 40 s; ICHG POR 2000 mA.
- What a floating TS actually reads is not specified, so the exact suspend behaviour **needs bench verification**.

**Recommendation:**
- Best option: use a 3-wire pack with a 103AT NTC, or put a 10 k 103AT NTC on the board in thermal contact with the cell (flex or glued). Bias it per Fig 7-6 with RT1 = 5.23 k from REGN and RT2 = 30.1 k to GND.
- At minimum, fit a fixed divider that reads TS_NORMAL from REGN, so default-mode charging works. Even then, the board still has no thermal protection.
- If TS_IGNORE stays the plan, the driver must set it on every probe, after every watchdog flag, and should set WATCHDOG = 00. Also enable the MAX17260 thermistor input as a software-level fallback.

> **Reviewer note:** Confirmed against SLVSIK1: §7.3.6.4 "The TS pin can be left floating if TS_IGNORE is set to 1b". REG0x1B bit 7 TS_IGNORE resets to 0 and is "Reset by: REG_RESET, WATCHDOG". WATCHDOG POR = 01b (40 s). ICHG POR = 2000 mA, halved on watchdog expiry (Table 7-9). HIGH stands. One correction: the "MAX17260 thermistor fallback" is not available as built. U5 TH (pin 1) is strapped to BATT, which the MAX17260 datasheet prescribes only "if not used". Without a hardware change the gauge can only report its internal die temperature (Config.TSel = 0), which is board temperature, not cell temperature.

#### [RESOLVED] PWR-02 nSTRTO → WKUP0 pulled to a divided VSYS: overdrives a VBAT-domain (1.8 V) pin and drains current when off
> **✅ Resolved (2026-11-27):** R58 was removed and R20 (now 100 k) goes from `~WKUP` to `+VBAT_SAMA` (the VBAT net), as on the Curiosity. Verified in the netlist (`/Power/~{WKUP}`: IC1.7 nSTRTO, R20 100 k, TP22, U1.A8 WKUP0). The important part was moving the pull-up to VBAT and removing R58. The 10 k → 100 k change is secondary: it cuts the current drawn from VBAT while nSTRTO pulls low (180 µA → 18 µA) and is still far stronger than WKUP0's leakage.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** `/Power/~{WKUP}`: IC1.7 nSTRTO, R20 10 k to +VSYS, R58 47 k to GND, U1.A8 WKUP0, TP22.
**Issue:**
- WKUP0 is powered from VBAT (SAMA7D65 pin table, ball A8, "VBAT"). VBAT is +1V8_BATT_CPU = MCP16502 LDO1 = 1.8 V (JP2 bridged 1-2).
- The divider makes the idle-high level 0.825·VSYS: 3.46 V at 4.2 V and up to about 3.8 V at 4.6 V. The pin allows at most VDD+0.3 = 2.1 V.
- **When on:** about 0.1–0.15 mA is injected through the WKUP0 clamp into the VBAT rail. LDO1 cannot sink current, so VBAT can be pulled above 1.8 V.
- **When off:** LDO1 is off and VBAT is about 0 V. About 0.35 mA flows continuously into the clamp, which is over the 0.2 mA recommended limit and may partly back-power VDDBU. The divider adds 74 µA from the battery all the time. Together that is roughly 10 mAh/day while the device is "off".

**Evidence:**
- SAMA7D6 DS60001851E Table 85.5: VIN ≤ VDD+0.3 V; IIN ±0.2 mA per pin.
- Pin table line "A8 … VBAT … WKUP0".
- MCP16502 DS20006275D §4.3.2: nSTRTO is open-drain and "typically has an external pull-up resistor".
- SAMA7D65-Curiosity UG DS50003806B Fig 3-5: nSTRTO (WKUP) pulled up with R23 100 k to **VBAT**.

**Recommendation:** Remove R58. Connect R20, changed to 100 k, to +1V8_BATT_CPU (the VBAT net) instead of +VSYS, as on the Curiosity.

> **Reviewer note:** Topology confirmed in the netlist: R20 10 k between /Power/~{WKUP} and +VSYS, R58 47 k between ~{WKUP} and GND, and the net is IC1.7, U1.A8 and TP22. The idle level is 0.825·VSYS. U1.A8 is on the VBAT rail (DS Table 8.1), and the Curiosity uses R23 100 k to VBAT. **Downgraded HIGH → MEDIUM:**
> - The level (2.5–3.8 V) is inside the absolute maximum (DS Table 85.2: inputs −0.3 to 4.0 V, injected current ±1 mA). It only violates the *recommended* VIN ≤ VDD+0.3 V and the ±0.2 mA injection limit (Table 85.5).
> - When on, the injected current simply lifts VBAT to about 3 V, which is still inside the VBAT range (≤ 3.6 V). Nothing malfunctions.
> - When off, LDO1's active discharge (LDO1-CFG default 0xA0, DISCH = 1, 25 Ω) holds VBAT near 0 V. The cost is therefore a standing drain of about (4.2 − 0.5 V)/10 k ≈ 0.37 mA ≈ 9 mAh/day. That total already includes the divider current, so the 74 µA should not be added on top.
>
> This is still worth fixing before fab because the fix costs nothing.

#### [ACCEPTED] PWR-03 Charger inductor L2 (DFE252012P-2R2M) undersized and at the top of the allowed L range
> **⚖️ Accepted by design (2026-11-27):** L2 stays DFE252012P-2R2M (the same part as L1 and L3–L5, as recommended in MCP16502 Table 5-1; 2.2 µH is inside the BQ25640's 0.68–2.2 µH range). The current is limited in software instead.
>
> **Why the limit is needed:** the BQ25640 is a power-path charger, so L2 carries charge current plus system load. At 5 V in and 3.7 V on the battery, ripple = V_IN·D·(1−D)/(f_s·L) ≈ 0.29 A (§8.2.2.1 eq. 4, f_s = 1.5 MHz). At the 2 A power-on default with the device running (0.5–1 A load), the average is 2.5–3 A and the peak 2.65–3.15 A, over I_temp (2.2 A) and I_sat (~2.6 A). With the device off it is ~2.0 A average and ~2.15 A peak, just within rating.
>
> **Mitigation:** set ICHG to about 1.0–1.2 A with the charger watchdog disabled (see PWR-01 for the full firmware list). The 2 A power-on default only returns after a full charger reset, and then usually with the device off (no system load).
>
> **If revisited:** a 1 µH, I_sat ≥ 4 A, DCR ≤ 30 mΩ inductor gives ~0.64 A of ripple, inside TI's 20–40 % recommendation. TI characterised the chip with Murata DFE322520F-1R0M=P2 (1210 footprint; rating to confirm).
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** L2 between /Power/SW and +VSYS.
**Issue:**
- DFE252012P-2R2M=P2 is rated Isat ≈ 2.6 A, Itemp 2.2 A, DCR 84 mΩ max. MCP16502 Table 5-1 lists it at 2.2 A; distributors list 2.6 A.
- Inductor current is the charge current plus the system load:
  - Default ICHG of 2 A plus about 0.5–1 A of system load gives 2.5–3 A average, plus about 0.3 A ripple (calculated at 1.5 MHz, 2.2 µH, 5 V to 3.8 V).
  - With a 3 A USB-C source, IINDPM can reach 3–3.2 A. That gives up to about 4 A of inductor current at 3.8 V SYS.
- That is above Isat, so the inductor saturates and overheats. The BQ25640 is a 5 A charger.
- The datasheet allows LSW of 0.68–2.2 µH, so 2.2 µH is the maximum, and the reference design uses 1 µH.

**Evidence:**
- BQ25640 §6.3: LSW 0.68–2.2 µH, ISW up to 5 A, IVBUS 3.2 A.
- Simplified application on p.1 shows 1 µH.
- Register table: ICHG POR = 2000 mA.

**Recommendation:**
- Fit a 1 µH (or 1.5 µH) inductor with Isat ≥ 5 A and a low-loss metal core. A 2520 or 3225 part works, for example the DFE252012F-1R0M (check its rating) or a 3.2×2.5 mm 1 µH part with Isat 5 A or more.
- Otherwise, cap ICHG at 1 A or less and IINDPM at 1.5 A or less in software, permanently. Note this cap is lost on watchdog reset unless the watchdog is disabled.

> **Reviewer note:** The ratings are confirmed:
> - MCP16502 Table 5-1 lists DFE252012P-2R2M=P2 as "2.2 µH, 2.2A, 84 mΩ Max". Murata/distributor data gives Isat about 2.6 A (−30 % L), Itemp 2.2 A max (+40 °C).
> - BQ25640 §6.3 gives LSW 0.68–2.2 µH. §8.2.2.1 requires ISAT ≥ ICHG + ½·IRIPPLE.
> - The datasheet characterisation inductor is the 1 µH Murata DFE322520F-1R0M=P2 (3.2 × 2.5 mm) on p.1 and in the Typical Characteristics conditions. Prefer that part (confirm its Murata rating) over the unverified DFE252012F-1R0M. Note it needs a 1210/3225 footprint.
>
> **Downgraded HIGH → MEDIUM:** a metal-alloy inductor saturates softly. Above its rating the result is extra heat (about 0.4–0.6 W at 2.5–3 A) and more ripple, not a hard failure. The stress also only occurs once software has put the charger in host mode with ICHG ≥ about 1.5 A on a 3 A source: in default mode the floating TS (PWR-01) probably suspends charging anyway. PWR-08 already requires ICHG ≤ 1 A for the connector. Swapping the inductor before fab is still the clean fix.

#### [RESOLVED] PWR-04 VBUS route: ~88 mm of 0.8 mm trace on 15 µm inner copper (In2) plus ~20 mm on B.Cu
> **✅ Resolved (2026-11-27):** VBUS now goes J3 → 6 vias → a copper pour on In2 ("VBUS PWR", 336 mm², narrowest point 1.7 mm near y ≈ 168.7 mm) → 3 vias at TP47 → a 1.25 mm B.Cu trace (~20 mm) → 3 vias → U4. Resistance calculated from the saved zone fill (inner copper 15.2 µm, outer 35 µm): pour ≈ 21 mΩ (2-D solve on the actual pour shape), 1.25 mm trace ≈ 8 mΩ, connector stubs ≈ 2–3 mΩ, vias ≈ 1–2 mΩ, so **≈ 33 mΩ total, against ≈ 140 mΩ before**. That is about 65 mV / 0.13 W at 2 A and 0.1 V / 0.3 W at 3 A. **Minor:** each transition has 3 × 0.3/0.15 mm vias, about 1 A per via at 3 A; a fourth via per transition adds margin. Widen the 1.7 mm neck if convenient. Refill zones before generating gerbers.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** VBUS from J3 (≈190, 194) to U4.2 (170.4, 136.3).
- In2.Cu: 0.8 mm wide, 87.9 mm long.
- B.Cu: 0.8 mm wide, 20.3 mm long; plus 0.6 mm wide, 7.6 mm long.
- 4 × 0.45/0.225 vias at the U4 end.

**Issue:**
- The stackup's inner copper is 0.0152 mm thick. Track resistance works out to about 124 mΩ on In2 plus about 12 mΩ on B.Cu, so ≈ 0.14 Ω plus vias.
- At 3 A (USB-C high, the default IINDPM after CC detection) that is about 0.42 V of drop and about 1.3 W in the trace. A 0.8 mm half-ounce inner trace at 3 A heats up far more than the usual 10–20 °C design limit.
- At 1.5 A it is still about 0.2 V and 0.3 W.
- The VBUS drop pushes the charger into VINDPM early, and the long path adds hot-plug ringing.

**Evidence:**
- Geometry measured from meko.kicad_pcb with SCR/tools/pwr_an.py and pwr_path.py.
- Stackup is taken from the board file (In2 thickness 0.0152).
- BQ25640 §7.3.3.3: IINDPM follows the Type-C advertisement, up to 3 A.

**Recommendation:** Pour VBUS as a wide polygon of 3 mm or more on In2, or use outer layers with stitching vias. Add more vias at both ends (at least 4 × 0.3 mm drill). Otherwise, cap IINDPM at about 1.5 A in software and accept slower charging.

> **Reviewer note:** I recomputed the resistance: ρL/(w·t) = 1.72e-8 × 87.9 mm / (0.8 mm × 15.2 µm) = 0.124 Ω on In2, plus about 0.019 Ω on B.Cu, for about 0.14 Ω in total. That confirms the numbers above. **Downgraded HIGH → MEDIUM** to match the duplicates CON-03 and LAY-04. The consequence is heat, plus VINDPM folding the input current back, so charging is slower. Nothing fails outright, and a software cap on IINDPM is a full workaround.

#### [MEDIUM] PWR-05 +1V8 (LDO2) is OFF at power-up in the AB variant, so periphery supplies come up after VDDCORE
> **Update (2026-11-27):** see the update under SAMA-02. Probably less severe than stated, and merging the rails or linking them with a resistor is not recommended.
**Where:** IC1.21 LOUT2 → +1V8. It feeds:
- U1 VDDIOP1 (C17), VDDSDMMC2 (F13) and VDDQSPI0 (P19);
- the MAYA-W386 1V8 VIO;
- pull-ups R33–R37.

**Issue:**
- In the MCP16502AB, LDO2 is disabled in every power mode and is not in the start-up sequence. Software must enable it over I²C after Linux boots.
- The SAMA7D6 datasheet requires the whole periphery group to be established before the core group (t2 ≥ 0 ms). Here VDDIOP1, VDDSDMMC2 and VDDQSPI0 come up seconds after VDDCORE/VDDCPU. The datasheet warns that operating outside this "may lead to unpredictable behavior".
- The signals on these banks today (PD1, PD2, PD14–PD16 WL/BT wake and enable, SDIO2) are only used after Linux boots, so functionally it probably works. It is still out of spec, and the BT and WL control pins are undriven during boot.

**Evidence:**
- MCP16502 Table 4-15 (AB column): LDO2-A/LPM/HIB/HPM = 0x37 (EN bit 7 = 0); LDO2-SEQ = 0x01. Table 4-1: VLOUT2 "Off" for AB.
- SAMA7D6 §85.5.1 and Fig 85.2 / Table 85.11.
- The Curiosity puts all of these rails on 3.3 V and leaves LDO2 "OFF / free use" (UG Fig 3-5).

**Recommendation:** Power +1V8 from LDO1, which is in the start-up sequence at 1.8 V with SELVL1 low. Two options:
- Keep VBAT on LDO1 as well. VBAT draws µA, and LDO1 is rated 300 mA.
- Move VBAT to +3V3 (JP2 position 2-3, the datasheet's "tie VBAT to VDDIN33" option) and use LDO2 for nothing, or for later loads.

In both cases, make sure the LDO1 hibernate state is enabled in software if hibernate or backup self-refresh is wanted (see PWR-15).

> **Reviewer note:** Confirmed against MCP16502 Table 4-1 (AB: VLOUT2 "Off") and Table 4-15 (AB column: LDO2-A/LPM/HIB/HPM = 0x37, so bit 7 EN = 0). In DS60001851E §85.5.1, Fig. 85.2 is titled "*Recommended* Power Sequence", so MEDIUM (out of spec, works in practice) is the right severity.

#### [MEDIUM] PWR-06 3V3 and 3V3_AVDD fall out of regulation at low battery
**Where:**
- IC1 Buck1: VSYS → +3V3. In battery-only mode VSYS ≈ VBAT, because the BATFET is fully on and VSYSMIN applies only when VBUS is present.
- U3 TPS7A2033: VSYS → +3V3_AVDD.

**Issue:**
- At 100 % duty, Buck1's output is VBAT − I·(RDSon_P 160 mΩ max + DCR 84 mΩ). At 0.8 A and VBAT = 3.3 V that is about 3.1 V.
- VDDIN33 and VDDUTMII need at least 3.0 V. The journal plans a software cut-off at 3.2 V and says "MPU works down to 3V", which leaves almost no margin with WiFi peaks.
- TPS7A2033 needs VIN ≥ 3.3 V + VDO, so AVDD tracks VSYS below about 3.35 V. That degrades the 120 dB codec performance.

**Evidence:**
- MCP16502 electrical table: RDSonP 140/160 mΩ, DMAX 100 %.
- SAMA7D6 Table 85.4: VDDIN33 3.0–3.6 V.
- TPS7A20 VDO: 145 mV max at 300 mA.

**Recommendation:** Put the shutdown threshold at 3.45–3.5 V under load, using MAX17260 VCell or AvgVCell. Alternatively, use a buck-boost for 3V3.

#### [MEDIUM] PWR-07 Buck1 (+3V3, 1 A rated) load budget is tight
**Where:** +3V3 loads:
- SAMA7 I/O and VDDIN33 (about 40 mW);
- MAYA-W386 3V3: 480 mA peak in TX, **850 mA peak during firmware init or calibration**;
- 2 × µSD cards: 100–200 mA each when writing;
- DRV2605L VDD (U7.6/U7.10 on +3V3): LRA drive peaks of a few hundred mA;
- TAC5212 IOVDD, IQS7211E, display.

**Issue:** The peak sum can exceed the 1 A rating. Cycle-by-cycle ILIM_HS is 1.2 A minimum, and hiccup protection could then reset the whole system (nRSTO).
**Evidence:** MAYA-W3 datasheet R05 Table 27 ("Maximum peak current … Firmware initialization / self-calibration 850 mA"); MCP16502: "All Buck channels can support loads up to 1A", ILIM_HSx 1.2/1.8/2.4 A.
**Recommendation:**
- Move DRV2605L VDD to +VSYS; it accepts 2.0–5.2 V.
- Consider a separate small buck from VSYS for the MAYA 3V3, or at least a load switch with soft start.
- Do not run WiFi calibration while SD writes are in progress.

#### [MEDIUM] PWR-08 Battery connector JST-GH 2-pin current rating vs charge and discharge current; no reverse-polarity protection
**Where:** BT1 SM02B-GHS-TB; the +BATT path is a 0.8 mm B.Cu track to 2 × 0.3 mm-drill vias to the F.Cu zone to U4.14; BT1− goes through 4 × 0.15 mm vias to R29.
**Issue:**
- The JST GH series is rated about 1 A per contact with AWG26 wire (from JST GH catalogue memory, **needs verification**). The default charge current is 2 A.
- Discharge peaks reach about 1–1.5 A: SoC, WiFi TX, haptics, plus OTG output to earbuds (5 V × 0.5–1 A from the battery ≈ 0.8–1.5 A).
- Nothing protects against a reversed pack. Third-party JST-GH packs often come with swapped wire order. BQ25640 BAT has an absolute minimum of −0.3 V, so a reversed pack damages U4, U5 and IC1.
- The journal says the pack has a PCM with a 2.4 V cut-off, so the cell does have basic over-discharge and over-current protection.

**Recommendation:**
- Program ICHG to 1 A or less, or to the cell's 0.5–1C if lower, and set it again after every watchdog reset.
- Otherwise choose a connector rated for 3 A (for example a JST-PH 2 A or Molex Pico-Lock 3 A) or solder pads.
- Confirm the pack polarity against the silkscreen. A reverse-polarity P-FET is optional.

> **Reviewer note:** The 1 A rating matches JST's GH catalogue ("1 A AC/DC, AWG #26"), so the "needs verification" caveat can be dropped. A reversed pack drives +BATT to about −3.7 V, which is beyond the MAX17260 BATT absolute minimum of −0.3 V as well as the BQ25640's.

#### [LOW] PWR-09 Charger defaults and OTG need software; legacy chargers are limited to 500 mA
**Issue:**
- The POR defaults are VREG 4.2 V, ICHG 2 A, VSYSMIN 3.52 V, CC_MODE = SNK-only and WATCHDOG 40 s. On watchdog expiry ICHG is halved and TS_IGNORE is reset.
- USB OTG to earbuds (README) only works after the host sets CC_MODE = 10b (DRP) and RP_VALUE, or SRC with CC_AUTO_OTG. In ship or shutdown mode the device is always SNK-only (dead-battery mode).
- BQ D+/D− are left open, as TI E2E suggested. A legacy USB-A DCP charger is therefore detected as "unknown" or default and gets IINDPM = 500 mA until software overrides it.

**Evidence:** BQ25640 §7.3.3.2–7.3.3.5, §7.3.3.1, §7.5 watchdog.
**Recommendation:** Write a driver init sequence that sets VREG, ICHG ≤ 1 A, IINDPM ≤ 1.5 A (see PWR-03/04), TS handling, CC_MODE and the watchdog policy. For legacy adapters, optionally connect BQ D+/D− in parallel with the USB D+/D− lines; TI does this in several reference designs.

#### [LOW] PWR-10 PMID capacitor: 10 µF 0402, 6.3 V
**Where:** C89 CL05A106MQ5NUNC on Net-(U4-PMID).
**Issue:**
- The datasheet asks for "10µF in parallel with 0.1µF" (CPMID ≥ 10 µF without derating). The nominal value meets that.
- At 5 V DC bias, a 6.3 V 0402 X5R part keeps only about 2–3 µF.
- The 6.3 V rating leaves no headroom for:
  - OTG VOTG settings above 5 V (range 3.84–9.6 V);
  - HVDCP if it is ever enabled;
  - hot-plug ringing on VBUS. PMID follows VBUS through the RBFET body diode.

**Recommendation:** Use 10 µF 0603 25 V (X5R) plus 100 nF.

#### [LOW] PWR-11 New BAT capacitor C123: meets the datasheet, small DC-bias caveat (re-check of owner's fix)
**Where:** C123 10 µF CL05A106MQ5NUNC 0402 on +BATT, at (170.98, 132.06). Pad 1 sits in the +BATT F.Cu zone between the BAT vias and U4.14, about 2.3 mm from the BAT pin. Pad 2 connects to GND through a 0.6 mm F.Cu stub and a GND via at (171.40, 132.25).
**Check:**
- BQ25640 Table 5-1 says "Connect a 10µF ceramic capacitor closely to the BAT pin and GND", and §6.3 says CBAT ≥ 10 µF without derating. Both are **satisfied**. Placement and the GND return are good.
- C102 (100 nF) stays as the MAX17260 BATT bypass.

**Remaining note:** A 6.3 V 0402 part at 3.0–4.2 V keeps only about 3–4 µF. That meets the letter of the spec. A 10 µF 0603 10 V part (for example CL10A106KP8NNNC) would give about 2× more effective capacitance for BAT-side transients when the battery is removed or the PCM trips.

#### [LOW] PWR-12 Few thermal vias under U4
**Where:** U4 thermal pad 23 (0.4 × 1.55 mm) has 2 × 0.3/0.15 mm GND vias. There is one more GND via near pin 18.
**Issue:** TI recommends thermal-pad vias to the ground planes. At 2 A charge the loss is about 0.3–0.5 W, and the pad is narrow. Most heat leaves through the PGND pins 5/18 and the SW/SYS copper.
**Recommendation:** Add GND vias next to PGND pins 5 and 18 and spread the GND copper on F.Cu around U4. IC1 by contrast has 9 × 0.225 mm vias in its EP, which is good.

#### [LOW] PWR-13 C126 (100 nF on nSTRT) makes the PMIC auto-start whenever VSYS ramps from 0
**Where:** /Buttons/PWR: IC1.24 nSTRT, C126 100 n to GND, R56 10 k to SW1.
**Issue:** The internal 40 k pull-up and 100 nF give τ ≈ 4 ms, longer than t1 (about 0.6 ms). This is exactly the "nSTRT capacitor for automatic turn-on" from MCP16502 §5.7. The device therefore boots by itself when:
- a battery is connected at assembly;
- the pack PCM recovers;
- VBUS is plugged in with a dead or absent battery.

**Recommendation:** If this is intended (boot to a charging screen), keep it. If not, reduce C126 to 1–10 nF for debounce only.

#### [LOW] PWR-14 U3 (TPS7A2033) is always enabled from VSYS
**Where:** U3.3 EN to +VSYS.
**Issue:** +3V3_AVDD (TAC5212 AVDD) stays on while the system is off. This costs the LDO Iq plus the codec AVDD standby current, and the codec sees AVDD without IOVDD.
**Recommendation:** Drive EN from +3V3 or from a GPIO.

#### [LOW] PWR-15 VBAT supplied by LDO1 (1.8 V) instead of a backup element or VDDIN33
**Where:** JP2 (bridged 1-2) connects /SAMA7/VBAT to +1V8_BATT_CPU (IC1 LOUT1, SELVL1 = R30 10 k to GND → 1.8 V).
**Issue / notes:**
- (a) The SAMA7D6 datasheet says that without a storage element, VBAT must be tied to VDDIN33. LDO1 starts in the same sequence step as Buck1, which satisfies t0 ≤ 0.2 ms, and matches MCP16502 Fig 4-1 "without backup supply". So it works, but it differs from the Curiosity, which uses VBAT = VDDIN33 or a coin cell.
- (b) The default LDO1-HIB register is 0x19 (EN = 0), so LDO1 turns off in Hibernate. For hibernate with DDR self-refresh, software must set LDO1-HIB EN (register 0x52 bit 7). Otherwise SHDN and LPM lose their supply and the PMIC falls to OFF.
- (c) SHDN and LPM are VBAT-domain outputs, so their high level is 1.8 V against the MCP16502 VIH minimum of 1.5 V. That is only 0.3 V of margin.
- (d) The RTC is lost whenever the PMIC is fully off. That is acceptable given the design intent.

#### [LOW] PWR-16 MAX17260 (U5) connections verified against the datasheet; CSN should be a Kelvin trace to R29
**Where:** U5 MAX17260SETD+ (TDFN-14), R29 10 mΩ low-side between BT1− (Net-(BT1--)) and GND, C102 100 nF on BATT, C105 470 nF on REG, R28 10 k ALRT pull-up.
**Check (MAX17260 data sheet Rev 1 6/18, Pin Configurations and Pin Descriptions, p.11–12):**

| Pin | Name | Netlist | Datasheet requirement | Result |
|---|---|---|---|---|
| 1 | TH | +BATT | "Connect to BATT if not used" | OK, but no cell thermistor (see PWR-01) |
| 2–5 | NC | open | No connection | OK |
| 6 | BATT | +BATT, C102 100 nF | "Bypass with a 0.1μF capacitor" | OK |
| 7 | CSN | GND | Low-side: "Kelvin connect to the system side of the sense resistor" | OK electrically; see layout note |
| 8 | GND | GND | IC ground (system side) | OK |
| 9 | CSPL | BT1− (cell side of R29) | "Kelvin connect to the cell side of the sense resistor" | OK |
| 10 | CSPH | +BATT | Low-side: "tie to the BATT pin" | OK |
| 11 | REG | C105 470 nF | "Bypass with an external 0.47μF capacitor" | OK (6.3 V 0201 at 1.8 V) |
| 12 | ALRT | FUEL_INT, R28 10 k to +3V3 | Open-drain, abs max 17 V | OK |
| 13/14 | SDA/SCL | shared I²C | internal pull-downs | OK |
| EP | EP | GND | — | OK |

- The symbol pin numbers match the TDFN pinout exactly. The CSPH/CSPL names are the datasheet's own.
- R29 at 10 mΩ gives ±5.12 A range and 156.25 µA resolution (Table 9, recommended for capacities > 400 mAh). The datasheet allows 1–1000 mΩ.
- CSPL's absolute maximum is ±0.3 V versus GND. At 10 mΩ that is only reached at 30 A, so it is fine.

**Issue (layout, minor):** CSN goes to U5's GND/EP vias, not to a dedicated Kelvin trace on the system-side pad of R29. Any ground current between R29 and U5's vias becomes a current-measurement offset.
**Recommendation:** Route CSN as its own trace to R29 pin 2, per the datasheet's Figure 3 "Low-Side Current Measurement Layout Guide". Alternatively, accept a small offset; the gauge's offset/learning algorithms tolerate it.
**Other notes:**
- Because TH is tied to BATT, the gauge can only use its internal die sensor (TSel = 0), and TH-based battery-removal detection is unavailable.

> **Reviewer note:** This entry replaces the earlier "Needs verification" placeholder. The datasheet was retrieved from a mirror (https://www.rlocman.ru/i/File/2018/07/11/MAX17260.pdf, because analog.com timed out) and saved to SCR/datasheets/max17260_ds/max17260.pdf (.txt). No connection error was found.

#### [INFO] PWR-17 MCP16502 power-stage layout
- Each buck's PVIN cap (C96, C99, C101, C104; 4.7 µF) sits next to its PVIN pin on an F.Cu VSYS island with 4 × 0.15 mm vias down to the In2 VSYS pour.
- Each cap's GND returns through one 0.225 mm via to In1, which is 76 µm below. The PGND pins reach the EP through F.Cu 0.6 mm straps and 9 EP vias.
- Each SW node is a small F.Cu zone of about 3.8 mm², and each inductor sits about 2 mm from its pin. The output caps (C94, C98, C100, C103; 22 µF 0603) are beside the inductors.
- This is acceptable. A direct F.Cu GND connection from each PVIN cap to the adjacent PGND pin would shrink the hot loop further.
- BQ25640: C89 (PMID) is about 1.7 mm from PMID with its GND via next to PGND pin 5. C95 BTST and C97 REGN are adjacent. The SW zone is 8.9 mm². This is good.

#### [INFO] PWR-18 Minor
- TP26 has value "HPM" but sits on Net-(BT1--); the label is wrong.
- DRC reports courtyard overlaps of BT1 with TP26 and with TP67.
- The +3V3 In2 pour is named "VSYS_3", which is confusing.
- The earlier DRC conflict between +1V8 vias and the +3V3 In2 pour near R33/R34/R37 is **gone** in the regenerated DRC (the WiFi pull-up fix).

### Power budget (estimate, battery-side)
| Rail | Source | Typ load | Peak | Limit |
|---|---|---|---|---|
| VDDCPU 1.15–1.25 V | Buck4 | 0.15–0.26 A (1 GHz CoreMark 0.2–0.33 W, DS Table 85.74) | ~0.35 A | 1 A |
| VDDCORE 1.15 V | Buck3 | 0.1–0.15 A (+GPU/LCDC) | ~0.4 A | 1 A |
| VDDIODDR 1.35 V | Buck2 | SoC PHY 20 mW + MT41K256M16 ~0.1–0.2 A | ~0.3 A | 1 A |
| +3V3 | Buck1 | 0.2–0.4 A | **>1 A possible** (MAYA 850 mA cal + SD + haptics) | 1 A (ILIM 1.2 A min) |
| +1V8 | LDO2 | <30 mA | ~50 mA | 300 mA |
| VBAT | LDO1 | µA | – | 300 mA |
| 3V3_AVDD | U3 | ~10–30 mA | – | 200 mA |

- Typical draw is about 1.5–2 W, roughly 0.5 A from a 3.7 V cell.
- Peak is about 4 W (about 1.1 A), plus up to about 1.5 A more while sourcing OTG to earbuds.
- Charging defaults to 2 A, plus system load through L2.

### Design rationale
- **Charger (BQ25640):** chosen for its integrated USB-C CC logic with DRP and Try.SNK/SRC (no separate TCPC), its NVDC power path (instant-on with a dead battery), OTG boost for powering earbuds, 26 V-tolerant VBUS/CC (so plain ESD441 diodes are enough), and ship mode.
  - BATP gets the datasheet's 100 Ω series resistor (R25), Kelvin-tapped at the BT1 pad (a good layout choice that the journal credits to the KiCad Discord).
  - QON is brought out to JP3 so ship mode can be exited manually.
  - PG drives a white charge LED from VSYS (R24 1.5 k, about 1 mA, within the 6 mA PG sink limit).
  - D+/D− are left open per a TI E2E answer.
  - I²C address 0x6B does not clash with the other parts on the bus: MCP16502 0x5B, MAX17260 0x36, DRV2605L 0x5A.
- **Fuel gauge (MAX17260):** a separate gauge was chosen because no single chip offered path, charger and gauge together (journal). It uses low-side 10 mΩ sensing, with REG 470 nF and ALRT as an interrupt to PD31.
- **PMIC (MCP16502TAB):** the Microchip-recommended PMIC for SAMA7 parts that need DVS. The AB variant is the "SAMA7G5 with DDRx" option and is the same part number fitted on the SAMA7D65-Curiosity (UG DS50003806B §3.1.2).
  - Its defaults match the SoC: 3V3, 1.35 V DDR3L (SELV2 floating = High-Z → 1.35 V, Table 4-4), VDDCORE 1.15 V and VDDCPU 1.15 V. Both core rails are inside 1.03–1.21 V; the Linux Curiosity DTS later trims core to 1.05 V. VDDCPU goes to 1.25 V for 1 GHz via HPM or I²C, which is within the 1.22–1.30 V requirement.
  - LDO1 is strapped to 1.8 V by R30 to GND, a "Low" input with ≤1 µA leakage.
  - PWRHLD comes from SHDN and HPM from PC11, each through 1 k, identical to the Curiosity. LPM comes from the SoC LPM pin. nRSTO drives NRST and the JTAG reset. nINTO goes to PC12 with a 10 k pull-up.
  - Inductors are 2.2 µH; the datasheet's slope compensation covers 1.5–2.2 µH and it is characterised at 2.2 µH. DFE252012P-2R2M is listed in MCP16502 Table 5-1, and the Curiosity uses the 1.5 µH sibling.
  - Each output has 22 µF 0603 (the stability minimum) and each PVIN 4.7 µF 0402 (as recommended). These match Table 5-1 part families.
  - Running the PMIC from VSYS (2.7–5.5 V input) instead of 5 V is fine.
- **VBAT on LDO1:** implements the journal's idea of a "free LDO as an always-on backup supply" for hibernate with DDR in self-refresh. It needs the register fixes in PWR-05 and PWR-15.
- **TPS7A2033:** a low-noise 3.3 V LDO from VSYS so the TAC5212 analog supply is not on a switcher.

### Verified OK
- **BQ25640 symbol:** pins 1–22 and thermal pad 23 match SLVSIK1 Table 5-1, including CC1/VBUS/PMID/SW/PGND/BTST/NC-REGTS/INT/PG/TS/CE/BATP/SYS/BAT/SDA/SCL/QON/PGND/REGN/D−/D+/CC2.
- **BQ25640 footprint VDL0023A-MFG:** pad order counter-clockwise, 0.45 mm pitch on the 5-pin sides and 0.4 mm on the 6-pin sides, thermal pad 0.4 × 1.55 mm offset 0.225 mm. Consistent with the land-pattern drawing.
- **MCP16502 symbol:** pins 1–32 plus EP match DS20006275D Table 3-1.
- **TPS7A2033 DBV:** pinout IN 1 / GND 2 / EN 3 / NC 4 / OUT 5 is correct; Cin and Cout are 1 µF.
- **Charger passives:** C88 1 µF on VBUS; BTST 47 nF (25 V); REGN 4.7 µF 10 V; SYS has 22 + 10 µF near the charger, above 20 µF nominal; INT 10 k; SDA/SCL 10 k; PG pull-up via LED and 1.5 k; CE floating is allowed (internal pull-down enables charging); QON has an internal pull-up.
- **BAT capacitor (new C123):** 10 µF at the BAT pin, meeting the datasheet minimum.
- **MCP16502 logic and decoupling:**
  - SVIN decoupled by C91 10 µF, above the 1 µF minimum.
  - LVIN by C106 4.7 µF, above 2.2 µF.
  - LOUT1 and LOUT2 have 4.7 µF each, within 2.2/4.7–20 µF.
  - PVIN = SVIN = LVIN, all on the same net.
  - Logic levels: nSTRT is pulled to 0.2·SVIN when the button is pressed, below VIL of 0.36·SVIN. PWRHLD, LPM and HPM see 1.8 V or 3.3 V, above VIH 1.5 V and below the 6 V absolute maximum.
- **Output rail capacitance:** 22 µF nominal on each buck output, plus SoC decoupling. Effective DDR capacitance is about 25 µF, and effective 3V3 capacitance is about 35 µF, well within the hiccup Cadd limits for the default soft-start.
- **I²C pull-ups:** to +3V3. The always-powered BQ and MAX17260 are open-drain, so there is no back-powering when 3V3 is off.
- **VSYS distribution:** 3 × 0.3 mm vias from the charger to the In2 VSYS pour (91 mm²), then 4 vias per PVIN island.
- **Thermal vias:** IC1 EP has 9 thermal vias.

### Datasheets used
- BQ25640 (SLVSIK1, Mar 2026): https://www.ti.com/lit/ds/symlink/bq25640.pdf → SCR/datasheets/bq25640/bq25640.pdf (.txt)
- MCP16502 (DS20006275D): https://ww1.microchip.com/downloads/aemDocuments/documents/APID/ProductDocuments/DataSheets/MCP16502-Data-Sheet-DS20006275.pdf → SCR/datasheets/mcp16502/
- SAMA7D6 Series data sheet DS60001851E: SCR/datasheets/SAMA7D65/ds.txt (fetched by the SAMA agent)
- SAMA7D65-Curiosity user guide (EV63J76A, DS50003806B): https://www.newark.com/site/binaries/content/assets/common/product-family-documents/microchip-ev63j76a/microchip-ev63j76a-ug-1.pdf → SCR/datasheets/sama7d65-curiosity-ug/
- Linux DTS at91-sama7d65_curiosity.dts (regulator settings): SCR/datasheets/linux-dts/
- TPS7A20: https://www.ti.com/lit/ds/symlink/tps7a20.pdf → SCR/datasheets/tps7a20/
- MAYA-W3 data sheet R05: SCR/datasheets/MAYA-W3/maya_ds.txt (power consumption, Table 27)
- ESD441 VRWM ±5.5 V (TI SLVSH26B, via search)
- Murata DFE252012P-2R2M ratings: MCP16502 Table 5-1 (2.2 A, 84 mΩ) and distributor data (Isat 2.6 A)
- MAX17260 (Maxim Rev 1, 6/18): analog.com timed out; retrieved by the reviewer from https://www.rlocman.ru/i/File/2018/07/11/MAX17260.pdf → SCR/datasheets/max17260_ds/max17260.pdf (.txt). Used for the pin-level checks in PWR-16.
- Tools: SCR/tools/pwr_pcb.py, pwr_an.py, pwr_path.py, dbg.py (PCB parsing and route measurement)

---

# SAMA7D65 SoC core

### Summary
The custom symbol and footprint are correct. All 343 balls in the netlist and in `sama7d65_343.kicad_sym` match `pinout_table.html`, with 0 mismatches. The HTML table matches the PDF pin table (DS60001851E Table 8.1). The footprint has 343 pads on the A–AA × 1–21 grid at 0.65 mm pitch, with no missing or extra balls. All rail assignments match the datasheet: VDDOUT25 feeds VDDANA, VDDIN25, VDDDPHY and ADVREFP; VDDIN33 and VDDUTMII share one source; TST is grounded. Every peripheral pin uses a valid mux function with a consistent I/O set and the correct bank voltage. The boot SD is on SDMMC1 IOSET1, which is the ROM default, and the default ROM/SAM-BA console (FLEXCOM6 IOSET4) is on J1.

The main problems are in the backup/power-control domain and in decoupling (no HIGH items remain after the reviewer pass):
- **WKUP0 voltage:** WKUP0 is in the VBAT (1.8 V) domain but is pulled up from +VSYS through a divider (SAMA-01, MEDIUM).
- **+1V8 rail is off at power-up:** the +1V8 rail (MCP16502AB LDO2) is OFF by default, which breaks the SoC power-up sequence (SAMA-02).
- **VDDOUT25 capacitance:** the output capacitance is above the stable range (SAMA-03).
- **Bulk decoupling:** bulk capacitors are missing near the SoC (SAMA-04).

*Reviewer pass:*
- SAMA-01 was downgraded HIGH → MEDIUM to match PWR-02.
- SAMA-07 was downgraded MEDIUM → LOW to match PWR-15.
- SAMA-11's "0.0892 mm below JLC minimum" claim was removed as a false positive: 0.0892 mm is 3.51 mil, which meets JLC's 3.5 mil (0.0889 mm) minimum.
- No findings were removed.

### Findings

#### [RESOLVED] SAMA-01 WKUP0 (VBAT domain) pulled up from +VSYS: over-voltage, current injection into VBAT and possible spurious PMIC start
> **✅ Resolved (2026-11-27):** see PWR-02. WKUP0 is now pulled up with 100 k to `+VBAT_SAMA`, and R58 is removed.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** U1.A8 WKUP0, net /Power/~{WKUP}: R20 10 k to +VSYS, R58 47 k to GND, IC1.7 nSTRTO, TP22. VBAT is set by JP2 (default 1-2) to +1V8_BATT_CPU, which is MCP16502 LDO1.

**Issue:** WKUP0 is supplied by the VBAT rail. Here VBAT is 1.8 V, or 0 V when the PMIC is fully off. The divider puts 0.825 × VSYS on the pin, which is about 2.5–3.5 V for a 3.0–4.2 V battery, and above 3.6 V if VSYS goes above ~4.37 V.
- **Out of spec:** the datasheet allows VIN ≤ VDD + 0.3 V (2.1 V here) and recommends ≤ ±0.2 mA DC injection.
- **Clamp current:** the pin has a clamp diode to VBAT (Abs-max note: "All I/O pins are internally clamped to their respective VDD"). The source impedance is 8.25 kΩ (10 k ∥ 47 k), so ~0.1–0.4 mA flows into the VBAT node.
- **VBAT rises:** that node is fed only by LDO1, which can only source current, plus C5 and C107, and the VBAT domain draws only µA. VBAT will therefore drift above 1.8 V during normal operation.
- **Phantom power when off:** with the PMIC fully OFF (LDO1 off), VSYS can raise VBAT through WKUP0 above the VBAT POR threshold (1.40–1.60 V). SHDN then goes high, which raises PWRHLD. The MCP16502 starts on a PWRHLD low-to-high transition even without nSTRT (MCP16502 DS §4.3.7 item 2). The likely result is unwanted power-ups at battery insertion or after shutdown, and an RTC/backup domain that is never cleanly reset.
- **Standing drain:** the divider draws ~74 µA from the battery at all times.

**Evidence:**
- Netlist: `R20: pin1 /Power/~{WKUP}, pin2 +VSYS`; `R58: GND – /Power/~{WKUP}`; `U1.A8(WKUP0_A8)`.
- pinout_table/DS Table 8.1: WKUP0 is on rail VBAT, as are SHDN, LPM, JTAGSEL, XIN32 and TST.
- DS60001851E Table 85.5 (p.3796): VIN ≤ VDD+0.3, IIN ≤ ±0.2 mA. Table 85.49 (p.3834): VBAT POR thresholds.
- MCP16502 DS20006275D p.3 application schematic: nSTRTO→WKUP0 is pulled up to the VBAT/backup supply. Fig. 4-1: PWRHLD (= SHDN) "is set to '1' as soon as VBAT is above its internal POR threshold".

**Recommendation:** Pull nSTRTO/WKUP0 up to the VBAT net (/SAMA7/VBAT, after JP2), for example 100 k, and remove R58. The pull-up must never be sourced from VSYS or +3V3 while VBAT can be lower than that rail.

> **Reviewer note:** The R20/R58 topology and the VBAT-rail assignment of A8 are confirmed. **Downgraded HIGH → MEDIUM**, consistent with PWR-02:
> - 2.5–3.8 V is within the absolute maximum (Table 85.2: −0.3 to 4.0 V, ±1 mA injection). Only Table 85.5's recommended conditions are violated.
> - While on, the injection lifts VBAT to about 3 V, which is still inside VBAT's ≤ 3.6 V range, so there is no malfunction.
> - The "phantom power" bullet is unlikely. LDO1-CFG defaults to 0xA0 (DISCH = 1), so LDO1's 25 Ω active discharge holds VBAT near 0 V while the PMIC is off, and the clamp current cannot raise VBAT to its POR threshold. Unwanted starts at battery insertion are caused by C126 on nSTRT instead (PWR-13).
> - The real cost is about 0.37 mA of off-state drain.

#### [MEDIUM] SAMA-02 +1V8 rail (MCP16502AB LDO2) is OFF by default, so VDDIOP1, VDDQSPI0 and VDDSDMMC2 power up after the core
> **Update (2026-11-27):** this is probably less severe than first stated. Nothing on +1V8 is in the boot path: the OS SD card is on SDMMC1, a 3.3 V bank. Everything that could drive those pins (the SDIO pull-ups R33–R37 and the MAYA's 1.8 V I/O supply) is on +1V8 itself, so it is off whenever the banks are off. Still to confirm: that the DS60001851E power-up section allows a VDDIOx bank to come up after VDDCORE, or that the Curiosity board does the same. **Not recommended as fixes:** (a) merging +1V8 with +1V8_BATT_CPU: two LDOs on one net, all 1.8 V loads kept on in backup, WiFi I/O powered without its 3.3 V, and switching noise on the VBAT/RTC domain; (b) a 100 k resistor between the rails, which would leave the banks half-powered. If early 1.8 V really is required, use a PMIC variant with LDO2 on at power-up, or a small always-on 1.8 V LDO from +3V3.
**Where:** +1V8 = IC1.21 LOUT2. It feeds U1.C17 VDDIOP1, U1.P19 VDDQSPI0, U1.F13 VDDSDMMC2 and the MAYA 1V8 supply.

**Issue:** In the AB variant VLOUT2 is "Off" by default: LDO2-A = 0x37 (not enabled), and LDO2 is not in the start-up sequence. These three I/O banks therefore stay unpowered until U-Boot or Linux enables LDO2 over I2C, long after VDDCORE/VDDCPU are up and NRST is released. The datasheet requires all periphery-group supplies to be established before the core group (t2 ≥ 0) and says "Operating the device outside this scope may lead to unpredictable behavior".
- **Pins affected:** the BT UART/I2S pins (PB8–PB18), the WiFi SDIO pins (PC27–PD0) and the wake/enable GPIOs (PD1–PD16) sit on unpowered banks during boot.
- **Software dependency:** the WiFi/BT path depends on an I2C enable before the pins can be used.

**Evidence:** MCP16502 Table 4-1 (p.18): AB has VLOUT2 = Off. Table 4-15 (p.66-67): LDO2-A = 0x37, LDO2-SEQ = 0x01; compare LDO1, which is enabled (0x99/0xA7/0xB7, SEQ 0x09). DS60001851E §85.5.1, Fig. 85.2 and Table 85.11 (p.3798-3799).

**Recommendation:** Generate +1V8 for the SoC banks with a small LDO from +3V3 (or VSYS) that is enabled together with Buck1, and keep LOUT2 for the module if wanted. Otherwise, document a "Needs verification" bring-up test of boot with the banks unpowered.

> **Reviewer note:** Confirmed against MCP16502 Table 4-1 (AB: VLOUT2 "Off") and Table 4-15 (LDO2-A = 0x37, so EN bit 7 = 0). DS §85.5.1 calls Fig. 85.2 the *recommended* sequence, so MEDIUM is right. PWR-05 proposes a simpler alternative: move +1V8 to LDO1, which is in the start-up sequence.

#### [RESOLVED] SAMA-03 VDDOUT25 output capacitance exceeds the regulator's stable range
> **✅ Resolved (2026-11-27):** C54 is now 1 µF (Samsung CL05A105KO5NNNC, 0402 16 V X5R, LCSC C29266). +2V5 therefore has 1 µF + 6 × 100 nF = 1.6 µF nominal, about 1.3 µF after DC-bias derating at 2.5 V. That is inside the VDDOUT25 regulator's 1–2.7 µF stable range, with margin on both sides.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** +2V5 net. C54 is 4.7 µF (CL05A475KP5NRNC, 0402 X5R 10 V), plus C56, C58, C60, C61, C62 and C63 at 6 × 100 nF. Total: 5.3 µF nominal.

**Issue:** The internal VDDOUT25 LDO is specified as stable only for COUT = 1–2.7 µF (ESR 0.01–0.3 Ω). Even after DC-bias derating at 2.5 V, the 4.7 µF 0402 is about 2.5–3 µF, so the total is about 3.1–3.6 µF, above the maximum. Microchip's SAMA7D65 Hardware Design Considerations specifies 2.2 µF on VDDOUT25. Instability would affect the PLLs, the main oscillator, the ADC and VDDANA.

**Evidence:** DS60001851E Table 85.45 (p.3832): COUT 1 µF min, 2.7 µF max; also ADVREFP needs CADVREFP ≥ 1 µF (Table 85.61). Microchip "SAMA7D65 Hardware Design Considerations" §2.3.1: "A 2.2 µF X7R (or X5R) ceramic capacitor should also be placed close to the VDDOUT25 power output pin".

**Recommendation:** Change C54 to 1 µF (X5R/X7R). With the six 100 nF capacitors, the effective total is about 1.4–1.6 µF, which is within range and still meets CADVREFP ≥ 1 µF. Alternatively, use 2.2 µF and remove three or four of the 100 nF capacitors. Keep the capacitors close to E3.

> **Reviewer note:** Confirmed: Table 85.45 gives COUT 1 µF min / 2.7 µF max and ESR 0.01–0.3 Ω, and the netlist has +2V5 = C54 4.7 µF + 6 × 100 nF. Microchip's own Curiosity (UG DS50003806B, SoC power page) uses C66 2.2 µF 0402 + 100 nF caps on VDDOUT25/VDDIN25/VDDANA/VDDDPHY/ADVREFP, about 2.7 µF nominal. Simplest fix: change C54 to 2.2 µF 0402 X5R to match the reference.

#### [MEDIUM] SAMA-04 Bulk decoupling near the SoC is below the datasheet minimum and Microchip guidance (VDDIN33, VDDUTMII, VDDIODDR, VDDCORE)
**Where:** The +3V3 balls (G7 VDDIN33, L3 VDDUTMI and others) have only 100 nF capacitors near U1. The nearest ≥ 1 µF capacitor on +3V3 is C110 (1 µF) at 14.5 mm from G7, and the nearest ≥ 2.2 µF is C119/C94 at 22–30 mm. +1V35_DDR has no ≥ 1 µF capacitor within 25 mm of U1 (C67 and C98 are at about 25 mm). VDDCORE has a single C8 4.7 µF.

**Issue:**
- The datasheet makes CIN ≥ 2.2 µF "between VDDIN33 and the device's closest GND pin" a minimum requirement for the VDDOUT25 regulator. That regulator has up to 100 mA inrush, and VDDIN33 has a 1 % ripple limit.
- Microchip's hardware guidance adds 4.7 µF on VDDCPU, VDDUTMI, VDDIN33 and VDDIODDR close to the MPU, and 2 × 4.7 µF on VDDCORE.
- In addition, G7, F9 and L3 reach the +3V3 supply through 0.3 mm In2.Cu tracks rather than vias into the plane, because the In2 area under the BGA is split between other rails.

**Evidence:** DS Table 85.45 note 4 (p.3832–3833). Table 85.1 (p.3793): VDDIN33/VDDUTMII ripple ≤ 1 %. Microchip SAMA7D65 Hardware Design Considerations §2.3.1. Layout: positions from pos.csv; U1 is on B.Cu at (196.36, 168.39).

**Recommendation:** On the top side under or near the BGA, add one 4.7 µF 0402 on +3V3 next to G7/L3, one on +1V35_DDR, and a second 4.7 µF on VDDCORE.

> **Reviewer note:** Confirmed from pos.csv. The nearest ≥ 1 µF parts are C110 1 µF at about 18 mm from U1's centre on +3V3, and C67/C98 at about 25 mm on +1V35_DDR. The Curiosity places C63 4.7 µF directly at VDDIN33/VDDUTMI. DDR-08 (LOW) covers the DRAM side of the same topic. Treat the VDDIODDR part as covered here.

#### [MEDIUM] SAMA-05 24 MHz crystal drive-level rating is probably below the SAMA7D65 oscillator's requirement (Needs verification)
**Where:** Y1, TKD SX32Y024000BC1T001 (LCSC C7420736), C3/C4 = 20 pF.

**Issue:** For 20–30 MHz crystals (Set 2), the SAMA7D65 requires a crystal drive-level rating PON ≥ 300 µW: "Applications that do not respect this criterion may damage the crystal". The TKD M3225 series datasheet gives 100 µW (typ) and no maximum. The other Set 2 parameters are OK:

| Parameter | Datasheet limit (Set 2) | Y1 |
|---|---|---|
| CL | 6–12.5 pF | 12 pF (LCSC listing) |
| ESR | ≤ 100 Ω | 40 Ω (≤ 60 Ω max) |
| C0 | ≤ 3 pF | 3 pF max |

**Evidence:** DS Table 85.56 (p.3837) and §85.8.10. TKD M3225 datasheet (LCSC C7420736).

**Recommendation:** Ask TKD for the maximum drive level, or pick a 24 MHz 3225 crystal with CL = 12 pF and a ≥ 300 µW rating, for example an NDK or Abracon part specified at 300 µW (Needs verification). The load capacitor calculation itself is correct (see Rationale).

> **Reviewer note:** The requirement is confirmed (Table 85.56 Set 2: PON ≥ 300 µW, CL 6–12.5 pF, ESR ≤ 100 Ω, C0 ≤ 3 pF). The TKD M3225 sheet gives only "100 µW (typ)", with no maximum. CM (1.3–3.2 fF required) is also not specified by TKD. The Curiosity sidesteps the issue with a DSC6001 MEMS oscillator (Y3, DSC6001HI1B-024.0000T) in bypass mode. A 24 MHz 1.8–3.3 V MEMS/XO is therefore an alternative fix. Severity stays MEDIUM / Needs verification.

#### [MEDIUM] SAMA-06 SDMMC2_CAL and QSPI0_CAL use the 3.3 V calibration resistor value on 1.8 V banks
**Where:** R10 16k9 on /SAMA7/SD2_CAL (VDDSDMMC2 = +1V8). R11 16k9 on /SAMA7/QSPI0_CAL (VDDQSPI0 = +1V8).

**Issue:** RZQ must be 20 kΩ for 1.8 V I/O and 16.9 kΩ for 3.3 V. With 16.9 kΩ, the HSIO driver impedance is calibrated about 15 % low.
- **SDMMC2:** this matters for the WiFi SDIO link at 1.8 V in SDR50/SDR104, which is where calibration is required.
- **QSPI0:** the bank is used only for UART, I2S and GPIO, so the impact there is negligible (effectively LOW).

**Evidence:** DS §85.6.4.1 and §85.6.4.2 (p.3811–3812): "a 20 KΩ RZQ resistor for 1.8V memories and a 16.9 KΩ resistor for 3.3V memories".

**Recommendation:** Change R10 and R11 to 20 kΩ 1 %. R8 and R9 (SDMMC0/1 at 3.3 V) at 16k9 are correct.

> **Reviewer note:** Confirmed: DS §85.6.4.1/§85.6.4.2 say "20 KΩ RZQ resistor for 1.8V memories and a 16.9 KΩ resistor for 3.3V memories". R10 and R11 are 16k9 (RC-01W1692FT), and VDDSDMMC2/VDDQSPI0 are on +1V8. MEDIUM is kept for SDMMC2 to stay consistent with the duplicate CON-02. The R11/QSPI0 part alone would be LOW.

#### [LOW] SAMA-07 VBAT is fed from PMIC LDO1 instead of VDDIN33 or a storage element: sequencing and hibernate depend on I2C setup (Needs verification)
**Where:** JP2 VBATSEL, default 1-2: /SAMA7/VBAT = +1V8_BATT_CPU (IC1 LOUT1), with C5 100 nF. The alternative position is +3V3.

**Issue:**
- The datasheet says that without a storage element "VBAT must be tied to VDDIN33", and that VBAT must be established within t0 ≤ 0.2 ms of VDDIN33.
- LDO1 and Buck1 start in the same sequencer slot (both SEQ = 0x09), so t0 is probably met. LDO1-HIB defaults to off, however, so backup and hibernate with DDR self-refresh only work after software has reprogrammed LDO1-HIB.
- Any PMIC reset or UVLO, or a full OFF, removes VBAT. The RTC/GPBR and the 32 kHz oscillator are lost and the SHDWC restarts cold. The logic levels are fine: SHDN/LPM at 1.8 V against MCP16502 VIH = 1.5 V min.
- This finding interacts with SAMA-01.

**Evidence:** DS §85.5.1 (p.3798): VBAT bullets and Table 85.11 t0. MCP16502 Table 4-15: LDO1-SEQ 0x09 = OUT1-SEQ 0x09; LDO1-HIB 0x19/0x27/0x37 (not enabled).

**Recommendation:** Measure the VBAT/VDDIN33 ramp on first boot. Confirm that the U-Boot or Linux PMIC driver sets the LDO1-HIB enable before using backup mode. If hibernate is not essential, the datasheet-compliant choice is JP2 = 2-3 (VBAT = +3V3). Consider a small supercap or coin cell if RTC retention is desired.

> **Reviewer note:** **Downgraded MEDIUM → LOW** to match the duplicate PWR-15. LDO1-SEQ = OUT1-SEQ = 0x09, so VBAT and VDDIN33 rise in the same sequencer slot, and 1.8 V is inside VBAT's operating range. Functionally this behaves like "VBAT tied to VDDIN33", which also loses the backup domain whenever the PMIC is off. The only real action is software (the LDO1-HIB enable).

#### [LOW] SAMA-08 Debug/SAM-BA UART header J1 has no GND pin
**Where:** J1 is a 1×2 header: pin 1 is UART_SAMBA_RX (SoC PD18 TXD) and pin 2 is UART_SAMBA_TX (SoC PD19 RXD).

**Issue:** There is no ground or VTref pin, so the USB-UART adapter ground has to be taken from J2 pin 3/5 or a test point. The net names follow the adapter's point of view, per the sheet note.

**Recommendation:** Use a 1×3 header (GND, RX, TX), or document the use of J2 GND. Silkscreen "SoC TX/RX".

#### [LOW] SAMA-09 Possible MCLK driver contention between SoC I2SMCC0_MCK and MAYA PCM_MCLK
**Where:** /SAMA7/BT.MCLK: U1.N21 (PB18, I2SMCC0_MCK, output) ↔ IC2.E8 PCM_MCLK.

**Issue:** On MAYA-W3, PCM_MCLK is an optional clock output ("PCM clock output signal (optional)", I2S_CCLK). If both sides enable it, two outputs fight.

**Recommendation:** In the device tree, mux only one side as the driver (for example, leave PB18 as a GPIO input), or add a 0 Ω/DNP link.

#### [LOW] SAMA-10 Copper routed under the crystals
**Where:**
- **Y2 (SC-32S, B.Cu):** /SAMA7/JTAGSEL on B.Cu and /Power/~{WKUP} on F.Cu run underneath. +1V8 and /SAMA7/VBAT run on In2 under it.
- **Y1 (F.Cu):** /Power/~{WKUP} runs under it on F.Cu and B.Cu, with a via inside the body outline. /Power/LPM and XOUT32 run under it on B.Cu.

**Issue:** Seiko requires "no pattern under SC-32S". The 32 kHz oscillator is extremely high-impedance (RF = 6 MΩ). The signals are mostly static, so the risk is low.

**Recommendation:** Reroute JTAGSEL and WKUP away from under Y2/Y1. Keep only GND under the crystals and their traces.

#### [LOW] SAMA-11 BGA fanout DFM details
- **Duplicate via:** two identical GND vias sit at (199.1207, 167.9305) inside the BGA (DRC `holes_co_located`), which causes a double drill hit. Delete one.
- ~~Track width~~ *(removed by reviewer: the 0.0892 mm segments are 3.51 mil, which meets JLC's 3.5 mil (0.0889 mm) multilayer minimum. LAY reports it as compliant, and it is the deliberate 90/100 Ω diff-pair width.)*

> **Reviewer note:** The duplicate GND via is also reported as LAY-07.

#### [INFO] SAMA-12 Other observations
- **Display SPI:** FLEXCOM3 IOSET2 is valid: PA24 IO0 = MOSI, PA22 IO2 = SPCK, PA21 IO3 = NPCS0. Sharp SCS is active-high, so use `cs-gpios` with `spi-cs-high`.
- **USB VBUS:** no VBUS-sense GPIO goes to the SoC. Device-mode attach detection must come from the BQ25640 (CHG_INT/I2C). The SoC's internal TCPC CC pins (PB31, PC0) are unused, and CC is handled by the BQ25640. That is acceptable.
- **SD card speed:** both SD slots have fixed 3.3 V I/O (VDDSDMMC0/1 = +3V3, 1V8SEL unconnected), so there is no UHS-I. Expect up to 25 MB/s (High Speed).
- **CPU frequency:** VDDCPU defaults to 1.15 V (MCP16502AB OUT4), which allows 800 MHz (≥ 1.12 V). 1 GHz needs 1.22–1.30 V via DVS/HPM, and for -E parts only up to TJ = 105 °C.
- **ERC:** the `power_pin_not_driven` warning on U1.E8 VBAT is cosmetic, caused by the jumper.
- **Unused pins:** MIPI_REXT is left unconnected while D-PHY is unused. The datasheet gives no requirement, so this is acceptable.
- **Ordering code:** the -SL3 suffix is a software-license level and has no hardware impact.

### Design rationale
- **Symbol and footprint:** the symbol was generated from Microchip's online pin table (`html_to_csv.py` → KiCad symbol generator) and then split into units. The footprint comes from the designer's fork of kicad-footprint-generator.
  - It has 0.30 mm NSMD pads with 0.05 mm mask expansion (0.40 mm opening).
  - Microchip's recommended land is ≤ 0.40 mm, and the package itself is 0.35 mm SAC105 balls on 0.30 mm SMD substrate openings.
  - This gives a 0.25 mm mask web and lets 0.1 mm tracks pass between balls.
- **Power tree (Microchip Fig. 9.2 / MCP16502AB reference):**

  | Supply | Rail | Feeds |
  |---|---|---|
  | Buck1 | 3.3 V | VDDIN33 and VDDUTMII from one source (required); also VDDIOP0, VDDGMAC0/1, VDDSDMMC0/1 and VDDLVDS |
  | Buck2 | 1.35 V | VDDIODDR (DDR3L) |
  | Buck3 | 1.15 V | VDDCORE |
  | Buck4 | 1.15 V, DVS via HPM | VDDCPU |
  | LDO1 | 1.8 V | VBAT, so the backup domain can stay alive in PMIC Hibernate with DDR in self-refresh (journal) |
  | LDO2 | 1.8 V | VDDIOP1, VDDQSPI0, VDDSDMMC2 (the 1.8 V I/O banks) plus the MAYA module, avoiding level shifters to the 1.8 V-only module |

  The internal VDDOUT25 (2.5 V) feeds VDDANA, VDDIN25, VDDDPHY and ADVREFP. The datasheet mandates this for VDDANA, VDDIN25 and VDDDPHY, and ADVREFP's 2.4–2.55 V range matches.
- **PMIC handshake:** SHDN→PWRHLD, LPM→LPM, NRST←nRSTO, WKUP0←nSTRTO, PC11→HPM and PC12←nINTO, exactly as in DS Fig. 9.2. The 1 k series resistors on PWRHLD and HPM limit current while either side is unpowered.
- **Decoupling:** one 100 nF 0201 per supply ball, placed on F.Cu directly under the bottom-side BGA (lateral distance ≤ 1 mm from each ball; 14/5/15/8/3/6 capacitors for CORE/CPU/DDR/3V3/1V8/2V5). There is a 4.7 µF 0402 per rail (CORE, CPU, 1V8, 2V5). This follows the "100 nF 0201 X7S + 4.7 µF 0402 X5R" choice of the Curiosity board.
- **Crystals:** CLEXT = 2 × (CL − Cpara − Cpcb/2) from DS Fig. 85.44/85.45.
  - 24 MHz: CL = 12 pF, Cpara = 1 pF, Cpcb = 1 pF, giving 21 pF → 20 pF C0G.
  - 32.768 kHz SC-32S: CL = 7 pF, Cpara32k = 2 pF, giving 9 pF (GJM 9.0 pF).
  - Both calculations are noted on the sheet and are correct. Y2's ESR is 70 kΩ (< 90 kΩ) and its drive limit is 1 µW (≥ 0.2 µW min).
- **Boot:** there are no boot straps. With an empty OTP Boot Configuration Packet, the ROM boots only from SDMMC1 IOSET1, so the internal "OS" microSD is wired exactly there (PB22–PB27, CD = PB29). If that fails, the ROM falls back to SAM-BA over USB port A (wired to the USB-C via the ECMF filter) and FLEXCOM6 IOSET4 UART (J1).
- **JTAG/debug:** JTAGSEL low selects ICE/SWD debug. JP1 defaults to GND, and the internal pull-down is a backup. JP1 can select boundary scan (high, VBAT-domain 1.8 V). There are 100 k pull-ups on TCK/TMS/TDI, NTRST goes to a test point (internal PU), and J2 pin 10 resets NRST.
- **I/O voltage matching:**
  - The 3.3 V peripherals (TAC5212 IOVDD, PMIC/charger/fuel-gauge/DRV2605 I2C, touchpad, LCD, SD cards, buttons) are on 3.3 V banks: VDDIN33, VDDIOP0, VDDGMAC0/1, VDDLVDS, VDDSDMMC0/1.
  - The MAYA-W386 (1.8 V VIO) signals are on 1.8 V banks: VDDSDMMC2 (SDIO), VDDQSPI0 (FLEXCOM2 UART and I2SMCC0 PCM), VDDIOP1 (wake/enable).
- **CAL resistors:** SDMMCx_CAL/QSPI0_CAL set the HSIO impedance calibration (16.9 k for 3.3 V, 20 k for 1.8 V). HHSRTUNE uses 5.62 k 1 % with 10 pF DNP (C2 9 p DNP), as in DS Fig. 84. DDR ZQ uses 240 Ω 1 %.

### Verified OK
- **Symbol and footprint:**
  - Netlist U1 ball→function: 343/343 balls match `pinout_table.html`, 0 mismatches.
  - Library `.kicad_sym`: 343/343 match, including alternates, and power pins are typed as power.
  - The HTML table matches the PDF Table 8.1 for 297 balls sampled automatically, with no real differences (only footnote formatting).
  - Footprint: 343 pads, positions exactly (col−11)×0.65 by (row−10)×0.65, row letters skip I/O/Q/S/X/Z per Microchip, and the pad set equals the table's ball set. The PCB instance matches the library (no `lib_footprint_mismatch` for U1).
- **Power pin to rail:** VDDCORE ×14 → +1V15_CORE; VDDCPU ×5 → +1V15_CPU; VDDIODDR ×15 → +1V35_DDR (DDR3L 1.283–1.45 V); VDDIN33, VDDUTMI, VDDSDMMC0/1, VDDIOP0, VDDGMAC0/1 and VDDLVDS → +3V3; VDDIOP1, VDDQSPI0, VDDSDMMC2 → +1V8; VDDANA ×2, VDDIN25, VDDDPHY, ADVREFP → VDDOUT25 (+2V5); TST → GND; all GND/GNDANA/GNDIN33/GNDUTMI/GNDBAT/GNDDPHY → GND (single plane, within the ±50 mV requirement).
- **Pin mux, I/O sets and bank voltages:**
  - SDMMC0 IOSET1 + CD on PA16 (3.3 V); SDMMC1 IOSET1 + CD on PB29 (3.3 V); SDMMC2 IOSET1 (1.8 V).
  - FLEXCOM0 IOSET2 I2C (PC7 SDA, PC6 SCL); FLEXCOM5 IOSET2 I2C (PE3 SDA, PE2 SCL).
  - FLEXCOM2 IOSET2 USART with hardware flow control (PB9 TXD→module RX, PB8 RXD←module TX, PB12 CTS←module RTSn, PB10 RTS→module CTSn); MAYA pin directions checked against its datasheet.
  - FLEXCOM3 IOSET2 SPI; FLEXCOM6 IOSET4 console; I2SMCC1 IOSET1 to TAC5212 (DOUT0→DIN, DIN0←DOUT); I2SMCC0 IOSET3 to MAYA PCM.
  - The ROM boot interface and default console match DS Table 21.14/21.15 and §21.6.2.2.
- **Pull-ups:** NRST, PMIC nINTO, CHG_INT, FUEL_INT, TOUCH_INT and SD CD are pulled up to +3V3 on 3.3 V banks. MAYA wake lines have 10 k pull-downs on the 1.8 V bank. DISP has a 10 k pull-down, which keeps the LCD off during boot.
- **Crystals:** load capacitor maths for both crystals; Y1 pinout (1/3 crystal, 2/4 GND); Y2 ESR, C0 and drive level; short XIN/XOUT traces (2.4/4.6 mm).
- **USB:** HHSRTUNE 5.62 k 1 %.
- **Placement and fanout:**
  - VBAT 100 nF placed 0.8 mm from E8.
  - Every connected BGA ball has a track or via; there is no via-in-pad, so POFV is not needed.
  - 174 vias of 0.30/0.15 mm, tented on both sides, inside the BGA.
  - Each power ball has its own via: CORE 14/14, CPU 5/5, DDR 15/15 and 2V5 6/6 to In2 planes, and 76 GND vias for 60 GND balls into In1/In3/In4.
  - The ball-to-via copper gap is about 0.16 mm.

### Datasheets used
- **Microchip SAMA7D6 Series Data Sheet DS60001851E:** https://ww1.microchip.com/downloads/aemDocuments/documents/MPU32/ProductDocuments/DataSheets/SAMA7D6-Series-Data-Sheet-DS60001851.pdf. Local: SCR/datasheets/SAMA7D65/ds.pdf (.txt). Sections used: Table 8.1, §9, §21, Ch. 85, Ch. 86.
- **Microchip "SAMA7D65 Hardware Design Considerations" §2.3.1 Requirements:** https://onlinedocs.microchip.com/oxy/GUID-DD32B9DD-5FB2-4D96-AC34-EF93C0B81615-en-US-1/GUID-4BECE6C4-DFD5-4A11-B2CE-060C3E4CB8E2.html (web only).
- **SAMA7D65 Curiosity / Curiosity Pro schematic index (not reviewed in full):** https://onlinedocs.microchip.com/oxy/GUID-04251033-8A3B-42A9-858E-7FF210E96175-en-US-1/GUID-87B014A1-0E1B-4812-BCE6-489DEA935705.html
- **Project pin table:** `hardware/pcb_lib/SAMA7D65-4HB/pinout_table.html` (parsed into SCR/sama7/pinout.json).
- **MCP16502 DS20006275D:** SCR/datasheets/mcp16502/mcp16502.txt (fetched by another agent).
- **TKD M3225 (SX32Y024000BC1T001):** https://www.lcsc.com/datasheet/C7420736.pdf, with the LCSC product page for CL/ESR. Local: SCR/datasheets/xtal_TKD_SX32Y024/
- **Seiko SC-32S:** https://www.lcsc.com/datasheet/C97604.pdf. Local: SCR/datasheets/xtal_SC32S/
- **u-blox MAYA-W3:** SCR/datasheets/MAYA-W3/maya_ds.txt (pin directions).
- **BQ25640:** SCR/datasheets/bq25640/bq25640.txt (VSYS behaviour).
- **Analysis scripts:** SCR/tools/sama7/ (`parse_pinout.py`, `cmp.py`, `fp.py`, `bga.py`, `pwr.py`, `trace.py`).

---

# DDR3L memory

Scope: U2 MT41K256M16TW-107:P (Micron 4 Gb DDR3L x16, 96-ball 8x14 mm "TW" package, LCSC C253882 confirmed as this MPN) connected point-to-point to U1 SAMA7D65 UDDRC/DDR3PHY. Supporting parts: R15/R16/C64/C66/C129/C130/C1 (VREF), R19 + R3 (ZQ), R17 (CK termination), R18 (RESET#), C67/C69/C71–C87 (DRAM decoupling), C15…C52/C128 (SoC VDDIODDR decoupling), +1V35_DDR from MCP16502AB Buck2 (IC1 OUT2, L3, C98).

Scripts (all read-only, in SCR/tools): `sexp.py` (s-expr parser), `ddr_lengths.py` (per-net length = tracks + arcs + via barrel from stackup z), `ddr_refcheck.py` (reference plane / return vias), `ddr_xtalk.py` (parallel-run coupling), `fd_impedance.py` (2-D finite-difference Laplace solver, validated against Hammerstad–Jensen and converged to <0.3 %). Outputs in SCR/ddr_out/ (`ddr_lengths.txt/json`, `impedance.txt`). My lengths agree with KiCad DRC to ≤0.07 mm (ODT 18.134 vs 18.1337, A3 40.744 vs 40.7494, DQS0+ 42.508 vs 42.500).

### Summary

- Schematic is correct: every DQ/DQS/DM/A/BA/CK/CKE/ODT/CS#/RAS#/CAS#/WE#/RESET# connection checked ball by ball against the SAMA7D65 pin table and Micron Figure 7. DQ swaps stay inside their byte lane, and DQS/DM stay with their lane. Address/BA are not swapped. ZQ is 240 Ω 1 % on both sides. VREF uses the 1k/1k 1 % divider plus 100 nF from Microchip DS Fig. 85.11. The footprint matches the Micron TW package drawing.
- Main layout problem: **ODT is 18.1 mm long, against 41–43 mm for every other addr/ctl net (DDR-01, MEDIUM).** Its meanders were lost in commit 754fa86 "redid addr and clk". It also kept the old PCBWay 0.115 mm width. It arrives about 140 ps early relative to CK. It probably still works at 533 MHz, but it uses up a large part of the timing margin and breaks the design's own rules.
- The other DRC skew/length items are harmless or come from how the rules are written. The DQS-vs-CK "≈3 mm skew" comes from the diff-pair skew rule grouping all pairs together and from the R17 stub being counted in CK's length. The ±2.3 mm addr/ctl spread is about 13 ps. The 44 + 12 "DDR clearance" violations are short same-group escape runs (≤0.7 mm coupled at <0.15 mm).
- Impedance is acceptable. The project stackup has the thicknesses of JLC06081H-1080 but not JLC's Dk values. With JLC's Dk and solder mask, 0.1072 mm single-ended is about 52 Ω and 0.0892/0.185 mm differential is about 107 Ω. Both are within ±10 %. All DDR routing stays on F.Cu/B.Cu over solid In1/In4 GND, with no void crossings.
- Reviewer pass: DDR-01 length and width re-measured and confirmed; DDR-08 cross-referenced to SAMA-04. No findings were removed and no severities were changed.
- Minor items: thin bulk decoupling, VREF routed next to DQ11, a stale impedance/length fab note, the DRAM footprint library missing from fp-lib-table, and A15 not routed (no 8 Gb upgrade path).

### Findings

#### [RESOLVED] DDR-01 ODT net is not length-matched (18.13 mm vs 41–43 mm addr/ctl target) and still has the pre-JLC 0.115 mm width
> **✅ Resolved (2026-11-27):** ODT has been re-meandered: it is now **41.46 mm** on B.Cu at **0.1072 mm** (the JLC 50 Ω width) along its whole length, inside the 41–43 mm addr/ctl window, so it lines up with CK and the other command signals again. KiCad DRC no longer reports any length or skew violation on `/DDR/ODT`. The remaining addr/ctl skew items are the pre-existing ~2.0 mm spread covered by DDR-03.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** /DDR/ODT, U1.W1 (DDR_ODT) → U2.K1 (ODT), all on B.Cu, no vias, from about (195.4,160.1) to (199.8,149.3). Net class DDR_ADDR_CTL.
**Issue:** ODT measures 18.134 mm. All other addr/ctl nets measure 40.74–43.01 mm, and CK's main path is about 42.9 mm. So ODT reaches the DRAM about 24.9 mm × 5.7 ps/mm ≈ **140 ps earlier** than CK and the other command signals. It is also the only DDR net still at 0.115 mm width: every other single-ended DDR net was resized to 0.1072 mm for the JLC stackup.
**Evidence:**
- DRC: `length_out_of_range … 'DDR addr/ctl length and skew' min length 41.0000 mm; actual 18.1337 mm … Pad K1 [/DDR/ODT] of U2 / Pad W1 of U1`, and `skew … actual -24.9429 mm`.
- Git history: in commit 6435b9e ("changed some trace widths") ODT had 174 track segments and measured **41.37 mm** (computed with the same script). In 754fa86 ("redid addr and clk") it has 23 segments and 18.13 mm. The meanders were deleted during the JLC re-route and never put back.
- Micron 4Gb_DDR3L Rev R, AC timing table: DDR3L-1066 tIS(base, AC160) = 140 ps and tIH(base, DC90) = 210 ps. ODT is registered on CK like a command ("ODT is referenced to VREFCA", Table 4). SAMA7D65 DS §85.7.7: DDR3L up to 533 MHz (tCK 1.875 ns).
- Microchip Curiosity (EV63J76A UG Fig. 3-13): "ADDR-CTL Matched Net Lengths [Tolerance = 10 mil]".

**Impact:** With 1T timing the command window is about ±0.94 ns around the CK edge. A 140 ps shift will probably not fail at 533 MHz, but it uses a large part of the margin that slew-rate derating, SoC output skew and jitter also need, on the signal that switches the DRAM's write termination. The schematic is fine; this is purely a layout regression. If boards come back with write errors, setting RTT_NOM/RTT_WR to off in the bootloader removes the dependency as a workaround.
**Recommendation:** Re-tune ODT on B.Cu to about 42 mm (inside 41–43 mm, close to CK) at 0.1072 mm width with the same meander settings as the other addr/ctl nets. Re-run DRC.

> **Reviewer note:** Independently re-measured from the working-tree meko.kicad_pcb with a separate parser (SCR/tools/odt_check.py): /DDR/ODT has 23 B.Cu items, 18.134 mm, no vias, all 0.115 mm wide. For comparison, DDR_A3 is 39.26 mm + 2 vias, ~{WE} 41.52 mm + 2 vias and CKE 39.73 mm + 2 vias (track only), all at 0.1072 mm. The DRC agrees (actual 18.1337 mm). MEDIUM is kept: it is a clear rule violation with a modest timing impact, and the fix is cheap.

#### [LOW] DDR-02 "DDR diff pair skew" rule compares DQS pairs against CK, giving false 2–3 mm skew violations; real intra-pair skews are tiny
**Where:** hardware/pcb/meko.kicad_dru, rule "DDR diff pair skew" (`A.hasNetclass('DDR_CLOCK') || A.hasNetclass('DDR_STROBE_LANE*')`, skew ±0.05 mm). Nets CK±, DQS0±, DQS1±.
**Issue:** A KiCad `skew` constraint compares every net matched by the rule against the longest one. The DRC lines say so themselves: `target net length 44.6524 mm (from /DDR/CK+)` for DQS0+ (42.50), DQS0− (42.33), DQS1+ (41.53) and DQS1− (41.54). That is DQS-vs-CK skew, not P/N skew. CK also looks long because KiCad's net length includes the stub to the termination resistor R17: CK+ ball → 0.54 mm on B.Cu → via (0.74 mm) → 0.41 mm on F.Cu → R17, about 1.7 mm in total. The main U1→U2 CK path is about 42.9 mm.
Actual intra-pair skews from ddr_lengths.py: CK 0.10 mm, DQS0 0.18 mm, DQS1 0.01 mm. That is ≤1 ps, negligible. DQS0 is slightly over the project's own 0.05 mm but well inside the common ±5 mil guideline in practice.
DQS-to-CK skew of about 1.4 mm (≈8 ps) is far inside tDQSS = ±0.25 tCK = ±469 ps (Micron AC table), and the SAMA7 UDDRC also does write leveling (DS: "Bit 7 – LEVEL Write Leveling Enable").
**Recommendation:** Restrict the rule to pairs: `(constraint skew (max 0.05mm) (within_diff_pairs))` (KiCad ≥ 9 syntax; verify in your version). Optionally add a separate DQS-to-CK length window. Optionally trim 0.13 mm from DQS0+.

#### [LOW] DDR-03 Addr/ctl spread is 2.26 mm (own rule 2 mm); 5 nets flagged by DRC
**Where:** DDR_A3 40.74, DDR_A5 40.92, A10 41.02, A1 41.06, A4 41.06 … ~{WE} 43.01 mm (DRC: WE 43.0766 at max, A3 40.7494 below min 41.0).
**Issue/impact:** 2.26 mm is about 13 ps, which does not matter against tIS/tIH (140/210 ps) at 533 MHz. CK (about 42.9 mm main path) sits inside the addr/ctl range, so the clock-to-command relationship is balanced.
**Recommendation:** Either add 0.3–0.5 mm to A3 and A5 and take about 0.1 mm off ~{WE} to make DRC clean, or loosen the rule to ±1.5 mm around 42 mm. No functional need.

#### [LOW] DDR-04 "DDR clearance to everything" (44) and "DDR diff pair clearance" (12) violations — not real SI problems
**Where:** Just outside the DDR/SAMA rule areas at the BGA escapes. Worst cases:
- CKE ↔ ~{RESET} 0.110 mm (F.Cu at 194.9,154.4; RESET is static).
- DQ12↔DQ14 0.155 mm, BA0↔~{CS} 0.178, ~{CAS}↔~{WE} 0.183, DQ11↔DQ15 0.184, DQ9↔DQ13 0.228, A0↔A3 0.239 mm.
- ~{RAS}↔/Display/SI 0.258 mm (B.Cu at about 201–202,162.6–163).
- /SAMA7/ZQ pad ↔ CKE 0.277 mm.
- Diff-pair rule (0.7 mm): DQS1−↔DQ8 0.328, DQS1+↔DQM1 0.442, CK+↔A13 0.520, CK−↔A10 0.560 mm.

**Analysis:** The 0.35 mm (≈4.6 H) and 0.7 mm (≈9 H) rules are very conservative for H = 76 µm microstrip. 3 H is 0.23 mm. `ddr_xtalk.py` measured the actual parallel-run length outside the BGA outlines:
- At <0.15 mm edge spacing: only BA0↔~{CAS} 0.72 mm and A13↔VREF 0.54 mm.
- At <0.25 mm: everything else is <1 mm, except VREF↔DQ11 (3.2 mm, see DDR-05) and two short runs next to +3V3 copper (A8 2.2 mm, DQ3 1.6 mm), which are AC ground.

Coupled lengths this short give negligible crosstalk at 533 MHz. Most aggressor/victim pairs are in the same group, so they are timed together. The Display/SI coupling is a short crossing with a slow SPI line. ZQ is only sampled during calibration, and CKE barely toggles.
**Recommendation:** Waive these, or enlarge the DDR/SAMA rule areas by about 1 mm so the escapes are covered. Consider increasing CKE↔RESET above 0.1 mm for manufacturability (it is legal at JLC's 0.09 mm).

#### [LOW] DDR-05 VREF track runs alongside DQ11 and DDR_A13
**Where:** /DDR/DDR_VREF (0.3 mm wide) on B.Cu next to /DDR/DQ11 for about 3.2 mm at <0.25 mm edge spacing. On F.Cu next to DDR_A13 for about 1.4 mm, with a 0.54 mm stretch at <0.15 mm.
**Issue:** VREF noise directly reduces input margin (VREF(DC) must stay within 0.49–0.51 VDDQ; Micron Table 25 notes). Guidelines (Micron TN-41-13, TI/NXP DDR3 guides) ask for ≥0.5 mm (20 mil) from VREF to switching signals, or a ground guard. The impact here is small because there are 100 nF caps at every VREF ball (C129/C130 at U2, C1 at U1.Y1) and at the divider (C64/C66).
**Recommendation:** When re-routing ODT, push VREF about 0.3 mm further from DQ11/A13 if space allows.

#### [LOW] DDR-06 Stackup dielectric constants do not match JLC's published values for the selected template; impedance is still inside ±10 %
**Where:** Board setup → stackup, and project tuning profiles ("50Ohms Single" 0.1072 mm, "100Ohms Diff" 0.0892/0.185 mm, "90Ohms Diff" 0.0892/0.105 mm).
**Evidence:** The project stackup (F.Cu 35 µm / 0.0764 prepreg / In1 15.2 µm / 0.13 core / 0.2328 prepreg / 0.13 core / 0.0764 prepreg) is identical in every thickness to **JLC06081H-1080**: 6L, 0.8 mm, 1 oz outer, 0.5 oz inner, from JLC's impedance-template API as archived in github.com/gsuberland/jlcpcb_autogenerated_stackups.
JLC lists NP-155F 1080 prepreg at **Dk 3.91**, core at 4.17 and 2116 at 4.16. The project uses 4.45 / 4.6 / 4.74.

FD-solver results (SCR/ddr_out/impedance.txt; mask = 15 µm, Dk 3.8, conformal):

| geometry (outer layer, H = 76.4 µm, t = 35 µm) | Dk 3.91 no mask | **Dk 3.91 + mask (JLC-like)** | Dk 4.45 + mask (as entered) |
|---|---|---|---|
| SE 0.1072 mm (all DQ/DM/addr/ctl) | 55.4 Ω | **51.9 Ω** | 49.4 Ω |
| SE 0.115 mm (ODT, stale width) | 53.5 Ω | **50.3 Ω** | 47.9 Ω |
| Diff 0.0892 / gap 0.185 (CK) | 116.0 Ω | **106.8 Ω** | 102.0 Ω |
| Diff 0.0892 / gap 0.196 (DQS measured) | 114.4 Ω | **105.7 Ω** | 101.0 Ω |

Measured gaps from the layout: CK 0.185 mm, DQS0/DQS1 0.196 mm, over about 30 mm.
All cases fall within the 50 Ω ±10 % / 100 Ω ±10 % targets in the Microchip Curiosity guide. JLC's own Dk values push the numbers about 5 % higher than the KiCad profile predicts. Delay is about 5.6–5.8 ps/mm, close to the profile's 5.59 ps/mm.
**Recommendation:** Run JLC's online impedance calculator for template JLC06081H-1080 and confirm the widths. If the differential pairs come out above about 105 Ω without mask credit, narrowing the gap to about 0.16 mm brings them back to about 100 Ω. Update the KiCad stackup Dk to JLC's values so the tuning profiles and time-domain lengths stay honest. Order with "impedance control: yes, JLC06081H-1080".

#### [LOW] DDR-07 Stale fabrication/impedance note on Cmts.User contradicts the actual design
**Where:** gr_text at (221.5,178.1) on Cmts.User. It says "50 Ohms single 0.115mm / 90 Ohms differ 0.100mm/0.10mm / 100 Ohms differ 0.100mm/0.18mm … DQ1 40.7–41.7mm".
**Issue:** The actual tuning profiles are 0.1072 / 0.0892-0.105 / 0.0892-0.185. The DRU lane1 window is 41.45–42.45 mm and the routed DQ8–15 are 41.46–42.43 mm. These look like the PCBWay-era numbers. They mislead anyone who reads them, including a fab engineer if the layer ends up in the outputs.
**Recommendation:** Update or remove the note.

#### [LOW] DDR-08 Bulk decoupling on +1V35_DDR is thinner than the Microchip reference
**Where:** +1V35_DDR. At U2: C67 4.7 µF plus 18 × 100 nF (C69, C71–C87), all within 2.4–7.4 mm of U2's centre, on F.Cu under the BGA. At U1: 16 × 100 nF (C15…C52, C128), no µF-class capacitor. Closest bulk is C98 22 µF at the PMIC, about 25 mm away.
**Evidence:** Curiosity EV63J76A UG Fig. 3-13/3-15: SoC 15 × 0.1 µF + C114 4.7 µF. DRAM 17 × 0.1 µF + C78 4.7 µF (VDD) + C98 4.7 µF (VDDQ). VREF divider also has C116 4.7 µF.
**Impact:** The In2 +1V35_DDR pour (377 mm²) and the 100 nF array handle high frequencies. Mid-frequency (1–20 MHz) current for refresh and burst writes has to come from 25 mm away. This is unlikely to fail, but it is below the reference design.
**Recommendation:** Add a 4.7 µF 0402 (same CL05A475KP5NRNC) near U1's VDDIODDR group, and a second 4.7 µF at U2 (one each for VDD and VDDQ). Note that CL05A475 is X5R 10 V and loses little capacitance at 1.35 V.

> **Reviewer note:** This duplicates SAMA-04 (MEDIUM), which already covers the SoC-side VDDIODDR bulk capacitor. This entry stays LOW for the DRAM side only.

#### [LOW] DDR-09 U2 footprint library not registered; symbol is a modified copy of the KiCad library
**Where:** ERC `footprint_link_issues: … does not include the footprint library 'MT41K256M16TW'`, `lib_symbol_mismatch: Symbol 'MT41K256M16TW' doesn't match copy in library 'Memory_RAM'`. DRC `lib_footprint_issues` for U2. hardware/pcb/fp-lib-table has no MT41K256M16TW entry even though hardware/pcb_lib/MT41K256M16TW/ exists.
**Verification:** The footprint Micron_FBGA-96_8x14mm_Layout9x16_P0.8mm matches Micron 4Gb_DDR3L Rev R Fig. 13 "96-Ball FBGA – x16 (TW)". 96 pads, columns 1–3 and 7–9, rows A–T (no I/O/Q/S), 0.8 mm pitch, 6.4 × 12.0 mm ball field centred, A1 at top-left. Pads are 0.42 mm, equal to Micron's "Ø0.42 SMD ball pads". Mask margin is +0.05 mm, which makes them NSMD (fine), and paste is −0.05 mm (Ø0.32 aperture, area ratio 0.67 on a 0.12 mm stencil, acceptable). Courtyard is 10 × 16 mm. The copy embedded in the board matches the library file.
The symbol pin map matches Micron Fig. 7 for all 96 balls (A1 VDDQ … T9 VSS, J1/J9/L1/L9/M7 NC).
**Impact:** None on fabrication. "Update footprint from library" and library-parity checks won't work for U2.
**Recommendation:** Add `(lib (name "MT41K256M16TW")(type "KiCad")(uri "${KIPRJMOD}/../pcb_lib/MT41K256M16TW"))` to fp-lib-table. The symbol mismatch can be ignored, or the symbol can be saved into a project library.

#### [LOW] DDR-10 DDR_A15 not routed to U2.M7 (no drop-in 8 Gb option)
**Where:** U1.R4 DDR_A15 is no-connect. U2.M7 is NC on the 4 Gb part and is A15 on 8 Gb x16 DDR3L parts.
**Issue:** The README says 512 MB, so this is consistent. However, the Curiosity board (AS4C512M16D3LA, 8 Gb) routes DDR_A15 to M7, and the journal earlier aimed for 1 GB. Routing A15 now (length-matched with addr/ctl) costs one trace and lets a 1 GB part be fitted later without a respin.
**Recommendation:** Optional. Route U1.R4 → U2.M7 in the DDR_ADDR_CTL class.

#### [INFO] DDR-11 100 Ω CK termination (R17) — deviates from the Microchip reference; acceptable
**Where:** R17 100 Ω 0201 across CK+/CK−, on F.Cu about 1.7 mm (stub including via) from U2.J7/K7.
**Analysis:** SAMA7D65 DS §85.6.3.1 says the DDR I/Os use "a serial termination connection scheme, where the driver has an output impedance matched to the characteristic impedance of the line", and the Curiosity board has no CK termination. With about 40 Ω drivers on each leg plus 100 Ω at the far end, the differential swing is about 0.75 V. That is still well above DDR3L VID(AC) ≈ 0.32 V. It adds about 1.35 V / 180 Ω ≈ 7.5 mA (≈10 mW) whenever CK is driven. It does damp ringing on a 43 mm single-load line, and the placement at the ball is good.
**Recommendation:** Keep it as a population option. If idle power matters, try DNP on the first boards and compare eye/stability.

#### [INFO] DDR-12 RESET# pull-up and no CKE pull-down — copied from the Microchip reference, intentional
**Where:** R18 100 kΩ from /DDR/~{RESET} to +1V35_DDR. CKE has no external resistor.
**Analysis:** Micron recommends RESET# below 0.2 × VDDQ during the power ramp. TI/NXP designs often use a pull-down on RESET# and on CKE. Meko instead copies Curiosity (R45 100k to VDDIODDR, nothing on CKE).
This suits the SAMA7 backup self-refresh mode the journal plans for: the DDR I/Os are put "in Retention state in order to maintain their state in Backup Self-refresh mode" (DS §22.3.4), DDR3PHY reset "will tie the CKE signal to '0'" (§22.3.4.1), and the controller drives RESET# low for the 200 µs JEDEC initialisation on cold boot. A pull-down on RESET# would risk wiping the DRAM in backup mode.
**Needs verification:** Check CKE behaviour while VDDCORE ramps before the PHY is out of reset. A DNP 10 kΩ pull-down footprint on CKE would be cheap insurance. For hibernate, +1V35_DDR must stay on (the MCP16502 Buck2 low-power state). The VREF divider draws 0.68 mA in that state, which is required because VREFCA must be maintained in self-refresh.

#### [INFO] DDR-13 Commercial temperature grade
MT41K256M16TW-107:P has no IT/AT suffix, so it is commercial: Tc 0 to +95 °C (Micron ordering options). A handheld cold-started below 0 °C is outside the spec. The industrial "-107 IT:P" variant is the drop-in if that matters. The -107 (DDR3-1866) speed bin runs far below its limit at the SoC's 533 MHz maximum.

#### [INFO] DDR-14 Bootstrap DDR configuration must differ from the Curiosity board
The Curiosity board uses 8 Gb AS4C512M16D3LA (16 row bits, A0–A15). Meko uses 4 Gb x16: 15 row bits (A0–A14), 10 column bits, 8 banks, 2 KB page. at91bootstrap/U-Boot SPL DDR settings (row count, total size 512 MB, timings for the -107 die at DDR3L-1066 / CL7) must be changed accordingly, otherwise memory aliases or training fails.

### Design rationale

- **Topology:** A single x16 DDR3L device point-to-point with the SoC's 16-bit UDDRC. Fly-by routing and VTT termination are not needed: there is only one load per address/command net, and the SAMA7 DDR3PHY uses ZQ-calibrated series (source) termination (DS §85.6.3.1). The DRAM's ODT terminates DQ/DQS on writes, and the PHY's own ODT does so on reads. This matches Microchip's SAMA7D65 Curiosity and SAMA7G5-EK, neither of which has VTT or address termination. A VTT regulator would cost power and area for no benefit at 533 MHz with one load.
- **Memory choice:** The SAMA7D65 has one CS/CKE and a 16-bit bus. LPDDR3 parts are x32 or dual-die, which would waste half the capacity (journal 2026-08-20 / 09-01), so a single-die x16 DDR3L was chosen, with the MCP16502**AB** whose SELV2 is left floating (High-Z → 1.35 V for Buck2, MCP16502 DS Table 4-4).
- **Byte lanes:** Lane 0 (SoC D0–7, DQM0, DQS0) → DRAM DQ0–7/LDM/LDQS, wired 1:1. Lane 1 (SoC D8–15, DQM1, DQS1) → DRAM DQ8–15/UDM/UDQS, with D11↔DQ13, D13↔DQ15 and D15↔DQ11 swapped inside the lane to ease the escape. DDR3 allows this. DQ0 and DQ8, the write-leveling feedback bits for x16 parts, are not swapped, so write leveling and MPR-based training still work. Address and BA are 1:1, as they must be for mode-register writes.
- **VREF:** One divider (R15/R16 1 kΩ 1 %) feeds SoC DDR_VREF, VREFCA and VREFDQ. C64 goes to VDDQ and C66 to GND at the divider, exactly as in DS Fig. 85.11, so VREF follows VDDQ at both DC and AC. There is a local 100 nF at each VREF ball (C129, C130 at U2; C1 at U1.Y1). The 1 % resistors keep VREF within about ±0.5 % of VDDQ, half of JEDEC's ±1 % DC budget. Sharing one VREF is acceptable at DDR3L-1066 with a single device.
- **ZQ:** 240 Ω 1 % (0201WMF2400TEE, "F" = 1 %) to GND at each end: R19 at U2.L8 per Micron Table 4, and R3 at U1.AA2 per DS Table 24.2.
- **Layout strategy:** Both BGAs sit on B.Cu, rotated 45° (U1 −45°, U2 135°) and pushed apart to make room for meanders (journal 10-05). The data lanes are routed entirely on B.Cu with **no vias** (reference In4 GND). Addr/ctl/CK escape from B.Cu to F.Cu with one through-via at each end (reference In1 GND). No DDR signal is routed on an inner layer or over the In2 power plane. The fan-out was copied from Microchip's Altium reference design.
- **Length targets in meko.kicad_dru:** CK 43 mm, addr/ctl 41–43 mm, lane0 42–43 mm, lane1 41.45–42.45 mm. Lane 1 is set about 0.5 mm shorter than lane 0, presumably to absorb package-delay differences the author got from Microchip; no die_length values exist in the footprints. Byte-to-byte offsets are irrelevant in DDR3 because each lane has its own DQS and is trained separately.
- **Rule areas** ("DDR", "SAMA") drop clearance to 0.1 mm under the BGAs, while elsewhere the 0.35 mm "3H-plus" rule applies. Most of the 56 clearance violations sit at the boundary between the two (DDR-04).

#### Measured lengths (mm, including via barrels; working tree)

| group | nets | min | max | spread | rule |
|---|---|---|---|---|---|
| CK | CK+ 44.57 / CK− 44.67 total; main path ≈ 42.9 (excluding the 1.7 mm R17 stub) | | | P/N 0.10 | opt 43 |
| Lane 0 (B.Cu, 0.1072 / DQS 0.0892) | DQ0–7, DQM0, DQS0± | 42.07 (DQM0) | 43.00 (DQ3) | 0.92 | 42–43 ✓; DQS0 42.51/42.33 |
| Lane 1 | DQ8–15, DQM1, DQS1± | 41.46 (DQ12/14) | 42.43 (DQ10) | 0.97 | 41.45–42.45 ✓; DQS1 41.53/41.54 |
| Addr/ctl (F.Cu + 2 vias, 0.1072) | A0–A14, BA0–2, CS#, RAS#, CAS#, WE#, CKE | 40.74 (A3) | 43.01 (WE#) | 2.26 | 41–43, skew 2 ✗ (minor) |
| ODT | | **18.13** | | | ✗ DDR-01 |

The full per-net table is in SCR/ddr_out/ddr_lengths.txt.

### Verified OK

- All 63 U1↔U2 DDR signal connections (netlist /DDR/* nets, 2 nodes each) match SAMA7D65 pinout_table.html and Micron Fig. 7. U1's DDR balls match the datasheet table: D0 N2 … D15 W3, A0 W6 … A14 L9, CLK U4/T4, CKE V3, CSN V7, WEN N10, RASN U8, CASN T8, ODT W1, RESETN V1, DQM0 N1, DQM1 Y4, DQS0 R1/R2, DQS1 Y6/AA6, VREF Y1, ZQ AA2.
- DQS/DM stay with their lanes, and DQ swaps occur only inside lane 1. DQS polarity is correct (DQS0+ → LDQS F3, DQS0− → LDQS# G3; DQS1+ → UDQS C7, DQS1− → UDQS# B7). CK polarity is correct (U4 → J7 CK, T4 → K7 CK#).
- All 15 VDDIODDR balls, and all 9 VDD + 9 VDDQ DRAM balls, are on +1V35_DDR. VSS/VSSQ are on GND. NC balls J1/J9/L1/L9/M7 are left open. SoC DDR_A15 (R4) is a no-connect.
- +1V35_DDR = 1.35 V via MCP16502AB Buck2 with SELV2 open (DDR3L range 1.283–1.45 V, Micron features list).
- ZQ 240 Ω 1 % on both sides. VREF divider and capacitors match Microchip Fig. 85.11 and Curiosity Fig. 3-14.
- 100 nF capacitors: 18 at the DRAM (one per power ball), on the opposite side within the BGA shadow. 16 at the SoC.
- Footprint geometry vs the Micron TW drawing (DDR-09). LCSC C253882 is MT41K256M16TW-107:P (FBGA-96 8×14).
- Reference planes: In1, In3 and In4 are each a solid GND pour (3586 mm² each). The sampled check found no DDR track over a void, apart from antipads at its own vias. 54 of 59 DDR signal vias have a GND stitching via within 1 mm; the other 5 (CK− at U2, A10, A13, RESET#, VREF) are within 1.03–1.55 mm, which is fine at 533 MHz.
- No via stubs: all DDR vias are full F.Cu↔B.Cu transitions, and the data lanes have no vias at all.
- R17 placement: the stub to the DRAM ball is short (≈1.7 mm).
- DRC shows no unconnected or shorted DDR items (the +3V3/+1V8 shorts and unconnected items in the DRC are outside DDR). The regenerated drc.rpt (22:02) has the same DDR entries as before.

### Datasheets used

- Micron 4Gb DDR3L (MT41K1G4/512M8/256M16) Rev R 09/18 — https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/6128/MT41K1G4_MT41K512M8_MT41K256M16_RevR_Sep2018.pdf → SCR/datasheets/MT41K256M16TW/micron_4Gb_DDR3L_RevR.pdf (+ ds.txt). Used: features/ordering p.1, Fig. 7 ball map, Table 4 ball descriptions, Fig. 13 TW package, Table 25, AC timing (tIS/tIH/tDQSS).
- Microchip SAMA7D6 Series Data Sheet DS60001851E — https://ww1.microchip.com/downloads/aemDocuments/documents/MPU32/ProductDocuments/DataSheets/SAMA7D6-Series-Data-Sheet-DS60001851.pdf → SCR/datasheets/SAMA7D65/ds.pdf. Used: Table 24.2, §22.3.4, §85.6.3 (ZQ, VREF Fig. 85.11), §85.7.7, fDDR_CLK table, pin table.
- SAMA7D65 Curiosity Kit (EV63J76A) User Guide DS50003806B → SCR/datasheets/sama7d65-curiosity-ug/ug.pdf. Used: Fig. 3-13/3-14/3-15 DDR schematic and routing notes.
- MCP16502 data sheet → SCR/datasheets/mcp16502/mcp16502.pdf. Used: Table 4-4 (SELV2 → VOUT2).
- JLCPCB 6L 0.8 mm stackups (JLC06081H-1080 etc.), auto-generated from JLC's API — https://github.com/gsuberland/jlcpcb_autogenerated_stackups → SCR/datasheets/jlc_stackups/. These files are not verified by JLC; confirm with JLC's impedance calculator.
- LCSC product page C253882 (MPN confirmation): https://www.lcsc.com/product-detail/C253882.html
- hardware/pcb_lib/SAMA7D65-4HB/pinout_table.html (project copy of the Microchip pin table).

---

# Connectivity (Wi-Fi/BT, microSD, USB-C)

Reviewer scope: /Wireless/ (IC2, Y3), /SD Cards/ (J6, J7), /USB/ (J3, U6, D2-D4) plus their SAMA7 / BQ25640 counterparts and the layout (meko.kicad_pcb working tree).

### Summary
- There are no CRITICAL findings. I checked the IC2 MAYA-W386 symbol (all 90 pins) and footprint (pad grid, 0.6 mm pads, RF keep-out polygon) against the u-blox data sheet R05 Table 20 and Fig 15/16. Both match. The U6 ECMF02-2AMX6 pinout and footprint match ST DocID17815 Fig 1/17. The D+/D- polarity is correct from J3 to the SAMA7 HHSDPA/HHSDMA pins.
- The MAYA-W3 is based on the **Infineon CYW55513**, not the NXP IW612. The software stack is brcmfmac/FMAC plus btbcm, and the NVRAM needs `lpo_select=3`.
- The main hardware risks are power related:
  - 3V3 is supplied by a 1 A MCP16502 Buck1 that also feeds both SD cards. The module's peak current is 850 mA.
  - There is no 10 µF bulk capacitor at the module (u-blox requires one). A single 0.15 mm via feeds both 3V3 pins.
  - SDMMC2 runs at 1.8 V but its calibration resistor is the 3.3 V value (16k9 instead of 20k).
  - The VBUS path is an 88 mm, 0.8 mm-wide trace on an inner 0.5 oz layer. With BQ25640 default settings (ICHG 2 A, IINDPM auto 3 A) the drop and heating are excessive.
- The external SD slot has no ESD protection and no VDD switch. All USB VBUS/CC ESD parts are DNP, and ESD441 (5.5 V VRWM) is the wrong part for VBUS anyway.
- USB-C OTG is credible: the BQ25640 has an integrated DRP CC controller, so no fixed Rd is fitted. It needs software (CC_MODE=DRP) and gives the SAMA7 no direct VBUS sense line.
- Known, being fixed by owner: WiFi SDIO pull-ups R33-R37 rail change (+3V3 to +1V8). The schematic is already +1V8; the layout still shows the DRC +3V3/+1V8 short at R35.
- Reviewer pass: I re-verified all MEDIUM findings and CON-06/16. No findings removed and no severities changed. Corrections: CON-03 IPC figure (0.85 → about 0.75 A), CON-16 SW4 distance (5 mm → about 2 mm, see LAY-05), USB-C receptacle is Extended at JLC, not Basic.

### Findings

#### [MEDIUM] CON-01 MAYA 3V3 supply: no bulk capacitance near the module, single small via, and the 1 A buck is shared with both SD cards
**Where:** IC2 A7/B7 (3V3), A2 (1V8); C110 1 µF (+3V3, top side at 178.74,170.05); C109 1 µF (+1V8); IC1 MCP16502 Buck1 OUT1 -> +3V3; via at (178.25,169.55) 0.3/0.15 mm is the only +3V3 via feeding A7/B7.
**Issue:**
- u-blox requires at least 10 µF bulk capacitance on both the 3V3 and 1V8 rails, close to the module supply pins, in addition to the 100 nF-1 µF bypass caps. Only one 1 µF 0402 X5R cap is fitted per rail; at 3.3 V DC bias it is effectively about 0.5-0.6 µF.
- The nearest ≥10 µF parts on +3V3 are C94 22 µF (Buck1 output, about 17 mm away) and C118 10 µF (at the SD socket, about 25 mm away).
- The whole module 3V3 current goes through one 0.15 mm-drill via (peak 480 mA in TX, 850 mA during firmware init/calibration).
- Budget on +3V3 (MCP16502 Buck1, "Four 1A output current buck channels", ILIM_HS min 1.2 A peak):
  - MAYA: 850 mA peak during init, 390 mA in 6 GHz TX.
  - Two microSD cards: up to about 100-200 mA each during writes in High Speed.
  - SAMA7 VDDIOP0/VDDIN33/VDDUTMI/VDDSDMMC0/1/GMAC/LVDS, codec IOVDD, touchpad, display.
- The likely case of WiFi firmware download and calibration while the OS card is busy can exceed the 1 A rating. u-blox asks for 20% margin over peak.
- Cross-domain (power), needs verification: with a 1S Li-ion, Buck1 goes into dropout at low battery. The MAYA 3V3 minimum is 3.13 V.
**Evidence:**
- SIM UBXDOC-465451970-2522 §3.3.1: "a minimum bulk capacitance of 10 µF should be applied to the 1V8 and 3V3 rails and placed close to the module supply pins"; "contingency of at least 20% over the stated peak current" (§2.1).
- DS Table 27: "Firmware initialization / self-calibration 850 mA" on 3V3.
- MCP16502 DS p.1 and p.12 (ILIM_HS1 1.2/1.8/2.4 A).
- Netlist: `+3V3 (63): ... IC1.9(OUT1_9), IC2.A7, IC2.B7, J6.4(VDD_4), J7.4(VDD_4), U1.F9(VDDSDMMC1), U1.G7(VDDIN33), U1.L3(VDDUTMI), U1.T13(VDDIOP0) ...`
**Recommendation:**
- Add a 10 µF 0603 X5R on +3V3 and a 4.7-10 µF on +1V8 within a few mm of A7/B7 and A2.
- Add 2-3 more +3V3 vias (and one more +1V8 via) between the pads, the caps and the In2 plane.
- Do a +3V3 current budget. If it is above about 0.8 A, move the SD card VDD and/or the MAYA 3V3 to a separate regulator, e.g. a 3.3 V buck-boost from VSYS, which also solves dropout at low battery.
> **Reviewer note:** Confirmed. SIM R02 §3.3.1 requires a minimum of 10 µF bulk on 1V8 and 3V3, close to the module. DS Table 27 gives 850 mA (3V3) for firmware init. +3V3 near IC2 has a single 0.3/0.15 via at (178.25, 169.55), and C110 is 1 µF. On +1V8 there is also C108 4.7 µF, but it is not at the module.

#### [MEDIUM] CON-02 SDMMC2 (WiFi, 1.8 V) calibration resistor R10 = 16k9; the data sheet requires 20 kΩ for 1.8 V
**Where:** R10 16k9 on /SAMA7/SD2_CAL (U1.E14 SDMMC2_CAL); VDDSDMMC2 = +1V8.
**Issue:** The SAMA7D6 HSIO calibration cell expects RZQ = 20 kΩ for 1.8 V signalling and 16.9 kΩ for 3.3 V. SDMMC2 only ever runs at 1.8 V (the MAYA is a 1.8 V-only SDIO device). In UHS-I (SDR50/DDR50) the SD spec makes calibration mandatory. With 16.9k the calibrated driver impedance is off by about 15%. It probably works, but it is out of spec at 100 MHz SDR50. R8/R9 (SDMMC0/1 at 3.3 V) are correct at 16k9.
**Evidence:** SAMA7D6 DS60001851E §85 (p.3811): "SDMMCx_CAL loaded with a 20 KΩ RZQ resistor for 1.8V memories and a 16.9 KΩ resistor for 3.3V memories … output impedance calibration is required for 1.8V signaling in SD UHS-I". Netlist: `/SAMA7/SD2_CAL (2): R10.2, U1.E14`; `F13 VDDSDMMC2 -> +1V8`.
**Recommendation:** Change R10 to 20.0 kΩ 1%. R11 (QSPI0_CAL, and VDDQSPI0 is also +1V8) should be 20k as well if QSPI0 is ever used. It isn't today, because those pins carry the BT UART/I2S.
> **Reviewer note:** Confirmed. DS60001851E §85 text: "20 KΩ RZQ resistor for 1.8V memories and a 16.9 KΩ resistor for 3.3V". R10 (SD2_CAL) and R11 (QSPI0_CAL) are both 16k9 while VDDSDMMC2 and VDDQSPI0 are +1V8.

#### [RESOLVED] CON-03 VBUS path: 88 mm of 0.8 mm trace on In2 (15 µm Cu); BQ25640 defaults will push about 2 A through it
> **✅ Resolved (2026-11-27):** see PWR-04. VBUS is now an In2 pour plus a 1.25 mm B.Cu trace, ≈ 33 mΩ in total.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** Net VBUS: J3 (190.3,198.2) -> 0.6/0.8 mm on B.Cu (27.8 mm) -> In2.Cu 0.8 mm (87.9 mm, along the left board edge x≈165.8 and under the MAYA module) -> 2×0.45/0.225 vias -> U4 BQ25640 VBUS at (170.9,135.3).
**Issue:**
- Calculated resistance: In2 is 0.0152 mm Cu per the stackup, giving R ≈ 1.72e-8·0.088/(0.8e-3·15.2e-6) ≈ 0.124 Ω. Adding B.Cu and vias gives about 0.15 Ω.
- BQ25640 POR state: ICHG = 2000 mA. IINDPM is set automatically from the CC result: USB-C High = 3 A, DCP = 3.2 A.
- With a 3 A Type-C charger, input current is about 2 A or more. That means about 0.3 V drop and about 0.6 W dissipated in an inner trace (IPC-2221 internal: about 0.75 A for 20 °C rise at this cross-section, 0.8 mm x 15.2 µm ≈ 18.8 mil²).
- The drop also eats VINDPM headroom, so the charger throttles early on worn cables.
**Evidence:** BQ25640 DS (SLVSIK1) REG ICHG "POR: 2000mA"; IINDPM "Based on Detection results … USB C High = 3A, USB DCP = 3.2A, POR 3200mA". Stackup in meko.kicad_pcb: In2.Cu thickness 0.0152. Track dump: `('VBUS','In2.Cu') 87.91 mm widths [0.8]`.
**Recommendation:**
- Widen VBUS to ≥2 mm, or pour it on In2, and use 3-4 vias at each layer change.
- Or shorten the route (place the charger closer to J3).
- Until then, cap IINDPM to about 1.5 A and ICHG to about 1 A in the first-boot driver/bootloader. The BQ watchdog halves ICHG, so set it explicitly.
> **Reviewer note:** Confirmed by re-measuring: VBUS is 87.9 mm of 0.8 mm on In2.Cu, 20.3 mm of 0.8 mm plus 7.6 mm of 0.6 mm on B.Cu, and 8 vias, with no VBUS zones. In2 is 0.0152 mm, giving R ≈ 0.124 Ω on In2. BQ25640 ICHG POR is 2000 mA. I corrected the IPC-2221 internal figure from 0.85 A to about 0.75 A at ΔT = 20 °C. Same issue as LAY-04 / PWR-04: report it once.

#### [MEDIUM] CON-04 External microSD (J7): no ESD protection, VDD hard-wired to the system +3V3 (no load switch or power cycling)
**Where:** J7 TF-015 (external, hot-swap), nets /SAMA7/EXT.*, J7.4 VDD -> +3V3; also J6.
**Issue:**
- The external slot is user-accessible, but CLK/CMD/DAT0-3/CD go straight to SAMA7 HSIO pins (JEDEC HBM ±2 kV class) with no TVS array.
- Card VDD connects directly to the same +3V3 that feeds the SoC I/O and the WiFi module:
  - Hot insertion dumps the card's input capacitance onto the rail, which can droop or glitch +3V3. Only C119/C120 2×22 µF are nearby.
  - A hung card can't be power-cycled for error recovery.
  - UHS-I is impossible, because the card VDD must be power-cycled to return from 1.8 V signalling. See CON-07.
**Evidence:** Netlist `J7.4(VDD_4) -> +3V3`; no ESD parts on /SD Cards/ (only C118-120, J6, J7, R43-R54).
**Recommendation:**
- Add a low-capacitance ESD array (≤1 pF/line, e.g. TPD6E05U06 or 2× TPD4E05U06) at J7 on CLK, CMD, DAT0-3, CD and VDD.
- Feed the J7 VDD (and optionally J6) through a small load switch with controlled rise time, e.g. TPS22916/TPS22919/AP22802, driven by a SAMA7 GPIO. The DT can then use it as `vmmc-supply` and Linux can power-cycle the card.
> **Reviewer note:** Confirmed. The /SD Cards/ sheet has no TVS parts, and J7.4 VDD connects directly to +3V3.

#### [MEDIUM] CON-05 USB-C VBUS/CC have no populated ESD protection; ESD441 is not suitable for VBUS
**Where:** D2 (VBUS), D3 (CC2), D4 (CC1): all ESD441, all `dnp=True`. U6 protects only D+/D-.
**Issue:**
- As built, CC1/CC2 (straight into the BQ25640 CC pins) and VBUS have only the chip-level ±2 kV HBM rating. They have no IEC 61000-4-2 protection on a user-facing connector.
- ESD441 has VRWM 5.5 V and VBR 6-8 V. If D2 is ever populated, it conducts on any VBUS above about 6 V and can fail short:
  - a misbehaving adapter, or hot-plug ringing (often about 2× VBUS);
  - BQ25640 OTG can be programmed up to 9.6 V, and its VBUS rating is 26 V.
- ESD441 is fine for CC: CC is ≤5.5 V and the device doesn't support VCONN.
**Evidence:** ESD441 DS (SLVSH26C) §5.6: VRWM 5.5 V, VBR 6-8 V. BQ25640 DS §6.1: VBUS/CC abs max 26 V; §6.2 HBM ±2000 V. Netlist: `D2 … dnp=True`, `D3 … dnp=True`, `D4 … dnp=True`.
**Recommendation:** Populate D3/D4 (ESD441 is appropriate on CC). Replace D2 with a VBUS TVS with VRWM ≥ 20-24 V, e.g. TVS2200, ESD751, or a SOD-323 22 V TVS. Place all of them at J3.
> **Reviewer note:** Confirmed. ESD441 SLVSH26C: VRWM 5.5 V, VBR 6/7/8 V at 1 mA. D2 (VBUS), D3 (CC2) and D4 (CC1) are all `dnp=True`. BQ25640 VOTG_RANGE is 3.84-9.6 V (electrical characteristics table). Severity is fine.

#### [LOW] CON-06 TF-008 (internal OS card) detect switch is normally-closed, so BOOT.CD polarity is inverted from the SAMA7 "low = card present" convention
**Where:** J6.10 DET_A -> GND, J6.9 DET_B -> /SAMA7/BOOT.CD (R48 10k to +3V3) -> U1.G4 SDMMC1_CD.
**Issue:**
- The SOFNG TF-008 drawing ("COMPONENT", p.2) shows D1-D2 **closed without a card** and **open with a card inserted**. So CD = 0 with no card and CD = 1 (pulled up) with a card.
- The SAMA7 treats SDMMC_CD as active-low:
  - Pin table: "SDMMC[2:0]_CD … Low".
  - The ROM code skips SDMMC boot if USE_CD=1 and CD is high (§21.1.7.4.2 and §21.1.9.3).
  - Linux sdhci native CD ignores `cd-inverted`.
- With the default boot config (USE_CD=0) and `non-removable` in the DT it works. Programming USE_CD=1 into the boot config would make the board unbootable from the OS card.
**Recommendation:** Keep USE_CD=0 and declare the slot `non-removable` (it is internal anyway), or use a GPIO CD with ACTIVE_HIGH. Alternatively swap to a normally-open socket.
**Needs verification:** the J7 TF-015 detect polarity. The XYECONN drawing doesn't state it; push-push sockets usually close Cd to the shell on insert, which would be correct.
> **Reviewer note:** Confirmed. The SOFNG TF-008 "COMPONENT" diagram shows D1-D2 closed in "NORMAL (WITHOUT CARD)" and open in "CARD INSERTED". DS60001851E: SDMMC_CD is active Low. Boot-config USE_CD bit 7 = 1 makes the ROM skip the card when CD is high. J7 TF-015 has only a single DET pin (J7.9), which presumably switches to the grounded shell, so it is likely normally open. Still unverified.

#### [LOW] CON-07 SD slots are 3.3 V-only (no UHS-I); SDMMCx_1V8SEL not used
**Where:** VDDSDMMC0 (W17) and VDDSDMMC1 (F9) = +3V3; SDMMC0_1V8SEL (N11) and SDMMC1_1V8SEL (A2) unconnected.
**Issue:** Both microSD buses are fixed to 3.3 V signalling, so they are limited to High Speed (50 MHz, about 23 MB/s). The SAMA7D65 supports SDR104 on all three SDMMCs, but that needs a 3.3/1.8 V switchable VDDSDMMC plus card VDD power cycling (CON-04). This is fine for music and OS boot but leaves a 2-4× speedup unused.
**Recommendation:** Accept it as a design decision, or for a future revision add a dual-output LDO switched by SDMMCx_1V8SEL on VDDSDMMC0/1, with RZQ changed to 20k (see CON-02).

#### [LOW] CON-08 WL_EN / BT_EN have no external pull-down; SAMA7 reset-default pull-up fights the module's 50 kΩ pull-down
**Where:** /SAMA7/WL.EN (U1.N14 PB13, VDDQSPI0) -> IC2.J3; /SAMA7/BT.EN (U1.E18 PD16, VDDIOP1) -> IC2.J7.
**Issue:**
- The SAMA7 pin reset state is "PIO, I, PU" with RPULL 60-140 kΩ. The MAYA has an internal 50 kΩ pull-down, and VIL max is 0.3 V while VIH min is 1.2 V.
- From reset until software drives the pins, EN sits at about 0.47-0.82 V. That is undefined, and the u-blox power-up sequence wants EN low until ≥50 µs after the rails are valid.
- Low impact: +1V8 (VDDQSPI0/VDDIOP1) only comes up after I2C enables MCP16502AB LDO2, so the pins are unpowered at first.
**Evidence:** SAMA7D6 pinout table (pcb_lib pinout_table.html) PB13/PD16 "PIO, I, PU"; DS DC table "RPULL 60-140 kΩ"; MAYA DS Table 25 (VIH 1.2 V, VIL 0.3 V, RPD 50 kΩ).
**Recommendation:** Add 10 kΩ pull-downs on WL_EN and BT_EN (common practice on CYW designs), or make U-Boot/at91bootstrap drive both low immediately.

#### [LOW] CON-09 PCM_MCLK is wired to I2SMCC0_MCK, so two outputs share one net
**Where:** /SAMA7/BT.MCLK: IC2.E8 PCM_MCLK (DS: "O, optional clock output") <-> U1.N21 PB18 I2SMCC0_MCK (O).
**Issue:** Both ends are outputs. If the SAMA7 pinmux enables I2SMCC0_MCK while the CYW firmware enables I2S_CCLK, they contend. The module doesn't need an MCLK input.
**Recommendation:** Don't mux PB18 as MCK (leave it GPIO-input) unless the firmware is known to keep E8 tri-stated. For a future revision, add a 0 Ω/33 Ω series resistor (DNP-able).

#### [LOW] CON-10 WiFi SDIO details: strap/pull-up values, skew, no series-R option
**Where:** R33-R37 (47k to +1V8), /SAMA7/WIFI.*.
**Issue:**
- SD_DAT[2] is the host-interface strap. u-blox specifies "10 kΩ pull-up to 1V8" for SDIO mode, and a CMD pull-up of 10-50 kΩ (typ 10k). 47k is inside the CMD range and the SAMA7/MAYA internal pull-ups (PU default at reset, 100 kΩ in the module) also help, so it should strap correctly, but it is not the documented value.
- Routed lengths: CK 20.5 mm, CMD 23.2, DAT0 18.9, DAT1 22.3, DAT2 19.8, DAT3 27.7. DAT3 is +7.1 mm versus CLK; the spec is ±3 mm (SIM Table 18). That is about 45 ps, negligible at 100 MHz.
- There are no series termination footprints. The SIM checklist recommends them as an EMI option.
**Recommendation:** When fixing the known pull-up rail issue, use 10k on DAT2 (and optionally CMD). Consider 0 Ω 0201 series footprints on CLK at the host side for EMI tuning.

#### [LOW] CON-11 Antenna feed has no pi-network/0 Ω option; a GND track touches the RF keep-out
**Where:** /Wireless/ANT: IC2.K9 RF_ANT1 -> IC2.L9 ANT_EXT_FEED, 1.5 mm, 0.115 mm wide on B.Cu (about 50 Ω over In4). DRC `items_not_allowed`: GND tracks 0.6 mm wide at (165.91,168.07) and (165.91,174.67) (M8/M2 pad escapes) touch the footprint RF keep-out.
**Issue:**
- The direct K9-L9 link works and matches the u-blox "connect L9 to K9" instruction.
- However, the SIM checklist asks for "a pi-filter … in front of each antenna for final matching". With no footprint there is no way to retune for the housing, or to insert a U.FL for conducted testing.
- The keep-out touch is cosmetic: the copper edge exactly meets the polygon.
**Evidence:** SIM §2.2.7 and §3.10.1; DRC rpt `[items_not_allowed] … Track [GND] on B.Cu, length 0.5361 mm`.
**Recommendation:** Optional: 0201 series 0 Ω + 2× DNP shunt pads. Neck the two GND escapes down to 0.4 mm, or accept the DRC.

#### [LOW] CON-12 BQ25640 D+/D- left unconnected, so no BC1.2 / legacy charger detection
**Where:** U4.20/21 D-/D+ no_connect.
**Issue:** EN_DPDM_DET defaults to 1, so BC1.2 detection runs on open pins. A legacy USB-A charger with an A-to-C cable (Rp 56k = "default") will be treated as SDP/unknown, limiting input to 500 mA. This is a functional limitation, not a fault.
**Recommendation:** Accept it, or tie the BQ D+/D- to the connector side of the data pair (DIRTY_D±; this is TI's standard topology). If left open, set EN_DPDM_DET=0 in software.

#### [LOW] CON-13 No direct VBUS-present signal to the SAMA7 for the UDC
**Where:** VBUS net has no SAMA7 node; BQ ~PG drives only LED D1; CHG_~{INT} -> PD30.
**Issue:**
- atmel_usba_udc normally uses `atmel,vbus-gpio` to gate the D+ pull-up. Without it, the gadget assumes VBUS is always present: D+ pulls up while unplugged and in host/OTG mode.
- Role and VBUS detection must come from the BQ25640 over I2C (VBUS_STAT, triggered by INT). A custom role-switch/extcon driver is needed.
**Recommendation:** Software plan (BQ25640 driver -> usb-role-switch). Or for a future revision, route ~PG (open-drain, also on VDD-tolerant pins) to a spare 3.3 V GPIO with a pull-up as `vbus-gpio`.

#### [LOW] CON-14 DRC clearance violations on SDMMC_EXT / SDMMC_WL / USB / ASI_BT netclasses
**Where:** SCR/main/drc.rpt (filtered: 20× SDMMC_EXT, 2× SDMMC_WL, 3× USB, 7× ASI_BT).
**Assessment:**
- **None are manufacturing violations.** The minimum actual gap is 0.10-0.12 mm, at or above the Default clearance (0.1 mm) and within JLC 6-layer capability. They are breaches of the self-imposed crosstalk spacing rules (0.35/0.3/0.2 mm).
- **USB (3):** Pad-to-pad inside J3 (A5-B7, A8-B6, 0.2 mm at the 0.5 mm-pitch connector) and inside U6 (pad 4 NC to pad 5). These are inherent to the footprints and are false positives. Add a rule that exempts intra-footprint pads, e.g. `(condition "A.Parent == B.Parent")`.
- **SDMMC_EXT (20):** All are inside the SAMA7 BGA fan-out window (x 200-206, y 163-175). Worst cases:
  - EXT.DAT3 near the VOL+ via: 0.20 mm.
  - EXT.DAT3 near AUDIOCLK: 0.157 mm over a short span. AUDIOCLK is the noisiest aggressor here; give it more room if possible.
  - EXT.CK near the BT.TX via: 0.146 mm.
  - EXT.CD near the jack-detect via: 0.17 mm.
  - EXT.DAT1 near the WL.EN/BT.RTS vias: 0.12-0.32 mm.
  The SIM allows the 3W/4W spacing to be ignored for up to 10 mm of BGA escape. Acceptable at 50 MHz HS.
- **SDMMC_WL (2):** WIFI.CK track to WIFI.DAT0 via 0.27 mm, and DAT3 to the CMD via 0.27 mm. These are intra-bus and acceptable.
- **ASI_BT (7):** BT.DOUT/BT.DIN versus UART/CTS at 0.10-0.16 mm. Low-speed (≤2 MHz PCM, ≤4 Mbaud UART) and harmless.
**Recommendation:** Optionally fix the AUDIOCLK-EXT.DAT3 and EXT.CK-BT.TX-via spots. Waive the rest.

#### [INFO] CON-15 MAYA-W3 is Infineon CYW55513-based, not NXP IW612
**Evidence:** MAYA-W3 DS R05 p.2 product table: "MAYA-W386 … Chipset CYW55513"; §1.1 "based on the Infineon CYW55513, CYW55512 and CYW55511 chipsets". The pin names (LHL_GPIO, BT_GPIO, SMIF_SPHB, RF_CNTL, JTAG_SEL) are Infineon naming.
**Implication:**
- The Linux stack is brcmfmac with the Infineon FMAC/ifx-backports, CYW5551x firmware plus a board NVRAM, and BT via hci_uart/btbcm (patchram).
- The NVRAM must have `lpo_select=3` (external crystal Y3, the default) and `muxenab=0x10` if the WL_HOST_WAKE OOB IRQ on PD1 is used.
- BT bring-up holds UART_CTS low while raising BT_EN (SIM §5.3.3).
- MAYA-W1 = IW416 and MAYA-W2 = IW612; that may be the source of the confusion.

#### [INFO] CON-16 Antenna placement versus housing (needs mechanical verification)
**Where:** IC2 on B.Cu at (172.41,171.37) rot -90. The antenna end is 0.13 mm from the left board edge (x 165.13). The footprint RF keep-out covers all copper layers.
**Note:** The PCB-side requirements are met:
- module at the board edge with the antenna facing out;
- GND plane extending far more than 10 mm on both sides (the board edge runs 77 mm);
- keep-out on all layers;
- 28 GND stitching vias under the module.
**Needs verification in CAD:**
- ≥5 mm clearance between the antenna and the housing (PC/ABS preferred).
- No metal within about 10 mm of the antenna end: battery pouch, MagSafe magnets/steel, LRA, display frame.
- SW4 (metal-shell side switch) sits on the same edge just past the antenna keep-out: its body edge is about 2.1 mm (courtyard 1.6 mm) from the keep-out end at y = 176.57, and its centre is 4.4 mm away. That is well inside the 10 mm "tall/large components" guideline. See LAY-05 (MEDIUM).
**Evidence:** SIM §2.2.7, Fig 6; DS Fig 16.
> **Reviewer note:** The original text put SW4 "about 5 mm from the antenna end". I measured body edge 2.1 mm and courtyard 1.6 mm from the keep-out end (SW4 at (166.88, 180.96), rotated 90°, Fab body ±2.25 mm). I corrected the text. The severity disagreement with LAY-05 (MEDIUM) is resolved in favour of LAY-05.

#### [INFO] CON-17 Housekeeping
- Neither project table registers the ECMF02-2AMX6 library. The DRC reports `lib_footprint_issues … does not include the footprint library 'ECMF02-2AMX6'`, and sym-lib-table has no entry either. The design still uses the embedded copies, but library updates and checks won't propagate. Add it to fp-lib-table and sym-lib-table.
- U6 is wired with DIRTY_D- on filter channel 1 (pins 1/6) and DIRTY_D+ on channel 2 (pins 2/5). The channels are identical and polarity is preserved end to end (J3 A6/B6 -> U6.2 -> U6.5 -> HHSDPA F2), so this is fine. It was presumably done for routing.
- The MAYA is MSL 4. Make sure JLC bakes it or handles it per J-STD-033.

### Design rationale

**Wireless (MAYA-W386, CYW55513)**
- The W386 variant is chosen because it carries an on-module niche antenna (Abracon). The board needs only the K9-L9 link and a keep-out at the board edge, with no RF connector or antenna part. This keeps the FCC/RED modular grant if the u-blox layout rules are followed.
- The single shared antenna variant time-shares 2.4 GHz Wi-Fi and BT with a shared LNA (fine for a DAP).
- Power: 3V3 (RF/PA) comes from MCP16502 Buck1 and 1V8 (I/O) from LDO2. On the MCP16502**AB** variant LDO2 is OFF at power-up and is enabled over I2C. So 1V8 always comes up after 3V3, which satisfies the u-blox rule "3V3 before or with 1V8, never 1V8 first" without extra parts.
- All MAYA digital I/O is 1.8 V. The designer therefore placed every host-side signal on 1.8 V SAMA7 banks:
  - SDMMC2 on VDDSDMMC2 = +1V8;
  - BT UART on FLEXCOM2 (PB8-PB12) and PCM on I2SMCC0 (PB14-PB18), both on VDDQSPI0 = +1V8, reusing the QSPI0 pins because there is no QSPI flash;
  - EN/WAKE GPIOs on VDDIOP1 = +1V8.
  No level shifters are needed. (I verified the power rail of every pin against pinout_table.html.)
- SDIO 3.0 SDR50 over SDMMC2 at a fixed 1.8 V I/O gives up to 50 MB/s, enough for 143 Mbps PHY. The pull-ups are within u-blox's 10-100 kΩ (DAT) range.
- The UART has RTS/CTS because u-blox makes hardware flow control mandatory at up to 4 Mbaud. The crossover is correct:
  - FLEXCOM2_IO0 TXD -> UART_RX;
  - IO1 RXD <- UART_TX;
  - IO4 RTS -> UART_CTSn;
  - IO3 CTS <- UART_RTSn.
- PCM/I2S (ASI_BT) goes to the SAMA7 I2SMCC0, not to the codec. The module's PCM supports only 8/16 kHz voice (NBS/WBS), so this path is only for HFP calls, which the SAMA7 can mix and route to the TAC5212. Music (A2DP / LE Audio LC3) travels over HCI UART and is decoded on the host, so 4 Mbaud is adequate.
- The external 32.768 kHz crystal (Y3, ±20 ppm, CL 7 pF with 9 pF caps, giving about 6-6.5 pF effective) is needed because the internal LPO "is only adequate for WLAN, and not for Bluetooth". The SC-32S footprint (1.0×1.8 pads at ±1.25 mm) matches the Seiko land pattern, and there is no copper under the crystal on B.Cu. The slightly low effective load gives about +10-20 ppm, well within the ±250 ppm LPO requirement. SLP_CLK_IN_OUT is correctly left open: it becomes a clock output when a crystal is used, and all pins have keepers.
- JTAG_SEL is tied to GND (u-blox: pull down if JTAG is unused, which also enables the coex GPIOs). WAKE lines have 10k pull-downs so they are defined while the host sleeps. The WL_HOST_WAKE OOB IRQ is on PD1.

**SD cards**
- There are two independent SDMMC controllers: SDMMC1 for the internal OS card (J6, the SAMA7 ROM boot source) and SDMMC0 for the user card (J7, push-push).
- They run at 3.3 V to avoid a switchable I/O rail.
- 47k pull-ups on CMD/DAT0-3 hold the bus idle-high (SD spec 10-100k). The CLK correctly has no pull-up. CD has a 10k pull-up to 3.3 V on VDDIN33/VDDIOP0-powered pins.
- There are no series resistors because the SAMA7 HSIO drivers are impedance-calibrated (16.9k RZQ, Type-D about 84 Ω at 3.3 V) and act as source termination at 50 MHz. Traces are 50 Ω (0.1072 mm on outer layers over In1/In4).

**USB**
- The HRO TYPE-C-31-M-12 (C165948) is the common JLC USB2-only receptacle. Per the jlcsearch mirror it is currently an Extended part, not Basic (reviewer correction). Its pads are identical to the KiCad stock footprint.
- The ST ECMF02-2AMX6 combines a common-mode choke (-20 dB at 0.8-2.2 GHz, protecting the WiFi/BT bands from USB common-mode noise next to an on-board antenna) with IEC 8 kV contact ESD on D+/D-. It is the right choice in a radio product.
- There is no Rd on CC because the BQ25640 integrates a full Type-C CC controller with Rd/Rp, DRP, Try.SNK/Try.SRC, and auto-OTG at 5 V up to 3.2 A. That is how "OTG to charge earbuds" works: software sets CC_MODE=DRP (or SRC with CC_AUTO_OTG=1), and the BQ boosts the battery onto VBUS. The SAMA7 HHSDPA/HHSDMA (port A, UDPHS + UHPHS) data role must follow VBUS_STAT read over I2C.
- The USB pair is routed as 0.089 mm/0.12 mm gap on B.Cu over In4, which is about 90 Ω. It is matched to 0.1 mm (38.14/38.04 mm). The shield is tied to GND, which is common for small handhelds.

### Verified OK
- IC2 symbol: all 90 pin numbers and names match MAYA-W3 DS Table 20 / Fig 15. NC pins A6/A8, RF_CNTL3 (DNC on W3x6), RF_ANT0 (NC on W386) are left open. All 33 GND pads are connected.
- IC2 footprint:
  - 0.6×0.6 mm pads on a 1.1 mm grid with inner columns at ±0.55 mm (rows D-J);
  - row offsets F->A 5.5 mm, F->M 7.4 mm, F->L 5.9 mm;
  - outline 10.4×14.3 mm;
  - RF keep-out polygon on all copper layers, matching DS Fig 16;
  - placement at the board edge per SIM Fig 6.
- MAYA power pins 3V3 = +3V3 (3.13-3.6 V OK), 1V8 = +1V8 (1.71-1.89 V OK). Supply sequencing is satisfied by the MCP16502AB LDO2 default-off behaviour.
- Every MAYA-to-SAMA7 signal is on a 1.8 V SAMA7 bank (VDDSDMMC2, VDDQSPI0, VDDIOP1 = +1V8).
- UART TX/RX/RTS/CTS crossover is correct. FLEXCOM2 IO0/1/3/4 all use I/O set 2.
- PCM DIN/DOUT crossover is correct (I2SMCC0_DOUT0 -> PCM_DIN, I2SMCC0_DIN0 <- PCM_DOUT). I2SMCC0 CK/WS/DIN/DOUT/MCK all use I/O set 3.
- Y3 footprint versus the Seiko SC-32S land pattern is correct. Load caps are C0G 9 pF.
- The ANT trace width of 0.115 mm is about 50 Ω on the outer layer over the 0.0764 mm prepreg.
- U6 ECMF02-2AMX6: pin 1 D+, 2 D-, 3 GND, 4 NC, 5 D-, 6 D+ (top view, channels 1↔6 and 2↔5). Symbol and footprint pad positions match DS Fig 1; pads are slightly longer than the Fig 17 land pattern, which is acceptable.
- J3 footprint is identical (pad by pad) to KiCad stock `Connector_USB:USB_C_Receptacle_HRO_TYPE-C-31-M-12`. A6/B6 = D+, A7/B7 = D-, and CC1/CC2 go separately to the BQ CC1/CC2.
- D+/D- polarity from J3 to the SAMA7 is correct. Length match is 0.1 mm. The diff impedance is about 90 Ω (calculated) for the 90 Ω profile.
- The J7 TF-015 footprint matches the XYECONN recommended layout: Cd, 8..1 at 1.10 mm pitch, 0.7×1.6 mm pads, 2 holes 8.00 mm apart, pad row 10.2 mm from the holes.
- J6 TF-008 pin order 1-8 at 1.1 mm pitch matches the drawing. The detect switch has two terminals; see CON-06 for polarity.
- SD pull-ups of 47k are within 10-100k. CD pull-ups of 10k go to the correct 3.3 V rail. SDMMC0/1 CAL = 16k9 is correct for 3.3 V.
- BQ25640 VBUS has 1 µF at the IC (C88). Total VBUS capacitance at the receptacle (C113+C127 = 2 µF) is well under the Type-C 10 µF sink limit.
- WiFi SDIO bus lengths of 19-28 mm are far under the 100 mm maximum, and traces are 50 Ω (0.1072 mm).

### Datasheets used
- u-blox MAYA-W3 data sheet UBXDOC-465451970-2050 R05: https://content.u-blox.com/sites/default/files/documents/MAYA-W3_DataSheet_UBXDOC-465451970-2050_0.pdf. Local: SCR/datasheets/MAYA-W3/maya_ds.pdf (.txt, pins-23.png, mech-40.png).
- u-blox MAYA-W3 system integration manual UBXDOC-465451970-2522 R02: https://content.u-blox.com/sites/default/files/documents/MAYA-W3_SIM_UBXDOC-465451970-2522.pdf. Local: SCR/datasheets/MAYA-W3/sim.pdf, sim.txt.
- ST ECMF02-2AMX6 DocID17815 Rev 3: https://www.st.com/resource/en/datasheet/ecmf02-2amx6.pdf (mirror used: https://static.chipdip.ru/lib/818/DOC034818004.pdf). Local: SCR/datasheets/ECMF02-2AMX6/ecmf.pdf.
- TI ESD441 SLVSH26C: https://www.ti.com/lit/ds/symlink/esd441.pdf. Local: SCR/datasheets/ESD441/esd441.pdf.
- TI BQ25640 SLVSIK1: https://www.ti.com/lit/ds/symlink/bq25640.pdf. Local: SCR/datasheets/bq25640/ (fetched by another agent).
- Microchip SAMA7D6 DS60001851E. Local: SCR/datasheets/SAMA7D65/ds.txt (fetched by another agent). Also hardware/pcb_lib/SAMA7D65-4HB/pinout_table.html.
- Microchip MCP16502 DS20006275D. Local: SCR/datasheets/mcp16502/.
- SOFNG TF-008 (LCSC C428465): https://www.lcsc.com/datasheet/C428465.pdf. Local: SCR/datasheets/TF-008/real.pdf.
- XYECONN TF-015-ZYD9AH1.85 (LCSC C20613194): https://www.lcsc.com/datasheet/C20613194.pdf. Local: SCR/datasheets/TF-015/real.pdf.
- Seiko SC-32S (LCSC C97604): https://www.lcsc.com/datasheet/C97604.pdf. Local: SCR/datasheets/SC-32S/real.pdf.

---

# Peripherals (audio, display, haptics/touchpad, buttons, touchpad PCB)

Reviewer domain: /Audio/, /Display/, /Touchpad/, /Buttons/ sheets of hardware/pcb and the hardware/pcb_touchpad board.
Sources: SCR/main/* (regenerated 22:02; my nets unchanged vs. the first dump), SCR/touch/*, meko.kicad_pcb, touchpad.kicad_pcb, hardware/cad/meko.step (Fusion assembly, used for FPC orientation), datasheets listed at the end.

### Summary
Pinouts check out for TAC5212 pins 1-24 and the EP, DRV2605L (DGS), IQS7211E (QFN20), PJ-342, PJ-242, the Sharp LS022B7DH03 FPC (J8) and the 5-pin touchpad FFC (J9 to J1). I traced both FPC links through the 3D assembly and pin 1 lands on pin 1 in both, so nothing is mirrored. No I2C address conflicts. I found three HIGH issues:
- AUD-01: the headphone jack-detect wiring can't produce a valid logic level.
- AUD-02: the generic VQFN-24 footprint is missing the TAC5212's four corner VSS pins.
- TP-01: the touchpad electrodes are wired 7 Rx x 6 Tx. That needs 24 sensing cycles and the IQS7211E maximum is 21, so the full 7x6 pad cannot be scanned.
MEDIUM issues:
- MICBIAS has no decoupling capacitor.
- The jack pins have no ESD protection.
- The headset mic bias headroom is marginal.
- The display's VCOM is hard-wired to serial mode, and this panel needs COM inversion at 57 Hz or more.
- The IQS7211E VDD and VREG capacitors are below the values Azoteq requires.
- Reviewer pass: I re-verified all HIGH and MEDIUM findings plus the I2C map. No findings removed and no severities changed. Notes added under AUD-01/02/03/05, TP-01/02, DISP-01, AUD-10 and the I2C map.

### Findings

#### [RESOLVED] AUD-01 Headphone jack detect (~DET_3.5mm / ~DET_2.5mm) never gives a valid logic level
> **✅ Resolved (2026-11-27):** both detect nets now go to ADC inputs: `~DET_3.5mm` → U1.G8 PC3/**AD0**, `~DET_2.5mm` → U1.H7 PC10/**AD5** (Table 8.1, DS60001851E pp. 27–28). Main-board DRC: 0 unconnected, 0 parity issues. ADVREFP = VDDANA = +2V5, so unplugged (1.65 V) reads about 2700 counts and plugged (0 V) about 0; threshold around 1000–1500 counts with debounce. **Firmware:** PC3 and PC10 reset with the internal pull-up enabled ("PIO, I, PU, ST"), and assigning a pin to the ADC does not change its PIO configuration (DS p. 41 note 2). Set `bias-disable` in the device tree. Detecting an unplugged jack still needs the codec powered, because the 1.65 V comes from VCOM. If audio plays with nothing plugged in it rides on the detect line, so average a few samples.
>
> *Original severity: HIGH. The original finding is kept below for reference.*
**Where:** /Audio/: J4.TN, R41 (100k to GND), U1.AA16 PE8. J5.TN, R42 (100k to GND), U1.AA19 PE10. J4.T = LEFT+ (OUT1P), J5.T = RIGHT- (OUT2M).
**Issue:** On both jacks TN is the normally-closed contact on the tip spring. The PJ-342 drawing shows terminal 3 (tip spring) with switch 4, and the PJ-242 shows 6 (tip) with switch 7. So when nothing is plugged in, the DET net is tied to a codec output that sits at the DAC common-mode voltage (1.65 V typ with AVDD = 3.3 V, TAC5212 DS §6.5 "Output Common Mode"). With a plug inserted, DET is pulled to 0 V. The designer's JOURNAL ("DET_x lines sit at around 1.65V") confirms this is the intended scheme.
- 1.65 V is VDDIO/2 on a 3.3 V bank, which is in the undefined band for a CMOS/Schmitt input (VIL ≤ ~0.3·VDD, VIH ≥ ~0.7·VDD). The exact SAMA7D65 VIH/VIL table is not in the downloaded datasheet, so the precise limits still need verification, but 1.65 V sits mid-supply either way.
- When the codec is in sleep or shutdown, VREF and the output stages are off. The outputs are then ~0 V or Hi-Z, so DET reads "inserted" even with no plug.
- At reset PE8 and PE10 come up with the internal pull-up enabled (pinout_table: "PIO, I, PU, ST"). That pull-up fights the 100k pull-down and injects DC into OUT1P/OUT2M until Linux reconfigures the pins.
- The result is that detection only works, at best, while the codec actively biases its outputs, and even then the level is marginal. It also can't wake the system from codec sleep.
**Evidence:** nets.txt `/Audio/~{DET}_3.5mm (3): J4.TN, R41.2, U1.AA16(PE8)` and `/Audio/LEFT+ (3): IC3.20(OUT1P), J4.T, J5.R2`. PJ-342 circuit diagram and parts table (C668606 p1). TAC5212 SLASF23A Table "Output Common Mode 1.65 V (AVDD = 3.3 V)".
**Recommendation:** Use a jack with an isolated detect switch (a separate normally-open or normally-closed contact that doesn't share the tip signal), wired to GND with a GPIO pull-up. Alternatively, feed DET to a comparator or an ADC input rather than a digital GPIO. As a stop-gap without a respin: keep the codec outputs biased at all times and use the TAC5212's built-in headset detection through MICBIAS/IN1 (JACK_DET_CFG0..3, P0_R25..R28). That covers the 3.5 mm jack only, and it needs a MICBIAS capacitor (see AUD-03). Also disable the PE8/PE10 internal pull-ups in the device tree.
> **Reviewer note:** Confirmed. PJ-342 drawing: 3 = right spring with fixed contact 4 normally closed; footprint T = drawing pad 3, TN = pad 4 (pad positions match the top-view land pattern, not mirrored). PJ-242: 6 = tip spring, 7 = its NC contact; footprint T/TN = 6/7. So unplugged, DET = OUT1P (J4) / OUT2M (J5). TAC5212 output common mode is 0.6 x VREF = 1.65 V (VREF 2.75 V) or AVDD/2 = 1.65 V (OUTxx_VCOM); both options give the same level, so no register setting moves it out of the band. SAMA7D6 DS60001851E Table 85.17 gives VIL max 0.3 x VDD = 0.99 V and VIH min 0.7 x VDD = 2.31 V at 3.3 V (hysteresis ≥150 mV), so 1.65 V is in the undefined band. The open item in the finding is now resolved. HIGH stands.

#### [HIGH] AUD-02 TAC5212 footprint has no pads for the four corner VSS pins (A1-A4), and its EP is larger than the package's exposed pad (Needs verification with TI)
**Where:** IC3, footprint `Package_DFN_QFN:VQFN-24-1EP_4x4mm_P0.5mm_EP2.45x2.45mm`, at (199.27, 130.67) rotated 45°.
**Issue:** The TAC5212 package is TI RGE0024R. It has four extra corner pins, A1-A4, all VSS: "Ground pin. Short directly to board ground plane" (Table 5-1). The note to §6.3 says "all ground pins must be tied together". The absolute maximum ratings list "VSS to VSS (thermal pad) ±0.3 V", which implies separately bonded ground nodes. The footprint (and the 25-pin symbol) has no pads at the corner positions, so those pins will not be soldered to anything. In addition, the RGE0024R exposed pad is SQ 2.1 ±0.1 mm and TI's land is 2.1 mm, while the footprint EP is 2.45 mm. The signal pads also start 0.3 mm further out than TI's land pattern (inner edge at 1.6 mm from centre vs 1.3 mm).
**Evidence:** IC3 pad dump from meko.kicad_pcb: 24 pads plus pad 25 = 2.45 x 2.45 mm, no A1-A4. TAC5212 DS §11 "RGE0024R package outline / example board layout": 4X SQ (0.25) corner pads at 2X 3.45 mm, EP SQ 2.1.
**Recommendation:** Before fabrication, make a TAC5212-specific footprint from TI's RGE0024R land pattern: a 2.1 mm EP, 0.24 x 0.6 mm signal pads, and four 0.25 mm square corner pads tied to GND. Add the A1-A4 pins to the custom TAC5x1x symbol (or give them as stacked/hidden GND pins). How much floating corner grounds would hurt can't be checked without TI's bond diagram. The fix costs nothing now and cannot be reworked after assembly.
> **Reviewer note:** Confirmed against TI drawing 4225246/A in SLASF23A: RGE0024R has 4X SQ 0.25 corner pads A1-A4 (centres at ±1.725 mm, 2X 3.45), EP SQ 2.1±0.1, land 24X 0.24 x 0.6 at 2X 3.8. Board IC3: 24 signal pads 0.25 x 0.775 centred at 1.9875 mm (inner edge 1.6 mm), EP 2.45 mm, no corner pads. Geometry check: the corner pins (1.6-1.85 mm on both axes) do not overlap any board pad, so there is no short; the only risk is four unsoldered ground pins. TI does not say whether A1-A4 are tie-bars to the die pad or separately bonded grounds. The "VSS to VSS (thermal pad)" abs-max line points to separate bonds. Kept HIGH because it cannot be reworked after assembly and the fix costs nothing. If TI confirms they are tie-bar anchors, it drops to LOW.

#### [RESOLVED] TP-01 Touchpad electrode assignment (7 Rx x 6 Tx) exceeds the IQS7211E's 21-cycle limit
> **✅ Resolved (2026-11-27):** touchpad electrodes re-assigned to 6 Rx × 7 Tx with a balanced 3 + 3 Rx split across Prox blocks A (RX0–3) and B (RX4–7), giving 7 × 3 = 21 cycles (IQS7211E DS Table 1.3 p. 3, §7.1.2–7.1.3 p. 24). Rows (Rx): ROW1 RX5, ROW2 RX6, ROW3 RX3, ROW4 RX1, ROW5 RX0, ROW6 RX4. Columns (Tx): COL1 TX12, COL2 TX2, COL3 TX11, COL4 TX10, COL5 TX7, COL6 TX8, COL7 TX9. Touchpad DRC: 0 unconnected, no net conflicts; the remaining 13 parity items are the harmless PAD_0_5MM footprint-link warnings. **Firmware:** Total Rxs = 6, Total Txs = 7, RxTxMapping (0x56–0x5A, §7.1.5) = `5, 6, 3, 1, 0, 4, 12, 2, 11, 10, 7, 8, 9`. Every cycle allocation (0x5D–0x7C) must pair one block A Rx (RX0/1/3) with one block B Rx (RX4/5/6) on the same Tx; the Azoteq GUI generates these. **Minor:** the ROW6 bottom-layer stub is 30.5 mm, against 2–10 mm for the other rows. Keep it from running long distances alongside column (Tx) traces, or it forms a small phantom sensing strip.
>
> *Original severity: HIGH. The original finding is kept below for reference.*
**Where:** Touchpad board U1: COL1-7 on RX6..RX0 (pins 11..5), ROW1-6 on RX7/TX7 and TX8..TX12 (pins 12..17).
**Issue:** TX8-TX12 can only be transmitters, so the 7 columns must be Rx and the 6 rows Tx. The IQS7211E senses one channel from Prox block A (Rx0-3) and one from block B (Rx4-7) per cycle, both on the same Tx (§7.1.2). Rx0-3 make 4 in block A against 3 in block B, so each Tx needs 4 cycles: 4 x 6 = 24 cycles against a maximum of 21 (§7.1.3). Table 1.3 lists exactly this combination (13 sensors, 7 Rx, 6 Tx, 24 timeslots) as "✗ not possible". The valid 13-sensor option is 6 Rx x 7 Tx (21 cycles), which is what Azoteq's reference schematic uses: RX0,1,2,4,5,6 as Rx and TX3, TX7-12 as Tx.
**Evidence:** touch/nets.txt `/COL7: U1.5(RX0/TX0)` … `/ROW6: U1.17(TX12)`. IQS7211E DS v1.4 Table 1.3 and §7.1.2-7.1.3.
**Recommendation:** Respin the touchpad board (2-layer, cheap). The 7 columns go to Tx pins (RX3/TX3, RX7/TX7, TX8-TX12) and the 6 rows to RX0-2 and RX4-6. This only reroutes the fan-out; the electrode pattern stays the same. Firmware workarounds with the current board, each giving reduced coverage:
- 7 Rx x 5 Tx (one edge row unused): 20 cycles.
- 6 Rx x 6 Tx (drop the RX0 = COL7 column): 18 cycles.
- Leave three block-A channels unallocated (§7.1.4).
Check the plan with Azoteq; they already reviewed an earlier version of this design.
> **Reviewer note:** Confirmed. touch/nets.txt: COL1-7 = U1.11..5 (RX6..RX0, all dual RX/TX pins), ROW1 = RX7/TX7, ROW2-6 = TX8-TX12 (Tx-only). Five rows are Tx-only, so the rows cannot become the Rx axis without a respin. All 13 electrodes are actually wired: there are 7 F.Cu zones per COL net and 8 per ROW net. IQS7211E DS v1.4 Table 1.3, 13 sensors / 7 Rx / 6 Tx: 42 channels, 24 timeslots, marked ✗. §7.1.3 limits the part to 21 cycles. Reference Fig. 2.1 uses Rx = RX0,1,2,4,5,6 and Tx = TX3, TX7-TX12. The cycle counts for the workarounds (20 and 18) check out.

#### [MEDIUM] AUD-03 MICBIAS pin has no decoupling capacitor
**Where:** IC3.14 MICBIAS: net +MICBIAS (2 nodes: IC3.14, R40.2).
**Issue:** TI's typical application puts 1 µF / 16 V on MICBIAS (Fig. 9-1). The layout guidelines say "Place the MICBIAS capacitor (with low ESR) close to the device". The MICBIAS noise spec (2 µVrms) is given with 1 µF. The jack-detect pulse width setting in JACK_DET_CFG0 assumes a 1 µF or 10 µF MICBIAS cap. Without it the mic bias is noisier, its stability is unspecified, and the built-in headset detect can't be used.
**Recommendation:** Add a 1 µF X5R/X7R (≥6.3 V) from MICBIAS to the VSS pad, right at pin 14.
> **Reviewer note:** Confirmed. The +MICBIAS net has 2 nodes (IC3.14, R40.2), with no capacitor.

#### [MEDIUM] AUD-04 No ESD protection on the user-accessible jack pins
**Where:** J4 and J5 contacts go directly to IC3.15/16/19/20/21/22 and to SAMA7 PE8/PE10 (DET).
**Issue:** The TAC5212 is rated ±2 kV HBM / ±500 V CDM (§6.2). Headphone plugs are a classic IEC 61000-4-2 (±8 kV contact) entry point, and the 2.5 mm balanced cables are often long and unshielded.
**Recommendation:** Add low-capacitance unidirectional TVS (5 V working voltage, <1 nF is irrelevant at audio, so pick for low leakage) on T, R1, R2, S of both jacks and on the DET lines. The ESD441 family already in pcb_lib is one option, close to the jacks with a short GND return. Alternatively, put 47-100 Ω series resistors between the codec and the TVS on MIC and DET.

#### [MEDIUM] AUD-05 Headset mic bias: low headroom and DC-coupled input loading
**Where:** R40 1k from +MICBIAS to MIC; MIC goes to IN1P and J4.S (CTIA sleeve). The headset ground ring (J4.R2) is LEFT- = OUT1M = VCOM (1.65 V), which is also IN1M.
**Issue:** The mic return sits at VCOM (1.65 V), not GND. With the default MICBIAS of 2.75 V only ~1.1 V minus I·R remains across the electret. At 0.3-0.5 mA through the 1k that leaves 0.6-0.8 V, below what many headset ECM JFETs need. The designer cut R from 2.2k to 1k for this reason, which also shifts the Android button thresholds. The input is DC-coupled with the default 5 kΩ ADC input impedance (Table 7-12) referenced to the ADC's internal common mode, so it loads the mic node. The differential DC offset (~0.5-1 V between IN1P and IN1M) uses part of the 2.83 Vpk full scale.
**Recommendation:** In firmware, set MICBIAS_VAL = "same as AVDD" (3.3 V gives ~1.65 V headroom; P0_R77[3:2] = 11), ADC_CH1_IMP = 40 kΩ, and ADC_CH1_CM_TOL = 10 (rail-to-rail); the digital HPF removes the DC. In hardware, consider 1 µF AC-coupling caps on IN1P and IN1M (TI recommends AC coupling for best DR/THD) and restoring the bias resistor to 2.2k once MICBIAS = AVDD. Test with a few real headsets.
> **Reviewer note:** Confirmed. LEFT- (IC3.16 IN1M, IC3.19 OUT1M, J4.R2, J5.S) sits at VCOM. Per Table 7-16, the MICBIAS default is 2.75 V (= VREF) and MICBIAS_VAL = 11 gives AVDD.

#### [MEDIUM] DISP-01 VCOM (COM inversion) mode is hard-wired to serial, but this panel needs ≥57 Hz inversion
**Where:** J8.4 EXTCOMIN to GND, J8.8 EXTMODE to GND.
**Issue:** The wiring is legal per Sharp Note 4-2 ("Lo mode: connect EXTMODE and EXTCOMIN to VSS"). However, the LS022B7DH03 specifies COM inversion fV = 57-140 Hz in serial mode (Table 6-3-1), and Table 4-1-1 ※1 says "a periodic signal transmission is necessary". So the SAMA7 must send an SPI transaction (M1 toggle) at least 57 times a second, forever, including while "idle" and while the SoC is suspended. Leaving the panel without inversion puts DC on the liquid crystal (image retention or degradation). The mainline Linux sharp-memory driver's software VCOM mode is designed around the ~1 Hz requirement of other Sharp panels. Using a hardware EXTCOMIN clock (PWM or timer) would let the display stay on through system suspend, but EXTMODE is tied low, so that option doesn't exist.
**Recommendation:** Add a resistor option: EXTMODE to VDD through a 0 Ω/DNP pair, and EXTCOMIN to a PWM- or TC-capable SAMA7 pin. PA21-PA25 already offer PWMH/PWML, or use a PCK output, with a 0 Ω/DNP to GND. Alternatively, plan to blank the panel (DISP low) before suspend and confirm with Sharp whether inversion is needed while DISP = Lo.
> **Reviewer note:** Confirmed, with an extra point. Table 6-3-1: with EXTMODE = Lo, COM inversion fV is 57-140 Hz (tV ≤ 17.5 ms) and fCOM is 28.5-70 Hz. With EXTMODE = Hi, fEXTCOMIN is also 57-140 Hz (Table 6-3-2). Both modes need about 60 Hz inversion; only the hardware mode can do it without the CPU. A full 240 x 320 frame at fSCLK ≤ 2 MHz takes about 41 ms in a single SCS transaction (see DISP-02). That is longer than the 17.5 ms tV maximum, so in serial-VCOM mode full-screen writes must also be split into chunks of about 130 lines or fewer to keep the M1 toggle in spec. This strengthens the case for the EXTCOMIN/EXTMODE resistor option. MEDIUM stands.

#### [MEDIUM] TP-02 IQS7211E decoupling below Azoteq requirements
**Where:** Touchpad board: C3 1 µF on VDD; C1 1 µF on VREGA; C2 1 µF on VREGD (all CL05A105KO5NNNC).
**Issue:** Azoteq §13.1.1 recommends 4.7 µF plus 100 pF on VDD. §13.1.2 says "Each VREG pin requires a 2.2 µF capacitor". The internal LDOs' stability and noise (which affects touch SNR) are specified with 2.2 µF.
**Recommendation:** Change C1 and C2 to 2.2 µF and C3 to 4.7 µF, and add 100 pF on VDD (0402 X5R parts are fine at 1.5-3.3 V). Do this in the TP-01 respin.
> **Reviewer note:** Confirmed. IQS7211E DS §13.1.1: 4.7 µF + 100 pF on VDD. §13.1.2: "Each VREG pin requires a 2.2 µF capacitor". Fig. 2.1 shows 2.2 µF + 100 pF on each VREG. Touchpad C1, C2 and C3 are all 1 µF CL05A105KO5NNNC.

#### [LOW] AUD-06 Codec supply decoupling is thinner than TI's typical application
**Where:** AVDD: C117 10 µF (0402, 6.3 V, CL05A106MQ5NUNC) plus C93 1 µF at the LDO. IOVDD: C116 10 µF 0402. DREG: C114 1 µF. VREF: C115 1 µF.
**Issue:**
- TI Fig. 9-1 shows 0.1 µF plus 10 µF on AVDD, IOVDD and DREG, and 1 µF on VREF.
- There are no 0.1 µF high-frequency caps on AVDD or IOVDD.
- The 10 µF 0402 parts derate to ~4 µF at 3.3 V.
- DREG has only 1 µF. The text doesn't state a minimum, so this needs verification against TI's EVM.
- VREF at 1 µF meets the "minimum 1 µF" requirement.
**Recommendation:** Add 0.1 µF 0201 caps at pins 23 and 6. Consider 2.2-10 µF on DREG per the EVM.

#### [LOW] AUD-07 Shared VCOM headphone return trace adds L/R crosstalk
**Where:** LEFT- (OUT1M/VCOM) runs ~17 mm of 0.2 mm track plus one via to J4.R2. OUT2M is not used as a common-mode sense in 3.5 mm mode (it goes only to J5.T).
**Issue:** The return impedance is ~40-50 mΩ shared by both channels. Into 16 Ω that is about -50 dB of crosstalk, before jack contact resistance. TI's mode 101 (OUT2M as external CM sense) can't be used because OUT2M is wired to the 2.5 mm jack, which was the designer's deliberate trade-off.
**Recommendation:** Widen LEFT- to ≥0.4 mm (and RIGHT+/LEFT+ if space allows) and route it as a short, direct return. Configure OUT1x_CFG = 100 / OUT2x single-ended in 3.5 mm mode.

#### [LOW] AUD-08 Codec AVDD LDO is always on
**Where:** U3 TPS7A2033: IN and EN both on +VSYS, so +3V3_AVDD powers IC3.23.
**Issue:** AVDD stays powered when the PMIC and +3V3/IOVDD are off, which adds the LDO's quiescent current plus the codec's AVDD-only leakage to the off-state battery drain. TI allows any supply order, so this is not a functional fault. (Overlaps with the power review.)
**Recommendation:** Drive EN from +3V3 or a GPIO, or confirm the off-state drain is acceptable.

#### [LOW] AUD-09 3.5 mm "ground" is VCOM (1.65 V DC)
**Issue:** This is inherent to the capless pseudo-differential scheme (JOURNAL rationale). If the 3.5 mm output is connected to equipment whose ground is shared with Meko's ground, the VCOM driver is shorted to ground. Examples: a car AUX input while charging from the same car, or a USB-powered amp on the same charger. The TAC5212's output short-circuit protection will trip and/or the user hears hum.
**Recommendation:** Document it, and enable the OUT short-circuit interrupt (INT_MASK4) so the driver can mute and notify.

#### [LOW] I2C-01 10 kΩ pull-ups are too weak for 400 kHz on the 8-node shared bus
**Where:** R1/R2 10k to +3V3 on /Audio/SCL,SDA. That bus carries IC1 MCP16502, IC3 TAC5212, U4 BQ25640, U5 MAX17260, U7 DRV2605L, U1 FLEXCOM0 and TP1/2. Also R4/R5 10k on TOUCH.SCL/SDA, which runs through the FFC.
**Issue:** At 50-80 pF, tr ≈ 0.85·R·C is 420-680 ns, which exceeds the 300 ns fast-mode limit. DRV2605L DS §8.5.1 recommends 660 Ω-4.7 kΩ; Azoteq's reference uses 4.7 kΩ.
**Recommendation:** Use 2.2-4.7 kΩ, or run the buses at 100 kHz.

#### [LOW] DISP-02 The 70 Hz full-frame claim is not reachable at the panel's 2 MHz SCLK limit
**Issue:** fSCLK max = 2.0 MHz (Table 6-3-2). A full frame is about 320 lines x (9 address + 240 data + dummy bits), roughly 82 kbit. That gives a maximum of ~24 fps for full-screen updates; 70 Hz is only possible for partial updates of ≤ ~110 lines. Not a hardware bug, but it affects the README claim and UI design.

#### [LOW] DISP-03 +3V3 tolerance vs. the LS022B7DH03 recommended range
**Issue:** The panel's VDD/VDDA recommended range is 3.05-3.35 V (abs max 3.6 V). +3V3 comes from MCP16502 Buck1, accuracy ±2% (DS Table "Output Voltage Accuracy"), so it can reach 3.366 V before ripple. That is inside abs max but can sit just above the recommended maximum.
**Recommendation:** Optionally program Buck1 to 3.25 V. Check that the other 3V3 loads accept it: SAMA7 VDDIO, TAC5212 IOVDD (3.0-3.6 V) and IQS7211E all do.

#### [LOW] DISP-04 SCS/SCLK are pulled high by the SAMA7 reset pull-ups during boot
**Where:** PA21 (SCS) and PA22 (SCLK) reset state is "PIO, I, PU".
**Issue:** Sharp: "Keep Lo serial signal (SCS/SI/SCLK) without communicating. Not to make SCS Hi when it does not communicate" (Table 4-1-1 note 5). DISP has a 10k pull-down (R55), so nothing is visible on screen, but the spec is violated during boot.
**Recommendation:** Add a 10k pull-down on SCS. In the device tree use `cs-gpios` with `spi-cs-high`, because SCS is active-high and the FLEXCOM SPI's native NPCS is active-low.

#### [LOW] BTN-01 Side/volume buttons: no ESD protection or RC filter; wake capability is limited
**Where:** SW2 (PE4), SW3 (PE5), SW4 (PA27), SW5 (PA29): switch to GND, no external pull-up.
**Issue:**
- The buttons rely on the SAMA7 internal pull-up (on by default) and PIO debouncing (PIO_CFGR IFSCEN). That is acceptable.
- Pin voltage domains are fine: VDDLVDS and VDDGMAC0 are both on +3V3.
- The switch frames (MP) are grounded, which shunts most ESD.
- None of these buttons can wake the system from Backup mode or power-off; only WKUP0 and PIOBU can. Waking from ULP0/ULP1 via PIO interrupts needs checking in the SAMA7 PM documentation.
**Recommendation:** Optionally add 100 nF to GND at each switch, plus a TVS if the actuators are metal. Document that only the power key wakes the device from off/backup.

#### [LOW] BTN-02 Power-key runtime events are hard to use from Linux
**Where:** SW1 to R56 10k to nSTRT (IC1.24), with C126 100 nF. nSTRTO goes to ~WKUP (SAMA7 WKUP0). A long press produces PBINT on nINTO (/Power/~INT, PC12).
**Issue:** Power-up from off works as Microchip intends: 10k against the internal 40k pull-up gives 0.2·SVIN, below VIL of 0.36·SVIN. At runtime, though, a short press is only visible as the WKUP0 level inside SHDWC, which has no mainline input driver, and the PMIC reports only long presses (t8 + t9) on nINTO.
**Recommendation:** If a short-press "suspend / screen off" is wanted, also route ~WKUP (it is open-drain and pulled up) to a normal GPIO through a resistor, or use one of the side keys. Also note that C126 (100 nF) with the 40 kΩ internal pull-up gives τ ≈ 4 ms. The MCP16502 DS uses exactly a capacitor on nSTRT to trigger auto-start when VIN ramps, so check whether the board auto-boots on battery insertion or charger revival. Needs verification; this may be intended.

#### [LOW] TP-03 IQS7211E-QNR exposed corner GND pads sit over the COL7 and +3V3 tracks
**Where:** Touchpad U1 at (154.40, 129.31), rotated -135°, B.Cu. Tracks /COL7 and +3V3 pass under two package corners.
**Issue:** Order code QNR has exposed corner pads tied to TAB (GND). Azoteq footprint note 6: "Solder mask (or exposed copper keep-out) areas necessary to avoid any traces shorting to exposed corner pads." Here only the solder mask insulates them.
**Recommendation:** Reroute those tracks away from the corners in the TP-01 respin, or use the QFR order code.

#### [LOW] MECH-01 J9 FFC slot is very tight on one side (Needs verification)
**Where:** Main-board Edge.Cuts rectangle (170.79, 161.97)-(178.79, 164.47). J9 centre x = 172.54.
**Issue:** The slot is offset by +2.25 mm to leave room for the LRA leads. A ~3.2 mm-wide 5-circuit FFC centred on J9 spans x ≈ 170.94-174.14, leaving only ~0.15 mm clearance to the slot's left edge.
**Recommendation:** Extend the slot by about 0.5 mm toward -x. Confirm the FFC width on Molex's 503480 drawing.

#### [LOW] SI-01 ASI and SPI lines have no source termination
**Where:** /Audio/BCLK ~58 mm of 0.1 mm track with 3 vias; display SCLK ~85 mm.
**Recommendation:** Use the SAMA7 PIO slew-rate and drive settings, or add 22-33 Ω series resistors at the SoC, to avoid ringing and double-clocking on BCLK. The test points TP50-53 make this easy to check on the first boards.

#### [INFO] HAP-01 Haptics implementation
- U7 DRV2605L pin mapping matches DGS Pin Functions (1 REG … 10 VDD).
- VDD and VDD/NC are both on +3V3, inside the 2-5.2 V range.
- REG has 1 µF (C125), as required.
- VDD has 1 µF (C124, on F.Cu ~3 mm from U7). TI also recommends 0.1 µF low-ESR on VDD; consider adding it.
- IN/TRIG is tied to GND, the datasheet's "unused" handling, so only I2C/RTP/library playback is available (no audio-to-vibe or external trigger).
- EN is driven by PE11 (HAPT_EN, with TP65).
- The C10-100 LRA is not on the FFC. In the STEP assembly it is mounted on the touchpad assembly ("touchpad 1/LRA"), and its leads go through the widened FFC slot to TP63/TP64 (2 mm pads, 0.3 mm traces), so no LRA current flows through the FFC.
- Firmware must set RATED_VOLTAGE, OD_CLAMP and DRIVE_TIME from the C10-100 datasheet (rated drive voltage and resonance) and run auto-calibration.
- Provide strain relief on the soldered LRA leads.

#### [INFO] AUD-10 2.5 mm balanced pin-out convention
J5 has T = R-, R1 = R+, R2 = L+, S = L- (verified against the PJ-242 drawing: 2 = S, 3 = R2, 4 = R1, 5 = R1N, 6 = T, 7 = TN). That matches the Astell&Kern / FiiO style mapping reported on Head-Fi. Pentaconn's reference lists T = L+, R1 = L-, R2 = R+, S = R- instead. Confirm against a commercial balanced cable before release. Any mismatch is fixable in firmware (swap ASI slots and invert a channel).

> **Reviewer note:** Re-checked the PJ-242 drawing myself. Plug segments are 6 = tip, 4 = ring 1, 3 = ring 2, 2 = sleeve. In the circuit, 7 is NC to 6 and 5 is NC to 4. The land pattern maps to the footprint by a proper rotation, not a mirror. So J5 is T = R-, R1 = R+, R2 = L+, S = L-, which is the tip-to-sleeve order "R-, R+, L+, L-" that Head-Fi users quote for the A&K 2.5 mm standard. Still INFO; confirm with a cable before release.
#### [INFO] TP-04 Touchpad DRC items (SCR/touch/drc.rpt): real or not
- The 13 `footprint_symbol_mismatch` (COL1-7, ROW1-6 test pads) and the ERC `footprint_link_issues` are not real. The symbols point to the eagle-import library nickname `Touchpad:` while the board has the same PAD_0_5MM footprint; the nickname is simply missing from the fp-lib-table. The pads are DNP test points.
- `extra_footprint SYM1` (OSHW logo) is benign.
- The 12 "barcode visual separation" errors are real but cosmetic. The B.Silkscreen QR code overlaps COL6/COL7 vias, so silkscreen will be clipped at the vias and the code may not scan. Move it.
- `lib_footprint_mismatch U1` reflects a locally edited QFN footprint, which is fine.
- `silk_over_copper` near C2 is cosmetic.
- 0 unconnected items.
- The ERC `power_pin_not_driven` entries are just missing PWR_FLAGs.

### FPC orientation analysis (the requested CRITICAL check): both links are correct

**J9 (main) to J1 (touchpad), 5-pin FFC.**
- Netlist mapping: J9 pins 1..5 (+3V3, INT, SDA, GND, SCL) connect to J1 pins 5..1 (+3V3, RDY, SDA, GND, SCL). That is a full reversal, pin k to pin 6-k.
- Method: I parsed the Fusion assembly hardware/cad/meko.step (NAUO/ITEM_DEFINED_TRANSFORMATION). The two instances of the same 503480-0540 model have:
  - main J9 at (-17.72, 5.45, -6.84), model X → -X, model Y → -Z, model Z → -Y;
  - touchpad J1 at (-17.72, -11.85, -0.10), model X → +X, model Y → -Z, model Z → +Y.
- Geometry this gives:
  - Both connectors face -Z, as expected for B.Cu parts.
  - They are rotated 180° relative to each other in plane, matching KiCad J9 at 180° and J1 at 0°.
  - Their cable openings face each other along Y. This agrees with the footprints, where the MP side is the entry side for both J8 and J9 by the same rule.
- With a straight, untwisted FFC in an S-bend down through the main-board slot, each conductor keeps its world X position. Touchpad J1 pin 1 therefore lands on main J9 pin 5, which is exactly the reversed mapping in the schematic, so the schematics are consistent.
- The 503480 is dual-contact (Sharp's table lists 503480-1000 as "Bottom and Upper"), so either FFC type works electrically. With bottom-only contacts, a same-side ("Type A") FFC would be needed. Specify a 5-circuit, 0.5 mm-pitch, ~25-30 mm Type A FFC.

**J8 to the LS022B7DH03 FPC.**
- Pin order J8.1..10 = SCLK, SI, SCS, EXTCOMIN (GND), DISP, VDDA, VDD, EXTMODE (GND), VSS, VSSA. This matches Table 4-1.
- The panel's FPC contacts are on the rear surface; viewed from the rear with the tail down, pin 1 is on the left (Fig. 8-1-1/8-1-2).
- In the assembly the display front faces +Z and the FPC leaves the panel's -X edge. It wraps around the main board's -X edge notch (Edge.Cuts x = 165.13-166.13, y = 138.8-147.2) and enters J8, whose opening faces -X, travelling +X.
- A U-fold about Y keeps the Y order, putting FPC pin 1 at world -Y. J8 pad 1 is at KiCad y = 145.33, which is world -Y, and pad 10 at 140.83. So pin 1 lands on pin 1. After the fold the contacts face the PCB, which the dual-contact connector accepts.

### I2C address map
> **Reviewer note:** Table re-verified against the netlist and datasheets. /Audio/SCL,SDA nodes are IC1, IC3, U4, U5, U7, U1 (FLEXCOM0 IO1 = SCL H6, IO0 = SDA B1), R1/R2 and TP1/2. Addresses: TAC5212 0x50 (Table 7-72, ADDR shorted to GND), MCP16502 0x5B (default), DRV2605L 0x5A, BQ25640 0x6B (§7.5.1.5), MAX17260 0x36/0x0B, IQS7211E 0x56 fixed (§11.2). No conflicts. Correct.
| Bus (SAMA7) | Pull-ups | Device | Ref | 7-bit address | Source |
|---|---|---|---|---|---|
| FLEXCOM0 (PC6 SCL/H6, PC7 SDA/B1; VDDIN33 = 3V3) "/Audio/SCL,SDA" | R1/R2 10k to +3V3 | TAC5212 | IC3 | 0x50 (ADDR = GND; broadcast also 0x50) | DS Table 7-72 |
| | | DRV2605L | U7 | 0x5A | DS §8.5.1 |
| | | MCP16502 | IC1 | 0x5B (default) | DS §4.8.1 |
| | | BQ25640 | U4 | 0x6B | DS §7.5.1 |
| | | MAX17260 | U5 | 0x36 (also 0x0B for history/NV) | Maxim DS |
| FLEXCOM5 (PE2 SCL/K12, PE3 SDA/D20; VDDGMAC1 = 3V3) "TOUCH" | R4/R5 10k to +3V3 (main board) | IQS7211E (via FFC) | touch U1 | 0x56 (fixed) | DS §11 |

No conflicts. All pull-ups and device I/O supplies are on +3V3; the TAC5212 IOVDD, the DRV2605L and the IQS7211E all run from +3V3, so there are no level issues. RDY/INT uses R57 10k to +3V3 (open-drain RDY, internal 210k MCLR pull-up).

### Design rationale
- **Audio, capless pseudo-differential 3.5 mm.** The designer avoided DC-blocking caps, which cost bass response; the JOURNAL notes that v2 needed a bodge for exactly this. OUT1M is driven as VCOM and used as the headphone return (TAC5212 OUT1x_CFG = 100). IN1M sits on that same VCOM node so the mic (IN1P, CTIA sleeve) is read pseudo-differentially against the headset ground. The 1k bias resistor (instead of 2.2k) compensates for the raised return.
- **Audio, 2.5 mm balanced.** The same four DAC pins are reused in fully differential mode (OUT1P/M, OUT2P/M; 2 Vrms differential at AVDD = 3.3 V, DS §6.5). This gives the README's "2 Vrms balanced" without an analog switch. TI support advised that dropping the OUT2M common-mode sense costs only a little performance. Mode switching is done in software from jack detect, which is why AUD-01 matters.
- **Audio supplies and clocking.** AVDD comes from a separate low-noise LDO (TPS7A2033) fed from VSYS, after review feedback. IOVDD is +3V3 so the I2S/I2C levels match the 3.3 V SAMA7 banks (PC14-PC17 on VDDIN33). There is no MCLK: the TAC5212 PLL runs from BCLK in target mode (auto clock/ratio detection), and the I2SMCC1 is the bus controller. The codec doesn't connect to the Bluetooth module; BT audio uses a separate ASI_BT path to the SoC. GPIO1/GPIO2/GPO1/GPI1 go to SAMA7 GPIOs for IRQ or a future secondary ASI.
- **Display.** The Sharp MIP panel (not e-paper) gets the Sharp-recommended Molex 503480-1000 connector, which is dual-contact so the FPC can be folded either way. EXTMODE and EXTCOMIN are tied low (serial VCOM via M1) to save a pin. DISP has a 10k pull-down so the panel stays white until initialised. The SPI is on FLEXCOM3 I/O set 2 (PA24 MOSI, PA22 SPCK, PA21 NPCS0).
- **Touchpad.** The IQS7211E is on its own I2C bus (FLEXCOM5), isolating touch traffic and allowing Fm+ (1 MHz) operation. The touchpad board carries only the IC and local LDO caps; pull-ups and the RDY pull-up sit on the main board. A 5-pin FFC with the reversed pin order is correct for 180°-opposed connectors (see the FPC analysis). The haptic driver stays on the main board on the shared I2C bus, and the LRA is mounted on the touchpad (moving) assembly and hard-wired.
- **Buttons.** The power key follows Microchip's MCP16502 + SAMA7 reference: PMIC nSTRT starts the PMIC, nSTRTO drives SAMA7 WKUP0, and SHDN drives PWRHLD. The series 10k plus 100 nF filters bounce and ESD. The other keys are plain GPIOs with internal pull-ups and debounce. The Alps SKRT shielded switches have grounded frames that act as the ESD return.

### Verified OK
- TAC5212 pins 1-24 and the EP (pin 25 = VSS) in the custom TAC5x1x symbol match DS Table 5-1. The ADDR strap is GND (0x50). VREF has 1 µF. AVDD and IOVDD are 3.3 V (3.0-3.6 V mode).
- ASI directions: SAMA7 I2SMCC1_DOUT0 (PC17) to codec DIN; codec DOUT to I2SMCC1_DIN0 (PC14); CK on PC16, WS on PC15.
- All peripheral GPIOs are on 3.3 V banks (VDDIOP0, VDDGMAC0/1, VDDIN33, VDDLVDS are all +3V3), so there are no over-voltage paths from the 3.3 V codec, haptic driver or touch IC.
- PJ-342 footprint pads (T/TN/R1/R1N/R2/S) match the LCSC C668606 land pattern, top view, not mirrored. CTIA mapping is T = L, R1 = R, R2 = GND(VCOM), S = MIC.
- PJ-242 footprint pads match the C431536 land pattern and terminal numbering.
- Note for assembly: the PJ-242 pad pattern and holes are symmetric under 180° rotation, so check the jack orientation in JLC's assembly preview (mouth toward the board edge).
- The Sharp LS022B7DH03 pinout, EXTMODE/EXTCOMIN Lo-mode wiring (Note 4-2), VDD = VDDA on one rail (VDD ≥ VDDA satisfied), C122 1 µF near J8, and VSS/VSSA joined at the connector are all correct.
- DRV2605L DGS pinout; REG cap; IN/TRIG unused handling.
- IQS7211E QFN20 pinout (VDD 1, VREGD 2, VSS 3, VREGA 4, RX0-7 5-12, TX8-12 13-17, SCL 18, SDA 19, RDY 20, TAB = GND). The 1.65 mm EP matches the QNR footprint. VDD 3.3 V is within the 1.71-3.6 V range.
- The FFC/FPC pin-1 mapping for both J8 and J9-J1 is correct.
- SKRTLAE010 wiring (pins 1 to GND, pin 2 to signal, MP to GND). The 84 µA nSTRT current is above the switch's 10 µA minimum rating.
- I2C address map: no conflicts.

### Datasheets used
- TI TAC5212 SLASF23A (Jan 2025): https://www.ti.com/lit/ds/symlink/tac5212.pdf → SCR/datasheets/TAC5212/tac5212.pdf (.txt)
- TI DRV2605L SLOS854D: https://www.ti.com/lit/ds/symlink/drv2605l.pdf → SCR/datasheets/DRV2605L/
- Azoteq IQS7211E datasheet v1.4: https://www.azoteq.com/images/stories/pdf/iqs7211e_datasheet.pdf → SCR/datasheets/IQS7211E/
- Sharp LS022B7DH03 spec LD-2022Z02A: https://d7rh5s3nxmpy4.cloudfront.net/CMP7377/files/LS022B7DH03_LD2022Z02A_230405.pdf → SCR/datasheets/LS022B7DH03/spec.pdf (rendered pages 25 and 47 for SCLK timing and FPC pin 1)
- SHOU HAN PJ-342 (LCSC C668606): https://datasheet.lcsc.com/datasheet/pdf/bcc8dec0db9ef8189a202e7c1231bfc0.pdf?productCode=C668606 → SCR/datasheets/PJ-342/C668606.real.pdf (crops crop-1.png, tbl-1.png)
- SHOU HAN PJ-242 (LCSC C431536): https://datasheet.lcsc.com/datasheet/pdf/13fe0be32f59ab7da3d6b413acb09fc1.pdf?productCode=C431536 → SCR/datasheets/PJ-242/C431536.real.pdf (lp-1.png, plug-1.png)
- Alps SKRTLAE010 (LCSC C110293) → SCR/datasheets/SKRTLAE010/C110293.real.pdf
- Microchip MCP16502 (fetched by the power agent) → SCR/datasheets/mcp16502/mcp16502.txt (nSTRT §4.3.2, pull-up 40 kΩ, VIL 0.36·SVIN, I2C 0x5B, ±2% Buck accuracy)
- TI BQ25640 (fetched by another agent) → SCR/datasheets/bq25640/bq25640.txt (I2C 0x6B)
- Microchip SAMA7D65 pin description table: hardware/pcb_lib/SAMA7D65-4HB/pinout_table.html (parsed to SCR/tools/sama_pinout.txt) for pin power rails and reset pull states
- Molex 503480 FBH1 (dual contact, back-flip). I couldn't download the drawing (molex.com blocked); the dual-contact status comes from the Sharp recommended-connector table and distributor listings.
- 2.5 mm balanced pin-out references: Head-Fi threads and the Pentaconn connector reference (conflicting, see AUD-10).
- Tools written: SCR/tools/fpinfo.py (footprint/pad/net dump), SCR/tools/steptree.py (STEP assembly transform walker)

---

# Layout, DRC & manufacturability

Reviewer domain: board-level layout, DRC triage, board setup vs JLC capabilities, plane integrity, antenna keep-out, assembly/BOM, silkscreen and outline.
Review target: `hardware/pcb/meko.kicad_pcb` as of commit e61034b (22 Nov 21:50: WiFi SDMMC pull-ups moved to 1V8, 10 µF C123 added on +BATT, impedance/stackup tables updated); re-triaged against the regenerated SCR/main/drc.rpt (22:02), `meko.kicad_pro`, `meko.kicad_dru`; touchpad `hardware/pcb_touchpad/touchpad.kicad_pcb`.
Tools: KiCad 10.0.8 `pcbnew` Python API (read-only load), `kicad-cli pcb drc --refill-zones` on a **copy** in `SCR/layout/proj/` (repo untouched). Scripts are in `SCR/tools/` (pcbstats.py, pcb2.py, zones.py, fpdiff*.py, ant*.py, fillchk.py, vias*.py, overhang.py, stitch.py, silk.py, holes.py, pwrtrk.py). Refilled DRC: `SCR/layout/drc_refill.rpt` (pre-fix) and `SCR/layout/drc_refill2.rpt` (current board, copy in `SCR/layout/proj2/`). Plane renders: `SCR/layout/img/In1.Cu.png`, `In2.Cu.png`, `In4.Cu.png`.

### Summary

- The board is manufacturable at JLCPCB as drawn. It uses through vias only (no blind or micro vias): 975 × 0.3/0.15, 41 × 0.45/0.225 and 55 × 0.6/0.3 (1071 total). The narrowest track is 0.0892 mm (3.5 mil) and the smallest real copper gap is 0.100 mm, both inside JLC's multilayer limits of 0.09/0.09 mm. The stackup matches JLC's 0.8 mm 6-layer "1080" build (JLC06081H-1080) exactly. The 0.65 mm-pitch SAMA7D65 fanout works with 0.3/0.15 vias, with no via-in-pad on the BGAs.
- The current DRC has 188 items and 0 unconnected. The +3V3/+1V8 short at R35 is gone (no shorting_items or solder_mask_bridge), and the stale-fill items are gone too: a refill-then-DRC run on a copy returns the same 188 items, so the stored zone fill is current. None of the 188 is a real electrical error. The 91 netclass/DRU clearance items are self-imposed signal-integrity spacing rules, all at 0.10 mm or more. Hole, silkscreen and library items are footprint-intrinsic or cosmetic. Two hole-spacing items (one pair at 0.166 mm, one duplicated via) need a trivial fix.
- Plane design is good: In1, In3 and In4 are solid GND, signals run only on F.Cu and B.Cu, and In2 (power) sits between two GND planes, so its splits cannot break a signal return path. The MAYA-W386 antenna keep-out matches u-blox Figure 6 and is clear on all six layers. The module sits on the board edge facing outwards.
- The main problems are ordering and assembly: JLC Standard PCBA needs edge rails and fiducials while parts overhang all four edges, and 4 ICs have no LCSC number. On the design side: the VBUS route is long and thin on 0.5 oz inner copper, and a metal side switch sits 1.5 mm from the antenna clearance area.
- Reviewer pass: I re-verified all MEDIUM findings. No findings removed and no severities changed. Correction: LAY-04 IPC-2221 figure (internal-layer, about 0.55 A at 10 °C, not 1 A).

### Findings

#### [RESOLVED] LAY-01 +3V3/+1V8 short at R35 and the 5 × +1V8 unconnected items (WiFi SDMMC pull-ups): fixed, verified
**Where:** R35 pad 1 (193.24, 178.76) B.Cu; +1V8 vias at (182.12, 178.57), (182.96, 179.13), (182.55, 175.27); R33, R36.
**Evidence:** The previous DRC had 4 shorting_items (+3V3 track vs R35.1 +1V8), 4 solder_mask_bridge, 5 unconnected_items, and 3 hole_clearance + 3 "GND and PWR reduced clearance" items at 0.0 mm (+1V8 vias inside a stale In2 +3V3 fill). The regenerated SCR/main/drc.rpt (22:02) has none of them: "Found 0 unconnected pads", no shorting_items, no solder_mask_bridge, no 0.0 mm hits. I ran `kicad-cli pcb drc --refill-zones` on a copy of the current board and got the identical 188-item set with 0 unconnected, so the zone fill saved in the board matches a fresh refill.
**Also checked:** the new C123 (10 µF 0402, C15525, +BATT/GND) sits on F.Cu at (170.98, 132.06), 2.3 mm from U4.14 (BAT), and adds no DRC items.
**Recommendation:** None. Keep refilling zones (B) before any plot.

#### [MEDIUM] LAY-03 JLC Standard PCBA needs edge rails and fiducials, and parts overhang every edge
**Where:** Board outline is 50.24 × 77.16 mm (Edge.Cuts bbox 165.13–215.37 × 123.44–200.60). Courtyard overhangs (`SCR/tools/overhang.py`): J4 top 1.95 mm, J3 (USB-C) bottom 1.83 mm, SW1 top 0.59 mm, SW2/SW3/SW5 right 0.59 mm, SW4 left 0.60 mm, J5 top 0.11 mm, J7 bottom 0.01 mm, J1 right 0.02 mm. IC2's courtyard extends 0.97 mm past the left edge because it includes the antenna keep-out; the module body is 0.13 mm inside the edge.
**Issue:** JLC's PCBA capability page lists, for Standard PCBA (which this board needs for BGAs, double-sided assembly and 0201 parts): minimum single PCB 70 × 70 mm, edge rails "Necessary", fiducials "Necessary". The board is narrower than 70 mm and has no fiducials or tooling holes. Overhanging connectors and switches on all four sides rule out plain V-cut rails. Copper-to-edge is 0.25 mm, below JLC's ≥0.4 mm V-cut rule but fine for routed edges (≥0.2 mm).
**Recommendation:** Either panelize yourself (for example with KiKit: 5 mm rails, mouse-bite tabs placed away from J3, J4, J5 and SW1–5, 3 fiducials and 4 × Ø1.152 tooling holes on the rails), or pick "edge rails added by JLCPCB" and state in the order notes that parts overhang all four edges, so the rails must be routed (milled) with a gap, not V-cut. Optional: add 2–3 local 1 mm fiducials per side near U1 and U2. The touchpad (41.4 × 30.4 mm) needs the same treatment if it goes through Standard PCBA. See LAY-19.
> **Reviewer note:** Confirmed against https://jlcpcb.com/capabilities/pcb-assembly-capabilities, fetched 2026-11-22. Standard PCBA: single PCB 70 × 70 to 460 × 500 mm, edge rails and fiducials "Necessary". Economic: 10 × 10 mm minimum, rails and fiducials not needed. The board is 50.24 × 77.16 mm. In practice the JLC order form offers "Edge rails/Fiducials: Added by JLCPCB", so the real risk is the parts overhanging every edge, not the size limit itself. MEDIUM stands.

#### [RESOLVED] LAY-04 VBUS path is 108 mm of 0.8 mm track, mostly on 0.5 oz inner copper
> **✅ Resolved (2026-11-27):** see PWR-04. VBUS is now an In2 pour plus a 1.25 mm B.Cu trace, ≈ 33 mΩ in total.
>
> *Original severity: MEDIUM. The original finding is kept below for reference.*
**Where:** Net VBUS: In2.Cu 0.8 mm × 87.9 mm (left edge, e.g. (165.78, 178.45)→(165.78, 199.28) and (165.78, 156.08)→(165.78, 163.88)), plus B.Cu 0.8 mm × 20.3 mm and 0.6 mm × 7.6 mm. It runs from J3 (USB-C, bottom edge) to U4.2 (BQ25640, top-left). 8 vias (4 × 0.6/0.3, 4 × 0.45/0.225).
**Issue:** At 15.2 µm (0.5 oz) inner copper, a 0.8 mm track is about 1.41 mΩ/mm. That gives about 124 mΩ on In2 plus about 12 mΩ on B.Cu, roughly 0.14 Ω in total. BQ25640 ICHG resets to 2000 mA at power-on (datasheet REG0x02, "POR: 2000mA"), and IINDPM can reach 3.2 A ("IINDPM will default to 3.2A" for unknown adapters with EN_ICO = 0, §7.3.3.1, and 3 A from a USB-C Rp). Realistic input current is therefore 2–2.5 A: about 0.3 V drop and 0.6–0.9 W dissipated along a thin inner track. IPC-2221 (internal-layer curve, k = 0.024) puts 0.8 mm × 15.2 µm (≈18.8 mil²) at only about 0.55 A for a 10 °C rise and about 0.75 A for 20 °C. Adjacent GND planes help (IPC-2152), but a rise of 20–40 °C at 2.5 A is plausible. The drop also eats into VBUS headroom (VINDPM) on 5 V adapters.
**Recommendation:** Widen VBUS to ≥1.5–2 mm, pour it as an In2 island (In2 already carries +VSYS as a pour), or duplicate it on B.Cu. Until then, cap IINDPM and ICHG in the driver (for example IINDPM ≤ 1.5 A). Needs verification by the power reviewer against the chosen charge current.
> **Reviewer note:** Lengths re-measured and confirmed: In2 0.8 mm 87.9 mm, B.Cu 0.8 mm 20.3 mm plus 0.6 mm 7.6 mm, 8 vias, no VBUS pour. The original IPC-2221 figure ("roughly 1 A for a 10 °C rise") used the external-layer constant. I corrected it to about 0.55 A at 10 °C (internal). This makes the finding stronger, not weaker. Same issue as CON-03 / PWR-04.

#### [MEDIUM] LAY-05 MAYA-W386 antenna: keep-out is correct, but large and metal parts sit inside u-blox's 10 mm zone
**Where:** IC2 on B.Cu at (172.41, 171.37), rotated −90°. The antenna end (rows L/M) faces the left board edge, x = 165.13. Footprint keep-out rule area (all 6 layers: no tracks, vias, pads, pours or footprints) covers x 165.26–168.61, y 166.17–176.57, with notches for the M1/M2/L1 and M8/M9/L9 corner pads.
**Evidence (OK):** The keep-out starts at the K-row pad edge (K row at x = 168.91, minus 0.3 mm → 168.61), matching u-blox Figure 16 (datasheet UBXDOC-465451970-2050 R05, p. 40: dimension 4.70 = K-row pad edge; "RF keep-out area is only required for MAYA-W3x6") and Figure 6 of the System Integration Manual (UBXDOC-465451970-2522 R02, p. 12). Zone fill check: no copper on In1, In2, In3 or In4 at (167.0, 171.4) or (166.0, 170.0). GND extends far more than 10 mm on both sides of the module (board runs y 123–200). K9 (RF_ANT1) to L9 (ANT_EXT_FEED) is bridged by a 1.5 mm, 0.115 mm-wide B.Cu track, as SIM §2.2.7 requires for the internal antenna.
**Issue:** SIM §2.2.7 also says "do not place physically tall or large components closer than 10 mm to the module antenna" and asks for "5 mm clearance between the antenna and the casing". SW4 (Alps SKRTLAE010 shielded side switch, metal can, B side, (166.88, 180.96)) is 1.5 mm from the antenna clearance area on the same edge, with its GND MP/NPTH pads. J9 (FPC) is 7.8 mm away, J6 (microSD, metal shell) 8.2 mm, Y3 5.5 mm. I could not check from the PCB where the MagSafe magnets, LRA, battery and case walls are relative to the antenna. The case is transparent resin (journal, 20 Nov), which is fine for RF.
**Recommendation:** If the mechanics allow, move SW4 at least 5–10 mm further down the edge, or accept some detuning at 2.4 GHz and check RSSI on the prototype. Keep the magnets, battery and LRA away from the left edge near y 160–182, and keep ≥5 mm between the antenna and the case wall.
**DRC items_not_allowed (2):** GND tracks on B.Cu at M2 (165.91, 174.67) and M8 (165.91, 168.07). They are 0.6 mm wide, ending at the pad centre; the round end cap reaches exactly to the keep-out notch boundary (y = 174.37 / 168.37) and stays inside the 0.6 × 0.6 mm pad copper. This is a **false positive** with no copper outside the pad. Start the tracks at the pad edge, or exclude the items.
> **Reviewer note:** Confirmed. SW4 is at (166.88, 180.96), rotated 90°, on B.Cu. Its Fab body spans y 178.71-183.21 and its courtyard starts at y 178.13, while the keep-out ends at y 176.57. The gap is 1.56 mm to the courtyard and 2.1 mm to the body, matching "1.5 mm". CON-16 previously said "about 5 mm"; I have corrected it.

#### [MEDIUM] LAY-06 Four ICs have no LCSC part number
**Where:** U1 SAMA7D65-E/4HB-SL3, IC1 MCP16502TAB-E/S8B, IC2 MAYA-W386-00B, U4 BQ25640VDLR (SCR/main/bom.csv; DigiKey numbers exist for U1 and U4). Touchpad U1 IQS7211E001QNR also has none.
**Issue:** JLC cannot place these without Global Sourcing or a consignment/pre-order, and the order stalls until they arrive. SAMA7D65 is MSL3 (DS60001851E Table 86.1) and must arrive dry-packed.
**Recommendation:** Use JLC "Global Sourcing" (DigiKey/Mouser) or pre-order to your parts library before placing the PCBA order. Fill the LCSC field (or a JLC part number) once the parts are in the library.
> **Reviewer note:** Confirmed in SCR/main/bom.csv: the LCSC field is empty for IC1, IC2, U1 and U4. Also note the trailing space in "BQ25640VDLR " (LAY-12).

#### [LOW] LAY-07 Hole-to-hole spacing and a duplicate via
**Where:** `hole_to_hole`: +3V3 vias (178.33, 157.84) and (178.53, 157.59) are 0.166 mm apart edge to edge. +3V3 vias (184.58, 161.68)/(184.83, 161.97) are 0.229 mm apart, and four +VSYS via pairs around IC1 ((170.61, 143.89)/(170.62, 143.51), etc.) are 0.230 mm apart. `holes_co_located`: two GND vias stacked at (199.12, 167.93).
**Issue:** JLC's minimum via hole-to-hole is 0.2 mm, so the 0.166 mm pair fails. It is the same net, so the only risks are fab rejection or breakout. The 0.229/0.230 mm pairs pass JLC; the board rule (0.25 mm) is stricter. A double drill hit at one coordinate can break 0.15 mm bits and gets flagged by CAM.
**Recommendation:** Delete one of the stacked GND vias and move or merge the 0.166 mm pair. Optionally set the board rule `min_hole_to_hole` to 0.2 mm (the JLC value) so the remaining warnings clear.

#### [LOW] LAY-08 Side switches SW1–SW5: NPTH holes 0.099–0.15 mm from pad copper
**Where:** 20 `hole_clearance` items. Example: SW4 pad 1 (167.78, 182.19) to NPTH (166.88, 183.09) is 0.099 mm; MP pads to NPTH are 0.150 mm. Same pattern on SW1, SW2, SW3 and SW5.
**Issue:** This comes from the KiCad library footprint `Button_Switch_SMD:SW_Push_1P1T-MP_NO_Horizontal_Alps_SKRTLAE010` (0.9 mm NPTH pegs next to the pads, Alps land pattern). JLC asks for 0.2 mm NPTH-to-copper, so CAM may pull the copper back by about 0.1 mm or drill through the pad edge. Every pad involved is GND (pad 1 and MP), so there is no electrical risk.
**Recommendation:** Accept, or treat it as a rule too strict for this footprint: mark these as DRC exclusions with a comment. Optionally trim the pad corners facing the pegs by 0.1 mm.

#### [LOW] LAY-09 The 91 netclass/DRU clearance violations are SI-preference rules, not DFM problems
**Where:** Current report: 44 "DDR clearance to everything" (0.35 mm), 12 "DDR diff pair clearance" (0.7 mm), 20 SDMMC_EXT (0.35 mm), 2 SDMMC_WL, 1 SDMMC_BOOT (new), 7 ASI_BT, 2 ASI_CODEC, 3 USB. A further 6 are barcode items (LAY-13). The pull-up rework moved a few DDR, SDMMC and ASI items around without changing the picture.
**Evidence:** The smallest actual gap among all of them is 0.100 mm (BT.DIN vs UART_SAMBA_RX at (200.77, 174.90); DDR ~RESET via vs CKE at (195.28, 153.49) is 0.129 mm). JLC's minimum is 0.09 mm, so all of them can be manufactured.
**Triage:**
- USB (3): J3 pads A5/B7 and A8/B6 at 0.20 mm, U6 pads 4/5 at 0.25 mm. These are **false positives**: the connector and ESD-array pad pitch sets the gap. Add a DRU exception, e.g. `(condition "A.Type == 'Pad' && B.Type == 'Pad' && A.Parent == B.Parent")`.
- DDR (56): handed to the DDR reviewer. Tightest gaps: BA0 vs ~CS 0.178 mm at (199.01, 149.55), CKE vs ~RESET via 0.129 mm, DQ12/DQ14 0.155 mm, CK± vs A10/A13 0.52–0.56 mm. Real crosstalk is limited because the parallel runs are short and inside the fanout.
- SDMMC_EXT (20): mostly where EXT.DAT1/2/3 and CD squeeze past VOL+, GPI1, ~DET_3.5mm, WL.EN and the BT UART near (202–206, 163–174). EXT.DAT3 vs AUDIOCLK (MCLK to the codec) is 0.157 mm at (208.38, 163.44). That one is worth opening up, because SD edges coupling into MCLK add audio jitter. EXT.CK vs the BT.TX via is 0.146 mm at (203.83, 171.07). Severity LOW: the parallel lengths are short.
- SDMMC_BOOT (1, new): BOOT.CD vs ~WKUP on F.Cu, 0.131 mm at (191.47, 171.51). Both are slow static signals, so accept.
- ASI_BT/ASI_CODEC (9): BGA-escape spacing near (200–202, 173–175) and the TDO via (188.71, 164.94). The "SAMA reduced clearance" rule area evidently does not cover these spots. Rule too strict: extend the SAMA area or accept.
**Recommendation:** Fix the AUDIOCLK/EXT.DAT3 spot if it is easy. Add the USB pad exception. Otherwise document these as accepted.

#### [LOW] LAY-10 lib_footprint_mismatch (IC1, IC3, U5, U3): copper identical, changes are cosmetic library drift
**Where:** IC1 VQFN-32 5×5 EP3.15, IC3 VQFN-24 4×4 EP2.45, U5 TDFN-14 3×3 EP1.78×2.35, U3 SOT-23-5.
**Evidence:** I compared each board footprint to `/usr/share/kicad/footprints/*.pretty`, both pad-by-pad through the pcbnew API and as a normalized s-expression diff. Pad numbers, positions, sizes, shapes, layers, paste and zone-connect all match (U3 pad Y = −0.949999 vs −0.95 is a 1 nm rotation round-off). The differences are: (a) silkscreen pin-1 marker position and segment ordering (KiCad 10 library update; IC1's marker moved from (−3.14, −1.75) to the corner (−2.61, −2.61)), and (b) 3D-model filenames (board IC1 uses `QFN-32-1EP_5x5mm_P0.500mm_EP3.300x3.300mm.step`, library uses `VQFN-32-…EP3.150…`; board U5 uses `DFN-14-…`, library `TDFN-14-…`). IC3's difference comes only from 45° rotation and pad ordering.
**Recommendation:** Not intentional modifications, just library drift from an older KiCad library. Safe to ignore, or run "Update footprint from library" (copper will not change; this also fixes the 3D models for the case-fit check). The `lib_footprint_issues` items for MT41K256M16TW, ECMF02-2AMX6 and 5034800540 mean those custom libraries are missing from fp-lib-table. That has no fabrication impact because footprints are stored in the board, but "update from library" will fail for them.

#### [LOW] LAY-11 Fab notes on User.Comments: now updated, one DDR value is still stale
**Where:** Cmts.User text at (221.47, 178.07) and the stackup PCB_TABLE.
**Evidence:** Commit e61034b updated both. The impedance note now reads 50 Ω 0.1072 mm, 90 Ω 0.0892/0.105 mm, 100 Ω 0.0892/0.185 mm, which matches the tuning profiles. The stackup table now lists the 0.0764/0.13/0.2328 mm dielectrics and 0.0152 mm inner copper, which matches the board stackup. Still stale: "DQ1 40.7 – 41.7mm", while `meko.kicad_dru` "DDR lane1" uses min 41.45 / opt 41.95 / max 42.45 mm.
**Recommendation:** Correct the DQ1 line. In the JLC order, select impedance control with stackup JLC06081H-1080 and list the target widths in the remark.

#### [LOW] LAY-12 BOM hygiene: stale fields, trailing spaces, extended-part fees
**Where:** SCR/main/bom.csv, `hardware/pcb/meko.csv` (git-ignored, 16 Nov), IC2 footprint fields.
**Issues:**
- PCB IC2 still has a field `Manufacturer_Part_Number = MAYA-W383-00B` and `descr "MAYA-W383-00B-1"` (from the SamacSys footprint), alongside the corrected `MPN = MAYA-W386-00B`. A BOM plugin that reads `Manufacturer_Part_Number` would order the W383, which has no internal antenna. The board relies on the W3x6 internal antenna.
- `meko.csv` (16 Nov) still lists IC2 as `MAYA-W383-00B` / `672-MAYA-W383-00BCT-ND`, but the schematic was fixed to W386 in commit 6f73ad5. Do not order from it.
- Trailing spaces in MPNs: `"SKRTLAE010 "` (SW1–5) and `"BQ25640VDLR "` (U4). These can break JLC's automatic BOM matching.
- Per the jlcsearch/tscircuit mirror of JLC's library (checked 2026-11; JLC's BOM tool has the final say), only C15525 (10 µF 0402, now also used for the new C123) is a Basic part. The other ~41 unique LCSC parts are Extended at about $3 setup each, roughly $120 per order. Commodity 0402/0201 R and C values (10k, 47k, 100k, 1k, 100R, 1 µF, 4.7 µF, 100 nF) have Basic equivalents.
**Recommendation:** Delete or overwrite the stale `Manufacturer_Part_Number` field (Edit → Update PCB from schematic does not remove extra fields; edit the footprint fields). Trim the MPN whitespace. Optionally swap commodity passives to Basic parts.

#### [LOW] LAY-13 Silkscreen: thin strokes, missing font, QR over vias
**Where/Issue:**
- All board texts are 1.0 mm high with a 0.10 mm stroke ("DON'T SELL ME PLS" uses 0.2 mm). JLC's minimum silk line is 0.15 mm, so 0.10 mm strokes may print broken. Most footprint silk is 0.12 mm (KiCad default, usually OK at JLC).
- `text_thickness`: '( •3• )' on B.Silk at (190.26, 198.26) uses the TrueType font "Serto Kharput". That font is not installed on this machine (KiCad substituted Noto Sans), and the board has `embedded_fonts no`, so the output depends on the plotting machine.
- QR barcode on F.Silk at (211.05, 143.49) sits on top of 2 vias (GND, ~DET_3.5mm) at 0.0 mm, 0.20 mm from TP62's silk, and 0.39 mm from the board edge (6 `barcode clearance` items). Silk over via bumps and mask openings gets clipped, which may make the code unreadable.
- `silk_over_copper` (25: J6/J7 microSD outlines over pads, IC3/U4 pin-1 polygons) and `silk_edge_clearance` (9: J2/J3/J4/J5 outlines crossing the edge or slot) are clipped by the fab. Cosmetic.
- `silk_overlap` (2): U4 circle vs C88; 'show me something' vs J8. Cosmetic.
- Only 2 of 275 reference designators are visible on silk. Fine for JLC, harder for rework and debug.
**Recommendation:** Raise text strokes to ≥0.15 mm. Convert the TrueType text to a stroke font or enable embedded fonts. Move the QR to a via-free area at least 1 mm from the edge.

#### [LOW] LAY-14 Board-setup rule values looser or stricter than JLC
**Where:** `meko.kicad_pro` design rules.
**Issue:** `min_clearance` 0.0762 and `min_track_width` 0.0762 are below JLC's 0.09 mm, so DRC would not catch a 3 mil track or gap if a netclass were changed. The real minimums used are 0.0892 mm tracks (diff pairs, 374 segments) and 0.100 mm gaps. `min_hole_to_hole` 0.25 is stricter than JLC (0.2). The stackup dielectric layers carry εr 4.45/4.6/4.74 rather than JLC's published values (see DDR-06), so KiCad's built-in calculator would not reproduce JLC's widths. The tuning profiles hold the JLC-calculator values.
**Recommendation:** Set min track and clearance to 0.09, hole-to-hole to 0.2, and change εr to JLC's values (1080: 3.91, core: 4.17, 2116: 4.16) to the stackup.

#### [INFO] LAY-15 Courtyard overlaps involve only test pads
**Where:** TP26 (168.48, 125.71) and TP67 (170.46, 133.10) vs BT1 (bottom). TP46 (196.09, 175.05) vs C9, C25, C57 (top).
**Issue:** The test points are bare 1 mm pads with no component and no paste, so there is no assembly conflict. A probe may not reach TP26/TP67 under the JST GH body.
**Recommendation:** Accept, or nudge them for probe access.

#### [INFO] LAY-16 BGA land and solder mask
**Where:** U1 343 pads, 0.30 mm copper, mask margin 0 (board `pad_to_mask_clearance 0`). U2 96 pads, 0.42 mm.
**Evidence:** Microchip DS60001851E Table 86.4 / drawing C04-23516 recommends a 0.40 mm land with a 0.30 mm solder-mask opening (SMD). The board has 0.30 mm copper and a 0.30 mm opening, so the wettable diameter matches. The copper was shrunk to fit one 0.1 mm track between pads (0.35 mm gap, 0.125 mm per side). With mask registration of about ±0.05 mm, some pads will be partly mask-defined on one side. That is acceptable for SAC105 0.35 mm balls.
**Recommendation (needs verification):** Confirm in JLC's DFM viewer that CAM does not add mask expansion on U1. If it did, the 0.35 mm pad-to-pad mask web would shrink; it would still stay above the 0.10 mm dam minimum.

#### [INFO] LAY-17 Via-in-pad on QFN thermal pads: order with epoxy fill and cap
**Where:** 33 vias in the QFN/DFN exposed pads (IC1 13 × 0.225 drill, IC3 10, U5 8, U4 2 × 0.15 drill), plus vias in TP14/15/16, JP1/JP2 and others.
**Issue:** Board setup says `filling no / capping no` and tenting yes, but tenting does not cover vias inside a pad opening. Unfilled 0.15–0.225 mm vias in an EP wick solder and leave voids. JLC's 6-layer default is via-in-pad epoxy fill plus cap, free per the capability page.
**Recommendation:** Keep the JLC 6-layer default "Epoxy filled & capped". Do not choose plain tenting.

#### [INFO] LAY-18 Assembly plan notes
- Both BGAs (U1, U2), the MAYA LGA (IC2), all connectors, switches, the 3.5 mm and 2.5 mm jacks, crystals Y2/Y3, U6 and U7 are on the **bottom** (64 parts). The **top** carries 211 parts: IC1, IC3, U3, U4, U5, L1–5 and passives (97 × 0201). Ask JLC to reflow the light top side first and the BGA/connector side last.
- THT and mixed parts: J3 USB-C has 4 plated-slot shell legs (0.6 × 1.2/1.7 mm, annular 0.2 mm, OK), so expect a THT/manual soldering line item. J1 (1×2 2.54 mm, top) and J2 (2×5 1.27 mm SWD, bottom) are `exclude_from_bom` and are hand-fitted later. J2's PTH annular ring is 0.175 mm (≥0.15 mm OK).
- DNP/excluded parts: C2, C121 and D2–D4 (ESD441) are `dnp` + `exclude_from_board`, so they do not appear in pos.csv. All TPs, JP1–3, H1–H4 and SYM1 are `exclude_from_bom`. No test pad has paste.
- Mounting holes H1 (212.88, 126.92), H2 (179.98, 129.35), H3 (167.73, 197.95), H4 (203.38, 182.18): NPTH Ø1.4 for M1.2 screws. The nearest outer-layer copper is 1.33 mm from the hole centre (H4: EXT.CK on B.Cu), so an M1.2 pan head (Ø ≈ 2.1–2.3 mm) does not reach copper. OK. H4 is mid-board next to J7 and the EXT SD lines, which is fine with mask.
- No fiducials or tooling holes on the board. See LAY-03.
- Tall parts vs case: not verified, because 3D models are not installed on this machine. The owner's Fusion case was modelled against the PCB.

#### [INFO] LAY-19 Touchpad board (SCR/touch/drc.rpt): no real errors
- 12 `clearance (barcode)`: QR on B.Silk at (181.97, 127.11) over COL6/COL7 vias. Cosmetic; the code may be hard to read.
- 13 `footprint_symbol_mismatch` (COL1–7, ROW1–6): the footprint library nickname differs after the Eagle import ("PAD_0_5MM doesn't match … Touchpad:PAD_0_5MM"). Benign.
- `extra_footprint` SYM1 (OSHW logo only on the PCB) and `lib_footprint_mismatch` U1 QFN-20: same kind of library drift as LAY-10. `silk_over_copper` U1 vs C2: cosmetic.
- Fab: 2L 1.6 mm, 41.39 × 30.43 mm, 90 vias 0.6/0.3, tracks 0.15 mm. Easy for JLC. Every part is on B.Cu (U1, C1–3, J1), so it can go through Economic PCBA (single-sided, no rails or fiducials needed; QFN 0.4 mm pitch equals the Economic minimum lead pitch of 0.40 mm). U1 IQS7211E has no LCSC number (LAY-06).
- Needs verification by the touch/IQS reviewer: B.Cu has a **solid** GND pour behind the F.Cu electrode zones on 1.6 mm FR4. Azoteq trackpad guidance usually calls for hatched or no ground behind electrodes to limit parasitic capacitance.

### Design rationale

- **Stackup (SIG/GND/PWR/GND/GND/SIG, 0.8 mm).** It is JLC's 1080 6-layer build: 35 µm outer, 1080 prepreg 0.0764 mm, 0.13 mm cores, 2 × 2116 (0.2328 mm) in the middle, 0.5 oz inner, 0.7764 mm copper+dielectric. It is identical to `SCR/datasheets/jlc_stackups/1080.json`. The thin 1080 outer prepreg is why the board is 0.8 mm (journal, 20 Sep): on 1.6 mm, 50 Ω traces would be about 0.2 mm, too wide for a 0.65 mm-pitch fanout. The tuning profiles (50 Ω: 0.1072 mm; 90 Ω: 0.0892/0.105; 100 Ω: 0.0892/0.185) check out. For example, IPC microstrip with h = 0.0764, w = 0.1072, t = 0.035, εr = 3.91 gives about 50 Ω.
- **Plane strategy.** Every signal layer (F.Cu, B.Cu) sits directly against a solid GND plane (In1, In4). In2 power is sandwiched between In1 and In3 GND, 0.13 mm from In1, which gives useful interplane capacitance. In2 can therefore be split into islands (+3V3 main, +1V15_CORE, +1V15_CPU, +1V35_DDR, +2V5, +VSYS) with no SI penalty: no signal references In2, and In1/In3/In4 carry no tracks at all. The three GND planes are identical apart from through-via antipads (`SCR/layout/img/In1.Cu.png`).
- **Return paths and stitching.** 620 GND vias (about 16 per 100 mm²). Every U1 and U2 GND ball has a GND via within 0.46/0.42 mm (median). Signal layer-change vias have a GND via within a median of 0.45–0.83 mm for DDR, SDMMC_WL, UART and ASI. SDMMC_EXT is the loosest at about 2.1 mm median, which is acceptable at SD speeds.
- **BGA fanout.** U1 (0.65 mm pitch, placed at −45°) uses dog-bone 0.3/0.15 through vias between ball quads. The diagonal pad-to-via distance is 0.46 mm, leaving 0.16 mm of copper clearance, and 0.35 mm between pads fits one 0.1 mm track. A 0.4/0.2 via would leave no room for a track between vias, so 0.3/0.15 is the right size. JLC lists 0.15/0.25 mm as its multilayer via minimum (cost-adder for 0.15 mm holes), and the board's 0.15 mm annular ring meets "via ≥ hole + 0.1 mm (0.15 preferred)". The journal (20 Nov) notes that free via-in-pad at JLC 6-layer could have allowed larger vias, but the current fanout needs no via-in-pad on the BGAs.
- **Rule areas.** DDR, SAMA and WIRELESS rule areas, used only by `meko.kicad_dru`, relax clearance to 0.1 mm inside the BGA and module fanouts. Outside them the 0.35/0.7 mm "3W"-style DDR and SDMMC spacing applies. That is why most clearance hits sit at area edges.
- **Antenna.** W386 uses the module's internal Niche/Abracon antenna through the K9→L9 bridge. The module sits on the left edge with the antenna end outward and the u-blox keep-out embedded in the footprint on all layers (SIM §2.2.7, Figure 6).
- **Power copper.** PMIC (IC1) switch nodes, inputs and outputs are short F.Cu pours. +VSYS is an In2 island. +BATT goes BT1 → 0.8 mm B.Cu → 2 × 0.6/0.3 vias → F.Cu pour → U4.14. BT− returns through 4 vias to the R29 sense resistor.

### Verified OK

- No blind, buried or micro vias. All 1071 vias are through vias (type THROUGH): 975 × 0.3/0.15, 41 × 0.45/0.225, 55 × 0.6/0.3. Aspect ratio 0.8/0.15 ≈ 5.3:1.
- Minimum track 0.0892 mm, minimum copper gap 0.100 mm (lowest actual value among all clearance violations); both meet JLC 0.09/0.09.
- Copper-to-edge: rule 0.25 mm with no violations (JLC routed edge ≥0.2 mm).
- Edge.Cuts is closed: 50.24 × 77.16 mm, R1 mm corners, a 1 mm notch on the left edge at y 138.8–147.2, and an internal 8 × 2.5 mm slot at (170.79–178.79, 161.97–164.47). Inside corners of the slot will get the router radius (≈0.5 mm).
- Stackup matches JLC 1080 6L 0.8 mm. ENIG ("Immersion gold") is set; it is needed for flat BGA pads.
- Inner via-hole-to-copper rule of 0.2 mm matches JLC's inner-layer value.
- U4 (BQ25640 WQFN) footprint: the thermal pad has no paste layer on the pad itself, but has an explicit F.Paste polygon (0.35 × 1.4 mm) plus corner-pad paste polygons, matching TI's VDL0023A-MFG pattern.
- MAYA keep-out is clear on all copper layers after refill. The module edge is 0.13 mm inside the board edge, and the M-row pads are 0.48 mm from the edge.
- No signal tracks on In1, In3 or In4. In2 carries only power tracks and pours.
- GND plane fill is present under U1 and U2 on In1, In3 and In4 (spot check). In2 under U1 is +2V5 and under U2 is +1V35_DDR.
- The duplicated "VSYS_x" zone names on In2 are cosmetic only; nets are correct.
- Mounting-hole clearance to outer copper is ≥1.33 mm from centre.
- Battery and charger high-current path uses 0.8 mm tracks and multiple vias. BT− runs through 4 × 0.15 vias to R29.

### Datasheets used

- JLCPCB PCB capabilities: https://jlcpcb.com/capabilities/pcb-capabilities (multilayer 0.09/0.09 mm, via 0.15/0.25 mm, hole-to-hole 0.2 mm, via-in-pad default on 6L+, BGA pad ≥0.2 mm, NPTH-to-copper 0.2 mm, silk ≥0.15 mm line / 1.0 mm text, mask dam 0.10 mm)
- JLCPCB PCBA capabilities: https://jlcpcb.com/capabilities/pcb-assembly-capabilities (Standard PCBA: min 70 × 70 mm, edge rails and fiducials "Necessary", Economic single-sided only)
- JLC 6L 0.8 mm stackups (fetched by another agent): SCR/datasheets/jlc_stackups/1080.json, 1080*.kicad_pcb
- u-blox MAYA-W3 data sheet UBXDOC-465451970-2050 R05: SCR/datasheets/MAYA-W3/maya_ds.pdf (Figure 16 p. 40, keep-out)
- u-blox MAYA-W3 System Integration Manual UBXDOC-465451970-2522 R02: https://content.u-blox.com/sites/default/files/documents/MAYA-W3_SIM_UBXDOC-465451970-2522.pdf → SCR/datasheets/MAYA-W3/sim.pdf (§2.2.7 internal antenna rules, Figure 6 p. 12)
- Microchip SAMA7D6 data sheet DS60001851E: SCR/datasheets/SAMA7D65/ds.pdf (Table 86.4 land/mask, drawing C04-23516)
- TI BQ25640: SCR/datasheets/bq25640/bq25640.pdf (§7.3.3.1 IINDPM default 3.2 A, REG0x02 ICHG POR 2000 mA)
- Alps SKRTLAE010 (C110293): SCR/datasheets/SKRTLAE010/C110293.real.pdf (land pattern)
- LCSC basic/extended status: jlcsearch mirror https://jlcsearch.tscircuit.com/api/search?q=<LCSC> (third-party; cached in SCR/layout/lcsc/*.json)
