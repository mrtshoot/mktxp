# coding=utf8
## Copyright (c) 2020 Arseniy Kuznetsov
##
## This program is free software; you can redistribute it and/or
## modify it under the terms of the GNU General Public License
## as published by the Free Software Foundation; either version 2
## of the License, or (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.


from mktxp.datasource.base_ds import BaseDSProcessor
from mktxp.datasource.package_ds import PackageMetricsDataSource


class WirelessMetricsDataSource:
    ''' Wireless Metrics data provider
    '''             
    WIFIWAVE2 = 'wifiwave2'
    WIRELESS = 'wireless'
    WIFI = 'wifi'

    WIFI_PACKAGE = 'wifi-qcom'
    WIFI_AC_PACKAGE = 'wifi-qcom-ac'

    @staticmethod
    def metric_records(router_entry, *, metric_labels = None, add_router_id = True):
        if metric_labels is None:
            metric_labels = []                
        try:
            wireless_package = WirelessMetricsDataSource.wireless_package(router_entry)
            registration_table_records = router_entry.api_connection.router_api().get_resource(f'/interface/{wireless_package}/registration-table').get()

            # With wifiwave2, Mikrotik renamed the field 'signal-strength' to 'signal' 
            # For backward compatibility, including both variants
            for record in registration_table_records:
                if 'signal' in record:
                    record['signal-strength'] = record['signal']

            return BaseDSProcessor.trimmed_records(router_entry, router_records = registration_table_records, metric_labels = metric_labels, add_router_id = add_router_id,)
        except Exception as exc:
            print(f'Error getting wireless registration table info from router{router_entry.router_name}@{router_entry.config_entry.hostname}: {exc}')
            return None


    @staticmethod
    def wireless_package(router_entry):
        if not router_entry.wifi_package:
            if PackageMetricsDataSource.is_package_installed(router_entry, package_name = WirelessMetricsDataSource.WIFI_PACKAGE):
              router_entry.wifi_package = WirelessMetricsDataSource.WIFI
            elif PackageMetricsDataSource.is_package_installed(router_entry, package_name = WirelessMetricsDataSource.WIFI_AC_PACKAGE):
              router_entry.wifi_package = WirelessMetricsDataSource.WIFI
            elif PackageMetricsDataSource.is_package_installed(router_entry, package_name = WirelessMetricsDataSource.WIFIWAVE2):
              router_entry.wifi_package = WirelessMetricsDataSource.WIFIWAVE2
            else:
              router_entry.wifi_package = WirelessMetricsDataSource.WIRELESS
        return router_entry.wifi_package

    @staticmethod
    def is_legacy(router_entry):
        return WirelessMetricsDataSource.wireless_package(router_entry) == WirelessMetricsDataSource.WIRELESS
