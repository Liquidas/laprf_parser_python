# laprf_parser_python
TCP packet parser for ImmersionRC 8-way laprf unit.
According to: LapRF Communications Protocol (109.5 KB) https://www.immersionrc.com/?download=6030

Currently functional packet parsing:
*Status (input voltage, rssi, gate state, detection count, status flags)
*RF settings (enable, channel, band, threshold, gain, frequency)

TODO:
*RF settings modification query
*Detections packets
*Settings packets
*Descriptor packets
