# Apple Wi-Fi Recommendations Checklist

This checklist is based on [Apple's Wi-Fi recommendations](https://support.apple.com/en-us/102766) for optimal performance with Apple devices.

## Network Configuration

### Basic Settings
- [ ] Use WPA3 Personal or WPA2/WPA3 Transitional security
- [ ] Avoid WEP or WPA security
- [ ] Use unique passwords for each wireless network
- [ ] Enable PMF (Protected Management Frames)

### Network Names (SSID)
- [ ] Use unique network names for each band (2.4 GHz and 5 GHz)
- [ ] Avoid special characters in network names
- [ ] Keep network names under 32 characters

### Channel Configuration
- [ ] Use auto channel selection or manually select non-overlapping channels
- [ ] For 2.4 GHz:
  - [ ] Use channels 1, 6, or 11 only
  - [ ] Avoid channels 2-5, 7-10, 12-14
- [ ] For 5 GHz:
  - [ ] Use non-DFS channels when possible
  - [ ] Configure channel width appropriately (20/40/80 MHz)

### Band Configuration
- [ ] Enable band steering for dual-band networks
- [ ] Configure proper minimum RSSI thresholds
- [ ] Enable 802.11k for better roaming
- [ ] Enable 802.11v for better roaming
- [ ] Enable 802.11r (Fast BSS Transition) for better roaming

## Advanced Settings

### DHCP and IP Configuration
- [ ] Use DHCP for IP address assignment
- [ ] Configure appropriate DHCP lease times
- [ ] Set up proper DNS servers
- [ ] Avoid IP address conflicts

### Quality of Service (QoS)
- [ ] Enable WMM (Wi-Fi Multimedia)
- [ ] Configure proper QoS settings for:
  - [ ] Voice traffic
  - [ ] Video traffic
  - [ ] Background traffic

### Security Features
- [ ] Enable firewall protection
- [ ] Configure proper guest network isolation
- [ ] Enable MAC address filtering (if needed)
- [ ] Configure RADIUS server (if using WPA2/WPA3 Enterprise)

## Network Optimization

### Coverage and Capacity
- [ ] Proper AP placement for optimal coverage
- [ ] Configure appropriate transmit power levels
- [ ] Balance client load across APs
- [ ] Monitor and adjust client density per AP

### Performance Monitoring
- [ ] Monitor network utilization
- [ ] Track client connection quality
- [ ] Identify interference sources
- [ ] Regular performance testing

### Maintenance
- [ ] Regular firmware updates
- [ ] Configuration backups
- [ ] Performance optimization reviews
- [ ] Network health monitoring

## Implementation Status

Each item in this checklist will be marked as:
- [ ] Not Started
- [~] In Progress
- [x] Completed
- [!] Not Applicable

## Notes

- This checklist will be updated as we implement checks in the tool
- Some items may require manual verification
- Additional items may be added based on specific UniFi capabilities
